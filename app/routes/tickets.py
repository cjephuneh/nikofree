from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.event import Event
from app.models.ticket import TicketType, Booking, Ticket, PromoCode
from app.models.payment import Payment
from app.utils.decorators import user_required, partner_required
from app.utils.qrcode_generator import generate_qr_code
from app.utils.email import send_booking_confirmation_email, send_booking_cancellation_email, send_booking_cancellation_to_partner_email
from app.utils.ticket_pdf import generate_ticket_pdf
from app.utils.sms import (
    send_booking_confirmation_sms,
    send_booking_cancellation_sms,
    send_booking_cancellation_to_partner_sms
)
from app.routes.notifications import notify_new_booking, create_notification

bp = Blueprint('tickets', __name__)


@bp.route('/validate-promo', methods=['POST'])
@user_required
def validate_promo_code(current_user):
    """Validate promo code"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        code = data.get('code')
        event_id = data.get('event_id')
        
        if not code or not event_id:
            return jsonify({'error': 'code and event_id are required'}), 400
        
        # Convert event_id to int if it's a string
        try:
            event_id = int(event_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid event_id format'}), 400
        
        # Normalize code to uppercase
        code = code.upper().strip()
        
        # Find promo code (case-insensitive search for safety)
        from sqlalchemy import func
        promo = PromoCode.query.filter(
            func.upper(PromoCode.code) == code,
            PromoCode.event_id == event_id,
            PromoCode.is_active == True
        ).first()
        
        if not promo:
            # Check if code exists but for different event (case-insensitive)
            promo_exists = PromoCode.query.filter(
                func.upper(PromoCode.code) == code,
                PromoCode.is_active == True
            ).first()
            if promo_exists:
                return jsonify({'error': 'Promo code exists but is not valid for this event'}), 404
            return jsonify({'error': 'Invalid promo code'}), 404
        
        # Check validity period
        now = datetime.utcnow()
        if promo.valid_from and now < promo.valid_from:
            return jsonify({'error': 'Promo code not yet valid'}), 400
        
        if promo.valid_until and now > promo.valid_until:
            return jsonify({'error': 'Promo code expired'}), 400
        
        # Check usage limits
        if promo.max_uses is not None and promo.current_uses >= promo.max_uses:
            return jsonify({'error': 'Promo code usage limit reached'}), 400
        
        # Check per-user usage
        user_usage = Booking.query.filter_by(
            user_id=current_user.id,
            promo_code_id=promo.id
        ).count()
        
        if user_usage >= promo.max_uses_per_user:
            return jsonify({'error': 'You have already used this promo code'}), 400
        
        return jsonify({
            'valid': True,
            'promo_code': promo.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Error validating promo code: {str(e)}')
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@bp.route('/book', methods=['POST'])
@user_required
def book_event(current_user):
    """Book tickets for an event"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('event_id'):
        return jsonify({'error': 'event_id is required'}), 400
    
    quantity = data.get('quantity', 1)
    
    if quantity < 1:
        return jsonify({'error': 'Quantity must be at least 1'}), 400
    
    # Get event
    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if event.status != 'approved' or not event.is_published:
        return jsonify({'error': 'Event is not available for booking'}), 400
    
    # Check if event is in the past
    if event.start_date < datetime.utcnow():
        return jsonify({'error': 'Cannot book past events'}), 400
    
    # Check if user has already booked this event (prevent duplicate bookings)
    existing_booking = Booking.query.filter_by(
        user_id=current_user.id,
        event_id=event.id
    ).filter(
        Booking.status != 'cancelled'
    ).first()
    
    if existing_booking:
        if existing_booking.status == 'confirmed':
            return jsonify({
                'error': 'You have already booked tickets for this event',
                'booking_id': existing_booking.id,
                'booking_number': existing_booking.booking_number
            }), 409  # 409 Conflict
        elif existing_booking.status == 'pending':
            return jsonify({
                'error': 'You have a pending booking for this event. Please complete the payment or cancel the existing booking.',
                'booking_id': existing_booking.id,
                'booking_number': existing_booking.booking_number
            }), 409  # 409 Conflict
    
    # Get ticket type - for free events, create default if none exists
    ticket_type = None
    if data.get('ticket_type_id'):
        ticket_type = TicketType.query.filter_by(
            id=data['ticket_type_id'],
            event_id=event.id,
            is_active=True
        ).first()
    
    # For free events without ticket types, create a default one
    if event.is_free and not ticket_type:
        # Check if a default free ticket type exists
        ticket_type = TicketType.query.filter_by(
            event_id=event.id,
            name='Free Admission',
            is_active=True
        ).first()
        
        if not ticket_type:
            # Create default free ticket type
            ticket_type = TicketType(
                event_id=event.id,
                name='Free Admission',
                price=0.00,
                quantity_total=None,  # None = unlimited
                quantity_available=None,  # None = unlimited
                quantity_sold=0,
                min_per_order=1,
                max_per_order=10,
                is_active=True
            )
            db.session.add(ticket_type)
            db.session.flush()
    
    # For paid events, ticket type is required
    if not event.is_free and not ticket_type:
        return jsonify({'error': 'Ticket type is required for paid events'}), 400
    
    if not ticket_type:
        return jsonify({'error': 'Ticket type not found'}), 404
    
    # Check quantity limits
    if quantity < ticket_type.min_per_order:
        return jsonify({'error': f'Minimum {ticket_type.min_per_order} tickets required'}), 400
    
    if quantity > ticket_type.max_per_order:
        return jsonify({'error': f'Maximum {ticket_type.max_per_order} tickets allowed'}), 400
    
    # Check availability (accounting for reserved but not expired tickets)
    if ticket_type.quantity_available is not None:
        # Count tickets reserved by pending bookings that haven't expired
        reserved_count = db.session.query(func.sum(Booking.quantity)).filter(
            Booking.event_id == event.id,
            Booking.status == 'pending',
            Booking.payment_status == 'unpaid',
            Booking.reserved_until.isnot(None),
            Booking.reserved_until >= datetime.utcnow()
        ).scalar() or 0
        
        # Available tickets = total available - reserved (non-expired) tickets
        actually_available = ticket_type.quantity_available - reserved_count
        
        if quantity > actually_available:
            return jsonify({'error': 'Not enough tickets available'}), 400
    
    # Check sales period
    now = datetime.utcnow()
    if ticket_type.sales_start and now < ticket_type.sales_start:
        return jsonify({'error': 'Ticket sales have not started yet'}), 400
    
    if ticket_type.sales_end and now > ticket_type.sales_end:
        return jsonify({'error': 'Ticket sales have ended'}), 400
    
    # Calculate amount
    ticket_price = float(ticket_type.price)
    total_amount = ticket_price * quantity
    discount_amount = 0
    
    # Apply promo code if provided
    promo_code = None
    if data.get('promo_code'):
        promo = PromoCode.query.filter_by(
            code=data['promo_code'].upper(),
            event_id=event.id,
            is_active=True
        ).first()
        
        if promo:
            # Calculate discount
            if promo.discount_type == 'percentage':
                discount_amount = total_amount * (float(promo.discount_value) / 100)
            else:  # fixed
                discount_amount = float(promo.discount_value)
            
            # Ensure discount doesn't exceed total
            discount_amount = min(discount_amount, total_amount)
            promo_code = promo
    
    final_amount = total_amount - discount_amount
    
    # Calculate platform fee (7%)
    commission_rate = current_app.config.get('PLATFORM_COMMISSION_RATE', 0.07)
    platform_fee = final_amount * commission_rate
    partner_amount = final_amount - platform_fee
    
    # Update user phone number if provided (even if user already has one, allow update)
    if data.get('phone_number'):
        from app.utils.validators import validate_phone
        phone = data.get('phone_number')
        if validate_phone(phone):
            # Check if phone is already taken by another user
            from app.models.user import User
            existing = User.query.filter(
                User.phone_number == phone,
                User.id != current_user.id
            ).first()
            if not existing:
                current_user.phone_number = phone
                print(f"📱 [TICKETS] Updated user {current_user.id} phone number to {phone}")
                # Commit phone number update immediately so it's available for SMS
                db.session.commit()
    
    # Create booking with 5-minute reservation timer for paid events
    reserved_until = None
    if not event.is_free:
        reserved_until = datetime.utcnow() + timedelta(minutes=5)
    
    booking = Booking(
        user_id=current_user.id,
        event_id=event.id,
        quantity=quantity,
        total_amount=final_amount,
        platform_fee=platform_fee,
        partner_amount=partner_amount,
        discount_amount=discount_amount,
        promo_code_id=promo_code.id if promo_code else None,
        status='pending',
        payment_status='unpaid' if not event.is_free else 'paid',
        reserved_until=reserved_until
    )
    
    db.session.add(booking)
    db.session.flush()  # Get booking ID
    
    # For free events, auto-confirm
    if event.is_free:
        booking.status = 'confirmed'
        booking.confirmed_at = datetime.utcnow()
        
        # Create tickets
        tickets = []
        for i in range(quantity):
            ticket = Ticket(
                booking_id=booking.id,
                ticket_type_id=ticket_type.id
            )
            db.session.add(ticket)
            db.session.flush()
            
            # Generate QR code
            qr_data = ticket.ticket_number
            qr_path = generate_qr_code(qr_data, ticket.ticket_number)
            ticket.qr_code = qr_path
            
            tickets.append(ticket)
        
        # Update ticket availability
        if ticket_type.quantity_available is not None:
            ticket_type.quantity_available -= quantity
            ticket_type.quantity_sold += quantity
        
        # Update event stats
        event.attendee_count += quantity
        event.total_tickets_sold += quantity
        
        # Update promo code usage
        if promo_code:
            promo_code.current_uses += 1
        
        db.session.commit()
        
        # Send confirmation email
        send_booking_confirmation_email(booking, tickets)
        
        # Send confirmation SMS
        # Use phone number from request if provided, or from user profile
        phone_for_sms = data.get('phone_number') or current_user.phone_number
        print(f"📱 [TICKETS] About to send booking confirmation SMS for booking {booking.id}")
        print(f"📱 [TICKETS] Phone number for SMS: {phone_for_sms}")
        send_booking_confirmation_sms(booking, tickets, phone_number_override=phone_for_sms)
        print(f"📱 [TICKETS] Booking confirmation SMS call completed for booking {booking.id}")
        
        # Notify user of successful booking
        create_notification(
            user_id=current_user.id,
            title='Booking Confirmed! 🎉',
            message=f'Your booking for "{event.title}" has been confirmed. {quantity} ticket(s) reserved.',
            notification_type='booking',
            event_id=event.id,
            booking_id=booking.id,
            action_url=f'/bookings/{booking.id}',
            action_text='View Booking',
            send_email=False  # Email already sent above
        )
        
        # Notify partner of new booking
        notify_new_booking(event, booking)
        
        return jsonify({
            'message': 'Booking confirmed!',
            'booking': booking.to_dict(),
            'requires_payment': False
        }), 201
    
    # For paid events, require payment
    db.session.commit()
    
    return jsonify({
        'message': 'Booking created. Please proceed to payment.',
        'booking': booking.to_dict(),
        'requires_payment': True,
        'amount': float(final_amount)
    }), 201


