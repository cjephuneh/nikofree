from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app import db
from app.models.payment import Payment
from app.models.ticket import Booking
from app.models.ticket import Ticket
from app.models.event import EventPromotion
from app.utils.decorators import user_required
from app.utils.mpesa import MPesaClient, format_phone_number
from app.utils.qrcode_generator import generate_qr_code
from app.utils.email import send_booking_confirmation_email
from app.routes.notifications import notify_new_booking, notify_payment_completed

bp = Blueprint('payments', __name__)


@bp.route('/initiate', methods=['POST'])
@user_required
def initiate_payment(current_user):
    """Initiate payment for booking"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('booking_id') or not data.get('phone_number'):
        return jsonify({'error': 'booking_id and phone_number are required'}), 400
    
    # Get booking
    booking = Booking.query.filter_by(
        id=data['booking_id'],
        user_id=current_user.id
    ).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    if booking.payment_status == 'paid':
        return jsonify({'error': 'Booking already paid'}), 400
    
    # Format phone number
    phone = format_phone_number(data['phone_number'])
    
    # Generate transaction ID
    import uuid
    transaction_id = f"NF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    
    # Create payment record
    payment = Payment(
        transaction_id=transaction_id,
        user_id=current_user.id,
        event_id=booking.event_id,
        partner_id=booking.event.partner_id,
        amount=booking.total_amount,
        platform_fee=booking.platform_fee,
        partner_amount=booking.partner_amount,
        payment_method='mpesa',
        payment_provider='daraja',
        phone_number=phone,
        description=f"Ticket payment for {booking.event.title}",
        payment_type='ticket',
        status='pending'
    )
    
    db.session.add(payment)
    db.session.flush()
    
    # Link payment to booking
    booking.payment_id = payment.id
    db.session.commit()
    
    # Initiate MPesa STK Push
    mpesa = MPesaClient()
    response = mpesa.stk_push(
        phone_number=phone,
        amount=float(booking.total_amount),
        account_reference=booking.booking_number,
        transaction_desc=f"Payment for {booking.event.title}"
    )
    
    # Save response
    payment.provider_response = response
    
    if response.get('ResponseCode') == '0':
        # Success - STK push sent
        payment.payment_metadata = {
            'CheckoutRequestID': response.get('CheckoutRequestID'),
            'MerchantRequestID': response.get('MerchantRequestID')
        }
        db.session.commit()
        
        return jsonify({
            'message': 'Payment initiated. Please check your phone to complete payment.',
            'payment_id': payment.id,
            'transaction_id': transaction_id,
            'checkout_request_id': response.get('CheckoutRequestID')
        }), 200
    else:
        # Failed
        payment.status = 'failed'
        payment.error_message = response.get('errorMessage') or response.get('ResponseDescription')
        db.session.commit()
        
        return jsonify({
            'error': 'Failed to initiate payment',
            'message': payment.error_message
        }), 400


@bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """MPesa payment callback"""
    data = request.get_json()
    
    # Extract callback data
    callback_data = data.get('Body', {}).get('stkCallback', {})
    result_code = callback_data.get('ResultCode')
    checkout_request_id = callback_data.get('CheckoutRequestID')
    
    # Find payment
    payment = Payment.query.filter(
        Payment.payment_metadata['CheckoutRequestID'].astext == checkout_request_id
    ).first()
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    if result_code == 0:
        # Payment successful
        callback_metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])
        
        # Extract details
        mpesa_receipt = None
        phone_number = None
        
        for item in callback_metadata:
            if item.get('Name') == 'MpesaReceiptNumber':
                mpesa_receipt = item.get('Value')
            elif item.get('Name') == 'PhoneNumber':
                phone_number = item.get('Value')
        
        # Update payment
        payment.status = 'completed'
        payment.completed_at = datetime.utcnow()
        payment.mpesa_receipt_number = mpesa_receipt
        
        # Update booking
        booking = payment.booking
        if booking:
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.confirmed_at = datetime.utcnow()
            
            # Create tickets
            tickets = []
            for i in range(booking.quantity):
                ticket = Ticket(
                    booking_id=booking.id,
                    ticket_type_id=booking.event.ticket_types.first().id  # TODO: Handle multiple ticket types
                )
                db.session.add(ticket)
                db.session.flush()
                
                # Generate QR code
                qr_data = ticket.ticket_number
                qr_path = generate_qr_code(qr_data, ticket.ticket_number)
                ticket.qr_code = qr_path
                
                tickets.append(ticket)
            
            # Update event stats
            event = booking.event
            event.attendee_count += booking.quantity
            event.total_tickets_sold += booking.quantity
            event.revenue += booking.total_amount
            
            # Update partner earnings
            partner = event.organizer
            partner.pending_earnings += booking.partner_amount
            partner.total_earnings += booking.partner_amount
            
            # Update ticket type availability
            ticket_type = booking.event.ticket_types.first()
            if ticket_type and ticket_type.quantity_available is not None:
                ticket_type.quantity_available -= booking.quantity
                ticket_type.quantity_sold += booking.quantity
            
            # Update promo code usage
            if booking.promo_code:
                booking.promo_code.current_uses += 1
            
            db.session.commit()
            
            # Send confirmation email
            send_booking_confirmation_email(booking, tickets)
            
            # Notify partner of new booking and payment
            notify_new_booking(event, booking)
            notify_payment_completed(booking, payment)
    else:
        # Payment failed
        payment.status = 'failed'
        payment.failed_at = datetime.utcnow()
        payment.error_message = callback_data.get('ResultDesc')
        
        if payment.booking:
            payment.booking.payment_status = 'failed'
        
        db.session.commit()
    
    return jsonify({'message': 'Callback processed'}), 200


@bp.route('/status/<int:payment_id>', methods=['GET'])
@user_required
def check_payment_status(current_user, payment_id):
    """Check payment status"""
    payment = Payment.query.filter_by(
        id=payment_id,
        user_id=current_user.id
    ).first()
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # If still pending, query MPesa
    if payment.status == 'pending' and payment.payment_metadata:
        checkout_request_id = payment.payment_metadata.get('CheckoutRequestID')
        
        if checkout_request_id:
            mpesa = MPesaClient()
            response = mpesa.stk_query(checkout_request_id)
            
            result_code = response.get('ResultCode')
            
            if result_code == '0':
                # Payment completed - update status
                payment.status = 'completed'
                payment.completed_at = datetime.utcnow()
                
                if payment.booking:
                    payment.booking.payment_status = 'paid'
                    payment.booking.status = 'confirmed'
                    payment.booking.confirmed_at = datetime.utcnow()
                
                db.session.commit()
            elif result_code:
                # Payment failed
                payment.status = 'failed'
                payment.failed_at = datetime.utcnow()
                db.session.commit()
    
    return jsonify({
        'payment': payment.to_dict(),
        'booking': payment.booking.to_dict() if payment.booking else None
    }), 200


@bp.route('/history', methods=['GET'])
@user_required
def payment_history(current_user):
    """Get user's payment history"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    payments = Payment.query.filter_by(
        user_id=current_user.id
    ).order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'payments': [payment.to_dict() for payment in payments.items],
        'total': payments.total,
        'page': payments.page,
        'pages': payments.pages
    }), 200


