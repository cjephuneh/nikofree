"""
SMS Utility using Celcom Africa API
"""
import requests
from flask import current_app
from threading import Thread
import urllib3

# Disable SSL warnings (since we're using verify=False to match PHP example)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Celcom Africa SMS API Configuration
CELCOM_SMS_URL = "https://isms.celcomafrica.com/api/services/sendsms/"
CELCOM_API_KEY = "ffbf65bc0649575080064282d3a324f8"
CELCOM_PARTNER_ID = "946"
CELCOM_SHORTCODE = "NIKO FREE"


def send_sms_async(app, phone_number, message):
    """Send SMS asynchronously using Celcom Africa API"""
    print(f"📱 [SMS ASYNC] Starting SMS send to {phone_number}")
    with app.app_context():
        try:
            # Check if SMS sending is suppressed (for development)
            if app.config.get('SMS_SUPPRESS_SEND', False):
                print(f"📱 [SMS ASYNC] [DEV MODE] SMS suppressed: {message[:50]}... to {phone_number}")
                return
            
            # Prepare payload (matching PHP example format)
            payload = {
                "apikey": CELCOM_API_KEY,
                "partnerID": CELCOM_PARTNER_ID,
                "message": message,
                "shortcode": CELCOM_SHORTCODE,
                "mobile": phone_number,
                "pass_type": "plain"  # Optional: 'plain' or 'bm5' (base64)
            }
            
            print(f"📱 [SMS ASYNC] Sending POST request to {CELCOM_SMS_URL}")
            print(f"📱 [SMS ASYNC] Payload: {payload}")
            
            # Send POST request with JSON body (matching PHP example)
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(
                CELCOM_SMS_URL, 
                json=payload, 
                headers=headers,
                timeout=30,
                verify=False  # SSL verification disabled (matching PHP example)
            )
            
            print(f"📱 [SMS ASYNC] Response status: {response.status_code}")
            print(f"📱 [SMS ASYNC] Response text: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"📱 [SMS ASYNC] Response JSON: {result}")
                    
                    # Check response format: {"responses":[{"response-code":200,...}]}
                    if 'responses' in result and isinstance(result['responses'], list):
                        for response_item in result['responses']:
                            response_code = response_item.get('response-code') or response_item.get('respose-code')  # Handle typo in API
                            if response_code == 200:
                                message_id = response_item.get('messageid')
                                mobile = response_item.get('mobile')
                                description = response_item.get('response-description', 'Success')
                                print(f"✅ [SMS ASYNC] SMS sent successfully to {mobile}")
                                print(f"   Message ID: {message_id}, Description: {description}")
                            else:
                                error_code = response_code
                                error_desc = response_item.get('response-description', 'Unknown error')
                                print(f"❌ [SMS ASYNC] SMS failed: Code {error_code} - {error_desc}")
                    else:
                        # Fallback: check for success indicators
                        if result.get('success') or result.get('status') == 'success':
                            print(f"✅ [SMS ASYNC] SMS sent successfully to {phone_number}")
                        else:
                            print(f"❌ [SMS ASYNC] SMS failed: {result}")
                except ValueError as e:
                    print(f"❌ [SMS ASYNC] Failed to parse JSON response: {response.text}")
                    print(f"   Error: {e}")
            else:
                print(f"❌ [SMS ASYNC] SMS API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ [SMS ASYNC] Error sending SMS: {str(e)}")
            import traceback
            traceback.print_exc()


def send_sms(phone_number, message):
    """Send SMS (async and non-blocking)"""
    print(f"📱 [SMS] send_sms called for phone: {phone_number}, message length: {len(message)}")
    try:
        from flask import current_app
        app = current_app._get_current_object()
        
        print(f"📱 [SMS] Starting async thread for SMS to {phone_number}")
        # Start thread and don't wait for it
        thread = Thread(target=send_sms_async, args=(app, phone_number, message))
        thread.daemon = True  # Daemon thread won't block app shutdown
        thread.start()
        print(f"📱 [SMS] Thread started for {phone_number}")
        
    except Exception as e:
        # Don't let SMS errors crash the app
        print(f"❌ [SMS] Error queuing SMS: {str(e)}")
        import traceback
        traceback.print_exc()


def format_phone_for_sms(phone_number):
    """Format phone number for SMS (ensure it starts with country code)"""
    if not phone_number:
        return None
    
    # Convert to string if not already
    phone_str = str(phone_number).strip()
    
    if not phone_str:
        return None
    
    # Remove any spaces, dashes, or other characters
    phone = ''.join(filter(str.isdigit, phone_str))
    
    if not phone:
        return None
    
    # If it doesn't start with 254, add it
    if not phone.startswith('254'):
        if phone.startswith('0'):
            # Replace leading 0 with 254
            phone = '254' + phone[1:]
        elif phone.startswith('+254'):
            phone = phone[1:]  # Remove +
        else:
            # Assume it's a local number, add 254
            phone = '254' + phone
    
    # Validate length (should be 12 digits: 254XXXXXXXXX)
    if len(phone) != 12:
        print(f"⚠️ [SMS] Invalid phone number length: {phone} (expected 12 digits)")
        return None
    
    return phone


def send_booking_confirmation_sms(booking, tickets, phone_number_override=None):
    """Send booking confirmation SMS
    
    Args:
        booking: Booking object
        tickets: List of Ticket objects
        phone_number_override: Optional phone number to use (from booking request)
    """
    print(f"📱 [SMS] send_booking_confirmation_sms called for booking {booking.id}")
    user = booking.user
    event = booking.event
    
    # Refresh user from database to get latest phone number
    from app import db
    db.session.refresh(user)
    
    print(f"📱 [SMS] User ID: {user.id}, Email: {user.email}, Phone: {user.phone_number}")
    if phone_number_override:
        print(f"📱 [SMS] Phone number override provided: {phone_number_override}")
    
    # Try phone number override first (from booking request)
    phone = None
    if phone_number_override:
        try:
            phone = format_phone_for_sms(phone_number_override)
            if phone:
                print(f"📱 [SMS] Using phone number from booking request: {phone}")
            else:
                print(f"⚠️ [SMS] Phone number override {phone_number_override} failed validation")
        except Exception as e:
            print(f"⚠️ [SMS] Error formatting phone number override: {e}")
            import traceback
            traceback.print_exc()
    
    # Try to get phone number from user
    if not phone and user.phone_number:
        try:
            phone = format_phone_for_sms(user.phone_number)
            if phone:
                print(f"📱 [SMS] Using user phone number: {phone}")
            else:
                print(f"⚠️ [SMS] User phone number {user.phone_number} failed validation")
        except Exception as e:
            print(f"⚠️ [SMS] Error formatting user phone number: {e}")
            import traceback
            traceback.print_exc()
    
    # For paid events, try to get phone from payment as fallback
    if not phone and booking.payment_status == 'paid':
        # Try to get phone from payment record
        from app.models.payment import Payment
        payment = Payment.query.filter_by(booking_id=booking.id, status='completed').first()
        if payment and payment.phone_number:
            try:
                phone = format_phone_for_sms(payment.phone_number)
                if phone:
                    print(f"📱 [SMS] Using payment phone number as fallback: {phone}")
                else:
                    print(f"⚠️ [SMS] Payment phone number {payment.phone_number} failed validation")
            except Exception as e:
                print(f"⚠️ [SMS] Error formatting payment phone number: {e}")
                import traceback
                traceback.print_exc()
    
    if not phone:
        print(f"⚠️ [SMS] No phone number available for user {user.id} (email: {user.email}), skipping SMS")
        print(f"⚠️ [SMS] User phone_number field: {repr(user.phone_number)}")
        print(f"⚠️ [SMS] Booking payment_status: {booking.payment_status}")
        print(f"⚠️ [SMS] Phone override provided: {phone_number_override}")
        return
    
    print(f"📱 [SMS] Formatted phone: {phone}")
    
    # Get base URL for download link (using frontend route for better UX)
    from flask import current_app
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    # Use frontend route that handles the download properly
    download_url = f"{base_url}/download-ticket/{booking.booking_number}"
    
    # Create message
    ticket_numbers = ', '.join([t.ticket_number for t in tickets[:3]])  # First 3 tickets
    if len(tickets) > 3:
        ticket_numbers += f" and {len(tickets) - 3} more"
    
    message = f"""Booking Confirmed! 🎉

Event: {event.title}
Date: {event.start_date.strftime('%d/%m/%Y %I:%M %p')}
Venue: {event.venue_name or event.venue_address or 'Online'}
Booking: {booking.booking_number}
Tickets: {ticket_numbers}
Amount: KES {booking.total_amount:,.2f}

Download ticket & QR code:
{download_url}

Present QR code at entrance.
Thank you for using Niko Free!"""
    
    print(f"📱 [SMS] Sending booking confirmation SMS to {phone} for event '{event.title}'")
    send_sms(phone, message)
    print(f"📱 [SMS] SMS queued for {phone}")


def send_payment_confirmation_sms(booking, payment):
    """Send payment confirmation SMS"""
    user = booking.user
    event = booking.event
    
    print(f"📱 [SMS] send_payment_confirmation_sms called for payment {payment.id}, booking {booking.id}")
    print(f"📱 [SMS] User ID: {user.id}, Email: {user.email}, User Phone: {user.phone_number}")
    print(f"📱 [SMS] Payment Phone: {payment.phone_number}")
    
    # Try payment phone number first (most reliable for paid events)
    phone = None
    if payment.phone_number:
        try:
            phone = format_phone_for_sms(payment.phone_number)
            print(f"📱 [SMS] Using payment phone number: {phone}")
        except Exception as e:
            print(f"⚠️ [SMS] Error formatting payment phone number: {e}")
    
    # Fallback to user's phone number
    if not phone and user.phone_number:
        try:
            phone = format_phone_for_sms(user.phone_number)
            print(f"📱 [SMS] Using user phone number as fallback: {phone}")
        except Exception as e:
            print(f"⚠️ [SMS] Error formatting user phone number: {e}")
    
    if not phone:
        print(f"⚠️ [SMS] No phone number available for payment {payment.id} (user {user.id}, email: {user.email}), skipping SMS")
        return
    
    print(f"📱 [SMS] Formatted phone: {phone}")
    
    # Create message
    message = f"""Payment Confirmed! ✅

Event: {event.title}
Amount: KES {payment.amount:,.2f}
Receipt: {payment.mpesa_receipt_number or payment.transaction_id}
Booking: {booking.booking_number}

Your tickets have been confirmed. Check your email for QR codes.
Thank you for using Niko Free!"""
    
    send_sms(phone, message)


def send_welcome_sms(user):
    """Send welcome SMS to new user"""
    if not user.phone_number:
        print(f"⚠️ No phone number for user {user.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(user.phone_number)
    
    message = f"""Welcome to Niko Free, {user.first_name}! 🎉

Discover amazing events, book tickets easily, and never miss out on the best experiences in Kenya.

Start exploring events now!
Thank you for joining us!"""
    
    send_sms(phone, message)


def send_event_notification_sms(user, event, notification_type='reminder'):
    """Send event notification SMS"""
    if not user.phone_number:
        print(f"⚠️ No phone number for user {user.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(user.phone_number)
    
    if notification_type == 'reminder':
        message = f"""Event Reminder ⏰

{event.title}
Date: {event.start_date.strftime('%d/%m/%Y %I:%M %p')}
Venue: {event.venue_name or event.venue_address or 'Online'}

Don't forget! See you there!"""
    elif notification_type == 'approved':
        message = f"""Event Approved! 🎉

{event.title} is now live!

Date: {event.start_date.strftime('%d/%m/%Y %I:%M %p')}
Book your tickets now!"""
    else:
        message = f"""Event Update 📢

{event.title}
{event.start_date.strftime('%d/%m/%Y %I:%M %p')}
Check it out!"""
    
    send_sms(phone, message)


def send_partner_approval_sms(partner):
    """Send partner approval SMS"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Congratulations! 🎉

Your partner account for {partner.business_name} has been approved!

You can now start creating events and reach thousands of attendees.

Login to your dashboard to get started!"""
    
    send_sms(phone, message)


def send_event_approval_sms(partner, event):
    """Send event approval SMS to partner"""
    print(f"📱 send_event_approval_sms called for partner {partner.id}, event {event.id}")
    
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id} ({partner.business_name}), skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    print(f"📱 Formatted phone number: {phone} (original: {partner.phone_number})")
    
    message = f"""Event Approved! ✅

{event.title} is now live!

Your event has been approved and is visible to all users.
Start promoting it to maximize attendance!"""
    
    print(f"📱 Sending SMS to {phone}...")
    send_sms(phone, message)
    print(f"📱 SMS queued for {phone}")


def send_event_rejection_sms(partner, event, reason):
    """Send event rejection SMS to partner"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Event Update 📝

{event.title} needs revision.

Reason: {reason}

Please review and resubmit your event.
Thank you!"""
    
    send_sms(phone, message)


def send_partner_rejection_sms(partner, reason):
    """Send partner rejection SMS"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Application Update 📝

Your partner application for {partner.business_name} needs revision.

Reason: {reason}

Please contact support if you have questions.
Thank you!"""
    
    send_sms(phone, message)


def send_partner_welcome_sms(partner):
    """Send welcome SMS to new partner"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Welcome to Niko Free, {partner.business_name}! 🎉

Your partner application has been received and is under review.

You will receive an email within 24 hours with your login credentials if approved.

Thank you for choosing Niko Free!"""
    
    send_sms(phone, message)


def send_new_booking_sms_to_partner(partner, booking, event):
    """Send SMS to partner when someone books their event"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""New Booking! 🎟️

{event.title}

New booking received:
- Booking: {booking.booking_number}
- Tickets: {booking.quantity}
- Amount: KES {booking.total_amount:,.2f}
- Customer: {booking.user.first_name} {booking.user.last_name}

Check your dashboard for details!"""
    
    send_sms(phone, message)


def send_password_reset_sms(user, reset_token):
    """Send password reset SMS with token"""
    if not user.phone_number:
        print(f"⚠️ No phone number for user {user.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(user.phone_number)
    
    message = f"""Password Reset Request 🔐

Hi {user.first_name},

Your password reset code is: {reset_token}

This code expires in 1 hour.
If you didn't request this, please ignore this message.

Niko Free"""
    
    send_sms(phone, message)


def send_payment_failed_sms(user, payment, event):
    """Send SMS when payment fails"""
    if not user.phone_number:
        print(f"⚠️ No phone number for user {user.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(user.phone_number)
    
    message = f"""Payment Failed ❌

Event: {event.title}
Amount: KES {payment.amount:,.2f}
Transaction: {payment.transaction_id}

Your payment could not be processed.
Please try again or contact support.

Niko Free"""
    
    send_sms(phone, message)


def send_partner_suspension_sms(partner, reason=None):
    """Send SMS when partner is suspended"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    reason_text = f"\nReason: {reason}" if reason else ""
    
    message = f"""Account Suspended ⚠️

{partner.business_name}

Your partner account has been suspended.{reason_text}

Please contact support for assistance.

Niko Free"""
    
    send_sms(phone, message)


def send_partner_activation_sms(partner):
    """Send SMS when partner is activated/unsuspended"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Account Reactivated! ✅

{partner.business_name}

Your partner account has been reactivated.
You can now access your dashboard and create events.

Welcome back to Niko Free!"""
    
    send_sms(phone, message)


def send_payout_approval_sms(partner, payout):
    """Send SMS when payout is approved"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Payout Approved! 💰

{partner.business_name}

Your payout request has been approved:
- Amount: KES {payout.amount:,.2f}
- Reference: {payout.reference_number}
- Method: {payout.payout_method.upper()}

Funds will be processed shortly.
Check your account for confirmation.

Niko Free"""
    
    send_sms(phone, message)


def send_booking_cancellation_sms(user, booking, event):
    """Send SMS when booking is cancelled"""
    if not user.phone_number:
        print(f"⚠️ No phone number for user {user.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(user.phone_number)
    
    message = f"""Booking Cancelled 📝

Event: {event.title}
Booking: {booking.booking_number}
Tickets: {booking.quantity}

Your booking has been cancelled.

Explore other exciting events on Niko Free!

Thank you for using Niko Free!"""
    
    send_sms(phone, message)


def send_booking_cancellation_to_partner_sms(partner, booking, event):
    """Send SMS to partner when a booking is cancelled"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Booking Cancelled 📝

{event.title}

A booking has been cancelled:
- Booking: {booking.booking_number}
- Tickets: {booking.quantity}
- Customer: {booking.user.first_name} {booking.user.last_name}

Check your dashboard for details.

Niko Free"""
    
    send_sms(phone, message)


def send_promotion_payment_success_sms(partner, event):
    """Send SMS when promotion payment is successful"""
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Promotion Active! ✨

{event.title}

Your event promotion payment was successful!
Your event is now featured in the "Can't Miss" section.

Start promoting to maximize attendance!

Niko Free"""
    
    send_sms(phone, message)