# Cancel booking route - support both /cancel/<id> and /bookings/<id>/cancel
@bp.route('/cancel/<int:booking_id>', methods=['POST'])
@bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@user_required
def cancel_booking(current_user, booking_id):
    """Cancel booking"""
    try:
        current_app.logger.info(f'Cancel booking request: booking_id={booking_id}, user_id={current_user.id if current_user else None}')
        
        if not current_user:
            return jsonify({'msg': 'User authentication required'}), 401
        
        if not booking_id:
            return jsonify({'msg': 'Booking ID is required'}), 400
        
        booking = Booking.query.filter_by(
            id=booking_id,
            user_id=current_user.id
        ).first()
        
        if not booking:
            return jsonify({'msg': 'Booking not found'}), 404
        
        if booking.status == 'cancelled':
            return jsonify({'msg': 'Booking already cancelled'}), 400
        
        # Check if event exists and has started
        if not booking.event:
            return jsonify({'msg': 'Event not found for this booking'}), 404
        
        if booking.event.start_date < datetime.utcnow():
            return jsonify({'msg': 'Cannot cancel booking for past events'}), 400
        
        # Store original status before cancelling
        was_confirmed = booking.status == 'confirmed'
        
        # Cancel booking
        booking.status = 'cancelled'
        booking.cancelled_at = datetime.utcnow()
        
        # Restore ticket availability if booking was confirmed
        if was_confirmed:
            for ticket in booking.tickets:
                ticket.is_valid = False
            
            ticket_type = booking.tickets.first().ticket_type if booking.tickets.first() else None
            if ticket_type and ticket_type.quantity_available is not None:
                ticket_type.quantity_available += booking.quantity
                ticket_type.quantity_sold -= booking.quantity
            
            # Update event stats
            if booking.event:
                booking.event.attendee_count -= booking.quantity
                booking.event.total_tickets_sold -= booking.quantity
        
        # TODO: Process refund if paid
        
        db.session.commit()
        
        # Send cancellation SMS and email to user
        try:
            send_booking_cancellation_sms(current_user, booking, booking.event)
        except Exception as sms_error:
            current_app.logger.warning(f'Failed to send cancellation SMS: {str(sms_error)}')
        
        try:
            send_booking_cancellation_email(current_user, booking, booking.event)
        except Exception as email_error:
            current_app.logger.warning(f'Failed to send cancellation email: {str(email_error)}')
        
        # Send cancellation SMS and email to partner
        try:
            partner = booking.event.organizer if booking.event else None
            if partner:
                send_booking_cancellation_to_partner_sms(partner, booking, booking.event)
        except Exception as sms_error:
            current_app.logger.warning(f'Failed to send partner cancellation SMS: {str(sms_error)}')
        
        try:
            partner = booking.event.organizer if booking.event else None
            if partner:
                send_booking_cancellation_to_partner_email(partner, booking, booking.event)
        except Exception as email_error:
            current_app.logger.warning(f'Failed to send partner cancellation email: {str(email_error)}')
        
        return jsonify({
            'message': 'Booking cancelled successfully'
        }), 200
    except AttributeError as e:
        current_app.logger.error(f'Attribute error cancelling booking {booking_id}: {str(e)}', exc_info=True)
        return jsonify({'msg': f'Failed to cancel booking: {str(e)}'}), 422
    except Exception as e:
        current_app.logger.error(f'Error cancelling booking {booking_id}: {str(e)}', exc_info=True)
        return jsonify({'msg': f'Failed to cancel booking: {str(e)}'}), 500


