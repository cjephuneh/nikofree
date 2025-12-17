from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import re
from sqlalchemy import func, or_, cast, String
from app import db
from app.models.payment import Payment
from app.models.ticket import Booking
from app.models.ticket import Ticket
from app.models.event import EventPromotion
from app.models.partner import Partner
from app.utils.decorators import user_required
from app.utils.mpesa import MPesaClient, format_phone_number
from app.utils.qrcode_generator import generate_qr_code
from app.utils.email import send_booking_confirmation_email, send_payment_confirmation_email, send_payment_failed_email, send_promotion_payment_success_email, send_payment_failed_email
from app.utils.sms import (
    send_payment_confirmation_sms, 
    send_booking_confirmation_sms,
    send_payment_failed_sms,
    send_promotion_payment_success_sms
)
from app.routes.notifications import notify_new_booking, notify_payment_completed, create_notification

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
    
    # Validate amount (minimum 1 KES for MPesa)
    if float(booking.total_amount) < 1:
        return jsonify({'error': 'Payment amount must be at least KES 1'}), 400
    
    # Format phone number
    phone = format_phone_number(data['phone_number'])
    
    # Validate phone number format (must be 12 digits starting with 254)
    if not phone or len(phone) != 12 or not phone.startswith('254'):
        return jsonify({
            'error': 'Invalid phone number format. Please use a valid Kenyan phone number (e.g., 0708419386 or 254708419386)'
        }), 400
    
    # Validate phone number is numeric after 254
    if not phone[3:].isdigit():
        return jsonify({
            'error': 'Invalid phone number. Phone number must contain only digits after country code'
        }), 400
    
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
        
        current_app.logger.info(
            f'STK push initiated successfully for payment {payment.id}: '
            f'Phone={phone}, Amount={payment.amount}, CheckoutRequestID={response.get("CheckoutRequestID")}'
        )
        
        return jsonify({
            'message': 'Payment initiated. Please check your phone to complete payment.',
            'payment_id': payment.id,
            'transaction_id': transaction_id,
            'checkout_request_id': response.get('CheckoutRequestID'),
            'amount': float(payment.amount)
        }), 200
    else:
        # Failed to initiate STK push
        payment.status = 'failed'
        payment.failed_at = datetime.utcnow()
        error_code = response.get('errorCode') or response.get('ResponseCode')
        error_message = response.get('errorMessage') or response.get('ResponseDescription') or 'Failed to initiate payment'
        payment.error_message = error_message
        db.session.commit()
        
        current_app.logger.error(
            f'STK push initiation failed for payment {payment.id}: '
            f'ErrorCode={error_code}, ErrorMessage={error_message}, Phone={phone}, Amount={payment.amount}'
        )
        
        # Provide more helpful error messages
        if '2001' in str(error_code) or 'invalid' in error_message.lower():
            error_message = 'Invalid phone number or amount. Please ensure your phone number is registered for M-Pesa and try again. If using sandbox, ensure you are using a test number.'
        elif 'insufficient' in error_message.lower() or 'balance' in error_message.lower():
            error_message = 'Insufficient balance. Please ensure you have enough funds in your M-Pesa account.'
        
        return jsonify({'error': error_message}), 400


@bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """
    MPesa payment callback webhook
    
    This endpoint receives payment confirmations from Safaricom M-Pesa Daraja API.
    Callback URL should be configured in M-Pesa Daraja portal as:
    https://nikofree-arhecnfueegrasf8.canadacentral-01.azurewebsites.net/api/payments/mpesa/callback
    
    The callback is called automatically when:
    - User completes STK push payment
    - Payment is cancelled or fails
    """
    try:
        data = request.get_json()
        
        # Log callback for debugging
        current_app.logger.info(f'MPesa callback received: {data}')
        
        if not data:
            current_app.logger.error('MPesa callback: No data received')
            return jsonify({'error': 'No data received'}), 400
        
        # Extract callback data
        callback_data = data.get('Body', {}).get('stkCallback', {})
        if not callback_data:
            current_app.logger.error(f'MPesa callback: Invalid callback structure: {data}')
            return jsonify({'error': 'Invalid callback structure'}), 400
        
        result_code = callback_data.get('ResultCode')
        checkout_request_id = callback_data.get('CheckoutRequestID')
        
        if not checkout_request_id:
            current_app.logger.error(f'MPesa callback: No CheckoutRequestID in callback: {callback_data}')
            return jsonify({'error': 'CheckoutRequestID missing'}), 400
        
        # Find payment by CheckoutRequestID
        # Use a database-agnostic approach that works with SQLite and PostgreSQL
        # SQLite stores JSON as TEXT, so we can use json_extract or filter in Python
        payment = None
        try:
            # Try SQLite JSON1 extension (most efficient for SQLite)
            payment = Payment.query.filter(
                func.json_extract(Payment.payment_metadata, '$.CheckoutRequestID') == checkout_request_id
            ).first()
        except Exception as e:
            current_app.logger.debug(f'JSON1 query failed, using Python filter: {str(e)}')
        
        # Fallback: if JSON1 didn't work or returned None, filter in Python
        if not payment:
            all_payments = Payment.query.filter(
                Payment.payment_metadata.isnot(None)
            ).all()
            payment = next(
                (p for p in all_payments 
                 if p.payment_metadata and p.payment_metadata.get('CheckoutRequestID') == checkout_request_id),
                None
            )
        
        if not payment:
            current_app.logger.error(f'MPesa callback: Payment not found for CheckoutRequestID: {checkout_request_id}')
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
            
            # Handle promotion payments
            if payment.payment_type == 'promotion':
                promotion = EventPromotion.query.filter_by(payment_id=payment.id).first()
                if promotion:
                    promotion.is_paid = True
                    promotion.is_active = True
                    db.session.commit()
                    
                    # Notify partner
                    partner = Partner.query.get(payment.partner_id)
                    if partner:
                        create_notification(
                            partner_id=partner.id,
                            title='Promotion Payment Successful!',
                            message=f'Your event "{promotion.event.title}" is now promoted in the Can\'t Miss section.',
                            notification_type='promotion',
                            event_id=promotion.event_id,
                            action_url=f'/events/{promotion.event_id}',
                            action_text='View Event'
                        )
                        # Send promotion success SMS and email
                        try:
                            send_promotion_payment_success_sms(partner, promotion.event)
                        except Exception as sms_error:
                            current_app.logger.warning(f'Failed to send promotion success SMS: {str(sms_error)}')
                        
                        try:
                            send_promotion_payment_success_email(partner, promotion.event)
                        except Exception as email_error:
                            current_app.logger.warning(f'Failed to send promotion success email: {str(email_error)}')
                    
                    return jsonify({'message': 'Payment processed'}), 200
            
            # Update booking - find booking by payment_id
            booking = None
            if payment.payment_type == 'ticket':
                booking = Booking.query.filter_by(payment_id=payment.id).first()
            
            if booking:
                booking.payment_status = 'paid'
                booking.status = 'confirmed'
                booking.confirmed_at = datetime.utcnow()
                booking.reserved_until = None  # Clear reservation timer on payment
                
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
                
                # Send payment confirmation email to user
                send_payment_confirmation_email(booking, payment, tickets)
                
                # Send booking confirmation email (includes tickets)
                send_booking_confirmation_email(booking, tickets)
                
                # Send payment confirmation SMS
                send_payment_confirmation_sms(booking, payment)
                
                # Send booking confirmation SMS
                # Use phone number from payment (most reliable for paid events)
                phone_for_sms = payment.phone_number or booking.user.phone_number
                send_booking_confirmation_sms(booking, tickets, phone_number_override=phone_for_sms)
                
                # Notify user of successful payment
                create_notification(
                    user_id=booking.user_id,
                    title='Payment Successful!',
                    message=f'Your payment of KES {payment.amount:,.2f} for "{event.title}" has been confirmed.',
                    notification_type='payment',
                    event_id=event.id,
                    booking_id=booking.id,
                    action_url=f'/bookings/{booking.id}',
                    action_text='View Booking',
                    send_email=False  # Already sent email above
                )
                
                # Notify partner of new booking and payment
                notify_new_booking(event, booking)
                notify_payment_completed(booking, payment)
        else:
            # Payment failed or cancelled
            result_desc = callback_data.get('ResultDesc', 'Payment failed')
            result_code_int = int(result_code) if result_code is not None else None
            
            # Map MPesa result codes:
            # ResultCode 0 = Success (handled above)
            # ResultCode 2001 = Initiator information invalid (STK push never sent - phone/amount validation failed)
            # ResultCode 1032 = User cancelled the STK push (user saw prompt and cancelled)
            # ResultCode 2002 = Insufficient balance (user tried to pay but no funds)
            # ResultCode 2003 = Transaction cancelled by user (user cancelled)
            # ResultCode 2004 = Transaction timeout (user didn't respond in time - wait longer before marking failed)
            # ResultCode 2005 = Duplicate transaction
            
            # ResultCode 2001 means the STK push was never sent to the user's phone
            # This happens when MPesa validates the request and finds issues before sending
            # Common causes: phone not registered for M-Pesa, invalid test number in sandbox, etc.
            # Since the user never got a prompt, we should mark as failed immediately
            
            # For ResultCode 2004 (timeout), the user might still be processing the payment
            # Give them more time - don't mark as failed immediately, keep as pending for a bit longer
            # Only mark as failed if it's been pending for more than 2 minutes after timeout callback
            
            # Check if payment was created recently (within last 2 minutes)
            time_since_creation = (datetime.utcnow() - payment.created_at).total_seconds()
            
            # For timeout (2004), wait at least 2 minutes before marking as failed
            # This gives the user time to complete the payment even if MPesa sends timeout callback early
            if result_code_int == 2004 and time_since_creation < 120:
                # Keep as pending - user might still complete payment
                current_app.logger.info(
                    f'Payment {payment.id} timeout callback received but payment created recently '
                    f'({time_since_creation:.1f}s ago). Keeping as pending to allow user to complete payment.'
                )
                # Don't mark as failed yet - let the status check endpoint handle it after timeout period
                return jsonify({'message': 'Callback received, payment still pending'}), 200
            
            # For other failure codes, mark as failed immediately
            # But for codes where user had interaction (1032, 2002, 2003), they attempted payment
            payment.status = 'failed'
            payment.failed_at = datetime.utcnow()
            payment.error_message = result_desc
            
            # Log the failure reason with more context
            current_app.logger.warning(
                f'Payment {payment.id} failed: ResultCode={result_code}, '
                f'ResultDesc={result_desc}, Phone={payment.phone_number}, Amount={payment.amount}'
            )
            
            # Find booking for failed payment
            booking = None
            if payment.payment_type == 'ticket':
                booking = Booking.query.filter_by(payment_id=payment.id).first()
            
            if booking:
                booking.payment_status = 'failed'
                # Send payment failed SMS for ResultCode 2001 (validation failed - STK push never sent)
                # ResultCode 2001 means the phone number/amount validation failed at MPesa's end
                # The user never received the STK push prompt, so we should inform them
                if result_code == 2001:
                    # Check if we're in sandbox mode for better error messaging
                    is_sandbox = current_app.config.get('MPESA_ENVIRONMENT', 'sandbox') == 'sandbox'
                user = booking.user
                event = booking.event
                if user and event:
                    try:
                        # Only send SMS if it's not a sandbox validation issue
                        # In sandbox, ResultCode 2001 usually means phone not registered as test number
                        # We'll still send the SMS but the frontend should show a better message
                        send_payment_failed_sms(user, payment, event)
                    except Exception as sms_error:
                        current_app.logger.warning(f'Failed to send payment failed SMS: {str(sms_error)}')
                    
                    try:
                        send_payment_failed_email(user, payment, event)
                    except Exception as email_error:
                        current_app.logger.warning(f'Failed to send payment failed email: {str(email_error)}')
            
            db.session.commit()
        
        current_app.logger.info(f'MPesa callback processed for payment {payment.id}, result_code: {result_code}')
        return jsonify({'message': 'Callback processed'}), 200
    except Exception as e:
        current_app.logger.error(f'Error processing MPesa callback: {str(e)}', exc_info=True)
        return jsonify({'error': 'Internal server error processing callback'}), 500


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
    # But only query if payment was created more than 30 seconds ago
    # This prevents querying too early before MPesa has processed the request
    time_since_creation = (datetime.utcnow() - payment.created_at).total_seconds()
    
    if payment.status == 'pending' and payment.payment_metadata and time_since_creation > 30:
        checkout_request_id = payment.payment_metadata.get('CheckoutRequestID')
        
        if checkout_request_id:
            current_app.logger.info(f'Querying MPesa for payment {payment.id} with CheckoutRequestID: {checkout_request_id}')
            mpesa = MPesaClient()
            response = mpesa.stk_query(checkout_request_id)
            
            current_app.logger.info(f'MPesa STK query response for payment {payment.id}: {response}')
            
            result_code = response.get('ResultCode')
            result_code_int = int(result_code) if result_code is not None else None
            
            # Handle both string and int result codes
            if result_code == '0' or result_code == 0:
                # Payment completed - process like callback
                current_app.logger.info(f'Payment {payment.id} completed according to MPesa query')
                payment.status = 'completed'
                payment.completed_at = datetime.utcnow()
                
                # Extract receipt number from query response if available
                # STK Query response structure may differ from callback
                # Try multiple possible locations for receipt number
                receipt_number = None
                
                # Check ResponseDescription field
                if 'ResponseDescription' in response:
                    desc = response.get('ResponseDescription', '')
                    receipt_match = re.search(r'[A-Z0-9]{10}', desc)
                    if receipt_match:
                        receipt_number = receipt_match.group()
                
                # Check if receipt is in ResultDesc
                if not receipt_number and 'ResultDesc' in response:
                    desc = str(response.get('ResultDesc', ''))
                    receipt_match = re.search(r'[A-Z0-9]{10}', desc)
                    if receipt_match:
                        receipt_number = receipt_match.group()
                
                if receipt_number:
                    payment.mpesa_receipt_number = receipt_number
                    current_app.logger.info(f'Extracted receipt number {receipt_number} for payment {payment.id}')
                
                # Find booking for payment
                booking = None
                if payment.payment_type == 'ticket':
                    booking = Booking.query.filter_by(payment_id=payment.id).first()
                
                if booking:
                    booking.payment_status = 'paid'
                    booking.status = 'confirmed'
                    booking.confirmed_at = datetime.utcnow()
                    
                    # Create tickets if they don't exist
                    if booking.tickets.count() == 0:
                        tickets = []
                        for i in range(booking.quantity):
                            ticket = Ticket(
                                booking_id=booking.id,
                                ticket_type_id=booking.event.ticket_types.first().id
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
                        if partner:
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
                        
                        # Send notifications
                        send_payment_confirmation_email(booking, payment, tickets)
                        send_booking_confirmation_email(booking, tickets)
                        send_payment_confirmation_sms(booking, payment)
                        phone_for_sms = payment.phone_number or booking.user.phone_number
                        send_booking_confirmation_sms(booking, tickets, phone_number_override=phone_for_sms)
                        
                        # Create notifications
                        create_notification(
                            user_id=booking.user_id,
                            title='Payment Successful!',
                            message=f'Your payment of KES {payment.amount:,.2f} for "{event.title}" has been confirmed.',
                            notification_type='payment',
                            event_id=event.id,
                            booking_id=booking.id,
                            action_url=f'/bookings/{booking.id}',
                            action_text='View Booking',
                            send_email=False
                        )
                        
                        notify_new_booking(event, booking)
                        notify_payment_completed(booking, payment)
                    else:
                        # Tickets already exist, just commit payment status
                        db.session.commit()
                else:
                    db.session.commit()
                    
            elif result_code:
                # Payment failed - but check if it's a timeout and payment is still recent
                # For timeout (2004), wait at least 3 minutes before marking as failed
                # This gives the user time to complete the payment
                if result_code_int == 2004 and time_since_creation < 180:
                    # Keep as pending - user might still complete payment
                    current_app.logger.info(
                        f'Payment {payment.id} timeout query result but payment created recently '
                        f'({time_since_creation:.1f}s ago). Keeping as pending.'
                    )
                else:
                    # Payment failed - mark as failed
                    payment.status = 'failed'
                    payment.failed_at = datetime.utcnow()
                    payment.error_message = response.get('ResultDesc') or response.get('errorMessage')
                    db.session.commit()
    
    # Get booking - payment.booking might be a list or single object
    booking = None
    if payment.payment_type == 'ticket':
        # For ticket payments, find the booking by payment_id
        booking = Booking.query.filter_by(payment_id=payment.id).first()
    
    return jsonify({
        'payment': payment.to_dict(),
        'booking': booking.to_dict() if booking else None
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

