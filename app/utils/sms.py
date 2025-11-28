"""
SMS Utility using Celcom Africa API
"""
import requests
from flask import current_app
from threading import Thread


# Celcom Africa SMS API Configuration
CELCOM_SMS_URL = "https://isms.celcomafrica.com/api/services/sendsms"
CELCOM_API_KEY = "b4e69853162316c2db235c8a444eb265"
CELCOM_PARTNER_ID = "36"
CELCOM_SHORTCODE = "TEXTME"


def send_sms_async(app, phone_number, message):
    """Send SMS asynchronously"""
    with app.app_context():
        try:
            # Check if SMS sending is suppressed (for development)
            if app.config.get('SMS_SUPPRESS_SEND', False):
                print(f"📱 [DEV MODE] SMS suppressed: {message[:50]}... to {phone_number}")
                return
            
            # Prepare payload
            payload = {
                "apikey": CELCOM_API_KEY,
                "partnerID": CELCOM_PARTNER_ID,
                "message": message,
                "shortcode": CELCOM_SHORTCODE,
                "mobile": phone_number
            }
            
            # Send request
            response = requests.post(CELCOM_SMS_URL, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') or result.get('status') == 'success' or result.get('responseCode') == '0':
                    print(f"✅ SMS sent successfully to {phone_number}")
                else:
                    print(f"❌ SMS failed: {result}")
            else:
                print(f"❌ SMS API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error sending SMS: {str(e)}")


def send_sms(phone_number, message):
    """Send SMS (async and non-blocking)"""
    try:
        from flask import current_app
        app = current_app._get_current_object()
        
        # Start thread and don't wait for it
        thread = Thread(target=send_sms_async, args=(app, phone_number, message))
        thread.daemon = True  # Daemon thread won't block app shutdown
        thread.start()
        
    except Exception as e:
        # Don't let SMS errors crash the app
        print(f"❌ Error queuing SMS: {str(e)}")


def format_phone_for_sms(phone_number):
    """Format phone number for SMS (ensure it starts with country code)"""
    # Remove any spaces, dashes, or other characters
    phone = ''.join(filter(str.isdigit, phone_number))
    
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
    
    return phone


def send_booking_confirmation_sms(booking, tickets):
    """Send booking confirmation SMS"""
    user = booking.user
    event = booking.event
    
    # Format phone number
    phone = format_phone_for_sms(user.phone_number) if user.phone_number else None
    
    if not phone:
        print(f"⚠️ No phone number for user {user.id}, skipping SMS")
        return
    
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

Present QR code at entrance.
Thank you for using Niko Free!"""
    
    send_sms(phone, message)


def send_payment_confirmation_sms(booking, payment):
    """Send payment confirmation SMS"""
    user = booking.user
    event = booking.event
    
    # Format phone number
    phone = format_phone_for_sms(payment.phone_number) if payment.phone_number else None
    
    if not phone:
        # Try user's phone number
        phone = format_phone_for_sms(user.phone_number) if user.phone_number else None
    
    if not phone:
        print(f"⚠️ No phone number for payment {payment.id}, skipping SMS")
        return
    
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
    if not partner.phone_number:
        print(f"⚠️ No phone number for partner {partner.id}, skipping SMS")
        return
    
    phone = format_phone_for_sms(partner.phone_number)
    
    message = f"""Event Approved! ✅

{event.title} is now live!

Your event has been approved and is visible to all users.
Start promoting it to maximize attendance!"""
    
    send_sms(phone, message)


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
Refund will be processed if payment was made.

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