@bp.route('/<ticket_number>/verify', methods=['GET'])
@partner_required
def verify_ticket(current_partner, ticket_number):
    """Verify ticket for check-in"""
    ticket = Ticket.query.filter_by(ticket_number=ticket_number).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Check if ticket belongs to partner's event
    if ticket.booking.event.partner_id != current_partner.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if ticket is valid
    if not ticket.is_valid:
        return jsonify({
            'valid': False,
            'error': 'Ticket is not valid'
        }), 200
    
    if ticket.is_scanned:
        return jsonify({
            'valid': False,
            'error': 'Ticket already scanned',
            'scanned_at': ticket.scanned_at.isoformat() if ticket.scanned_at else None
        }), 200
    
    # Check if booking is confirmed
    if ticket.booking.status != 'confirmed':
        return jsonify({
            'valid': False,
            'error': 'Booking not confirmed'
        }), 200
    
    return jsonify({
        'valid': True,
        'ticket': ticket.to_dict(),
        'booking': ticket.booking.to_dict(),
        'attendee': ticket.booking.user.to_dict()
    }), 200


@bp.route('/<ticket_number>/checkin', methods=['POST'])
@partner_required
def checkin_ticket(current_partner, ticket_number):
    """Check-in ticket"""
    ticket = Ticket.query.filter_by(ticket_number=ticket_number).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Check if ticket belongs to partner's event
    if ticket.booking.event.partner_id != current_partner.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if already scanned
    if ticket.is_scanned:
        return jsonify({'error': 'Ticket already scanned'}), 400
    
    # Check if valid
    if not ticket.is_valid:
        return jsonify({'error': 'Ticket is not valid'}), 400
    
    # Check-in
    ticket.is_scanned = True
    ticket.scanned_at = datetime.utcnow()
    
    # Update booking check-in status
    if not ticket.booking.is_checked_in:
        ticket.booking.is_checked_in = True
        ticket.booking.checked_in_at = datetime.utcnow()
        ticket.booking.checked_in_by = current_partner.id
    
    db.session.commit()
    
    return jsonify({
        'message': 'Ticket checked in successfully',
        'ticket': ticket.to_dict(),
        'attendee': ticket.booking.user.to_dict()
    }), 200