# ============ EVENT PROMOTION PAYMENTS ============

@bp.route('/promote-event', methods=['POST'])
def initiate_promotion_payment():
    """Initiate payment for event promotion"""
    data = request.get_json()
    
    # Validate required fields
    required = ['event_id', 'phone_number', 'days']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    from app.models.event import Event
    event = Event.query.get(data['event_id'])
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Calculate cost
    days = int(data['days'])
    price_per_day = current_app.config.get('PROMOTION_PRICE_PER_DAY', 400)
    total_cost = days * price_per_day
    
    # Create promotion record
    from datetime import timedelta
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=days)
    
    promotion = EventPromotion(
        event_id=event.id,
        start_date=start_date,
        end_date=end_date,
        days_count=days,
        total_cost=total_cost,
        is_active=False,
        is_paid=False
    )
    
    db.session.add(promotion)
    db.session.flush()
    
    # Create payment record
    import uuid
    transaction_id = f"PROMO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    
    payment = Payment(
        transaction_id=transaction_id,
        event_id=event.id,
        partner_id=event.partner_id,
        amount=total_cost,
        payment_method='mpesa',
        payment_provider='daraja',
        phone_number=format_phone_number(data['phone_number']),
        description=f"Promotion for {event.title} - {days} days",
        payment_type='promotion',
        status='pending'
    )
    
    db.session.add(payment)
    
    # Link payment to promotion
    promotion.payment_id = payment.id
    db.session.commit()
    
    # Initiate MPesa STK Push
    mpesa = MPesaClient()
    response = mpesa.stk_push(
        phone_number=payment.phone_number,
        amount=float(total_cost),
        account_reference=f"PROMO-{event.id}",
        transaction_desc=f"Event Promotion - {days} days"
    )
    
    # Save response
    payment.provider_response = response
    
    if response.get('ResponseCode') == '0':
        payment.payment_metadata = {
            'CheckoutRequestID': response.get('CheckoutRequestID'),
            'MerchantRequestID': response.get('MerchantRequestID')
        }
        db.session.commit()
        
        return jsonify({
            'message': 'Payment initiated',
            'payment_id': payment.id,
            'promotion_id': promotion.id,
            'amount': float(total_cost)
        }), 200
    else:
        payment.status = 'failed'
        payment.error_message = response.get('errorMessage')
        db.session.commit()
        
        return jsonify({
            'error': 'Failed to initiate payment',
            'message': payment.error_message
        }), 400