@bp.route('/scan', methods=['POST'])
@partner_required
def scan_ticket(current_partner):
    """Scan and check-in ticket by QR code data"""
    data = request.get_json()
    
    if not data.get('qr_data'):
        return jsonify({'error': 'qr_data is required'}), 400
    
    # QR data should be the ticket number
    ticket_number = data['qr_data']
    
    # Verify and check-in in one step
    ticket = Ticket.query.filter_by(ticket_number=ticket_number).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Check if ticket belongs to partner's event
    if ticket.booking.event.partner_id != current_partner.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if already scanned
    if ticket.is_scanned:
        return jsonify({
            'success': False,
            'error': 'Ticket already scanned',
            'scanned_at': ticket.scanned_at.isoformat() if ticket.scanned_at else None,
            'attendee': ticket.booking.user.to_dict()
        }), 200
    
    # Check if valid
    if not ticket.is_valid or ticket.booking.status != 'confirmed':
        return jsonify({
            'success': False,
            'error': 'Ticket is not valid'
        }), 200
    
    # Check-in
    ticket.is_scanned = True
    ticket.scanned_at = datetime.utcnow()
    
    if not ticket.booking.is_checked_in:
        ticket.booking.is_checked_in = True
        ticket.booking.checked_in_at = datetime.utcnow()
        ticket.booking.checked_in_by = current_partner.id
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Ticket checked in successfully',
        'ticket': ticket.to_dict(),
        'attendee': ticket.booking.user.to_dict()
    }), 200


@bp.route('/<int:booking_id>', methods=['GET'])
@user_required
def get_ticket(current_user, booking_id):
    """Get ticket details with QR codes"""
    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=current_user.id
    ).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Get all tickets for this booking
    tickets = list(booking.tickets.all())
    if not tickets:
        return jsonify({'error': 'No tickets found for this booking'}), 404
    
    # Ensure QR codes are generated for all tickets
    from flask import current_app
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    
    ticket_data = []
    for ticket in tickets:
        # Generate QR code if it doesn't exist
        if not ticket.qr_code:
            qr_data = ticket.ticket_number
            qr_path = generate_qr_code(qr_data, ticket.ticket_number)
            ticket.qr_code = qr_path
            db.session.commit()
        
        # Build QR code URL
        if ticket.qr_code.startswith('http'):
            qr_url = ticket.qr_code
        elif ticket.qr_code.startswith('/'):
            qr_url = f"{base_url}{ticket.qr_code}"
        else:
            qr_url = f"{base_url}/uploads/{ticket.qr_code}"
        
        ticket_data.append({
            'id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'qr_code_url': qr_url,
            'qr_code_path': ticket.qr_code,
            'ticket_type': ticket.ticket_type.to_dict() if ticket.ticket_type else None,
            'is_valid': ticket.is_valid,
            'is_scanned': ticket.is_scanned,
            'scanned_at': ticket.scanned_at.isoformat() if ticket.scanned_at else None
        })
    
    return jsonify({
        'booking': booking.to_dict(),
        'tickets': ticket_data,
        'download_url': f"{base_url}/api/tickets/{booking_id}/download"
    }), 200


@bp.route('/<int:booking_id>/qr', methods=['GET'])
@user_required
def get_ticket_qr(current_user, booking_id):
    """Get QR code for a booking"""
    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=current_user.id
    ).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Get first ticket for QR code
    ticket = booking.tickets.first()
    if not ticket:
        return jsonify({'error': 'No tickets found for this booking'}), 404
    
    # Generate QR code if it doesn't exist
    if not ticket.qr_code:
        qr_data = ticket.ticket_number
        qr_path = generate_qr_code(qr_data, ticket.ticket_number)
        ticket.qr_code = qr_path
        db.session.commit()
    
    # Return QR code URL
    from flask import current_app
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    # Handle both relative paths and full URLs
    if ticket.qr_code.startswith('http'):
        qr_url = ticket.qr_code
    elif ticket.qr_code.startswith('/'):
        qr_url = f"{base_url}{ticket.qr_code}"
    else:
        qr_url = f"{base_url}/uploads/{ticket.qr_code}"
    
    return jsonify({
        'qr_code_url': qr_url,
        'ticket_number': ticket.ticket_number,
        'booking_number': booking.booking_number
    }), 200


@bp.route('/<int:booking_id>/download', methods=['GET'])
@user_required
def download_ticket(current_user, booking_id):
    """Download ticket as PDF (authenticated)"""
    from flask import send_file, current_app, Response
    import os
    
    try:
        booking = Booking.query.filter_by(
            id=booking_id,
            user_id=current_user.id
        ).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Get all tickets for this booking
        tickets = list(booking.tickets.all())
        if not tickets:
            return jsonify({'error': 'No tickets found for this booking'}), 404
        
        print(f"📄 [TICKET DOWNLOAD] Generating PDF for booking {booking_id}, {len(tickets)} tickets")
        
        # Ensure QR codes are generated for all tickets
        for ticket in tickets:
            if not ticket.qr_code:
                print(f"📄 [TICKET DOWNLOAD] Generating QR code for ticket {ticket.ticket_number}")
                qr_data = ticket.ticket_number
                qr_path = generate_qr_code(qr_data, ticket.ticket_number)
                ticket.qr_code = qr_path
                db.session.commit()
                print(f"📄 [TICKET DOWNLOAD] QR code generated: {qr_path}")
        
        # Generate PDF
        print(f"📄 [TICKET DOWNLOAD] Creating PDF buffer...")
        pdf_buffer = generate_ticket_pdf(booking, tickets)
        
        # Create filename
        filename = f"ticket-{booking.booking_number}.pdf"
        
        print(f"📄 [TICKET DOWNLOAD] PDF generated successfully, sending file: {filename}")
        
        # Reset buffer position
        pdf_buffer.seek(0)
        
        # Return PDF as download
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"❌ [TICKET DOWNLOAD] Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate ticket PDF',
            'details': str(e),
            'message': 'Please try again or contact support if the issue persists'
        }), 500


@bp.route('/download/<booking_number>', methods=['GET'])
def download_ticket_public(booking_number):
    """Public download ticket as PDF using booking number (for SMS links)"""
    from flask import send_file, current_app, Response
    import os
    
    try:
        # Find booking by booking number
        booking = Booking.query.filter_by(booking_number=booking_number).first()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Get all tickets for this booking
        tickets = list(booking.tickets.all())
        if not tickets:
            return jsonify({'error': 'No tickets found for this booking'}), 404
        
        print(f"📄 [TICKET DOWNLOAD PUBLIC] Generating PDF for booking {booking_number}, {len(tickets)} tickets")
        
        # Ensure QR codes are generated for all tickets
        for ticket in tickets:
            if not ticket.qr_code:
                print(f"📄 [TICKET DOWNLOAD PUBLIC] Generating QR code for ticket {ticket.ticket_number}")
                qr_data = ticket.ticket_number
                qr_path = generate_qr_code(qr_data, ticket.ticket_number)
                ticket.qr_code = qr_path
                db.session.commit()
                print(f"📄 [TICKET DOWNLOAD PUBLIC] QR code generated: {qr_path}")
        
        # Generate PDF
        print(f"📄 [TICKET DOWNLOAD PUBLIC] Creating PDF buffer...")
        pdf_buffer = generate_ticket_pdf(booking, tickets)
        
        # Create filename
        filename = f"ticket-{booking.booking_number}.pdf"
        
        print(f"📄 [TICKET DOWNLOAD PUBLIC] PDF generated successfully, sending file: {filename}")
        
        # Reset buffer position
        pdf_buffer.seek(0)
        
        # Return PDF as download
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"❌ [TICKET DOWNLOAD PUBLIC] Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate ticket PDF',
            'details': str(e),
            'message': 'Please try again or contact support if the issue persists'
        }), 500


@bp.route('/release-expired', methods=['POST'])
def release_expired_bookings():
    """Release expired pending bookings (called by background task or frontend)"""
    try:
        # Find all pending bookings that have expired (reserved_until < now)
        expired_bookings = Booking.query.filter(
            Booking.status == 'pending',
            Booking.payment_status == 'unpaid',
            Booking.reserved_until.isnot(None),
            Booking.reserved_until < datetime.utcnow()
        ).all()
        
        released_count = 0
        for booking in expired_bookings:
            # Cancel the expired booking
            booking.status = 'cancelled'
            booking.cancelled_at = datetime.utcnow()
            
            # Restore promo code usage if applicable
            if booking.promo_code:
                booking.promo_code.current_uses = max(0, booking.promo_code.current_uses - 1)
            
            released_count += 1
        
        if released_count > 0:
            db.session.commit()
            current_app.logger.info(f'Released {released_count} expired bookings')
        
        return jsonify({
            'message': f'Released {released_count} expired booking(s)',
            'released_count': released_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error releasing expired bookings: {str(e)}')
        return jsonify({'error': 'Failed to release expired bookings'}), 500

