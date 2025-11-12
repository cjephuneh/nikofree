from flask import current_app, render_template_string
from flask_mail import Message
from app import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {str(e)}")


def send_email(subject, recipient, html_body, text_body=None):
    """Send email"""
    msg = Message(
        subject=subject,
        recipients=[recipient] if isinstance(recipient, str) else recipient,
        html=html_body,
        body=text_body or html_body
    )
    
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()


def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = "Welcome to Niko Free!"
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Welcome to Niko Free, {user.first_name}! 🎉</h2>
                <p>Thank you for joining Niko Free - your gateway to amazing events in Kenya!</p>
                <p>With Niko Free, you can:</p>
                <ul>
                    <li>Discover exciting events near you</li>
                    <li>Book tickets easily and securely</li>
                    <li>Save events to your bucketlist</li>
                    <li>Get digital tickets with QR codes</li>
                </ul>
                <p>Start exploring events now!</p>
                <a href="{current_app.config.get('FRONTEND_URL')}/events" 
                   style="display: inline-block; padding: 12px 30px; background-color: #4CAF50; 
                          color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                    Browse Events
                </a>
                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    If you have any questions, feel free to contact us.
                </p>
            </div>
        </body>
    </html>
    """
    send_email(subject, user.email, html_body)


def send_booking_confirmation_email(booking, tickets):
    """Send booking confirmation email"""
    user = booking.user
    event = booking.event
    
    subject = f"Booking Confirmed: {event.title}"
    
    tickets_html = ""
    for ticket in tickets:
        tickets_html += f"""
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <p><strong>Ticket #{ticket.ticket_number}</strong></p>
            <p>Type: {ticket.ticket_type.name}</p>
            <img src="{ticket.qr_code}" alt="QR Code" style="max-width: 200px;">
        </div>
        """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Booking Confirmed! 🎉</h2>
                <p>Hi {user.first_name},</p>
                <p>Your booking for <strong>{event.title}</strong> has been confirmed!</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Event Details</h3>
                    <p><strong>Event:</strong> {event.title}</p>
                    <p><strong>Date:</strong> {event.start_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Venue:</strong> {event.venue_name or event.venue_address}</p>
                    <p><strong>Booking Number:</strong> {booking.booking_number}</p>
                    <p><strong>Total Amount:</strong> KES {booking.total_amount}</p>
                </div>
                
                <h3>Your Tickets</h3>
                {tickets_html}
                
                <p style="margin-top: 30px;">
                    Please present your QR code at the event entrance for check-in.
                </p>
                
                <a href="{current_app.config.get('FRONTEND_URL')}/bookings/{booking.id}" 
                   style="display: inline-block; padding: 12px 30px; background-color: #4CAF50; 
                          color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                    View Booking Details
                </a>
            </div>
        </body>
    </html>
    """
    send_email(subject, user.email, html_body)


def send_partner_approval_email(partner, approved=True):
    """Send partner approval/rejection email"""
    if approved:
        subject = "Your Partner Account Has Been Approved! 🎉"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50;">Congratulations! Your Account is Approved</h2>
                    <p>Hi {partner.business_name},</p>
                    <p>Great news! Your partner account has been approved and you can now start creating events.</p>
                    
                    <a href="{current_app.config.get('FRONTEND_URL')}/partner/dashboard" 
                       style="display: inline-block; padding: 12px 30px; background-color: #4CAF50; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                        Go to Dashboard
                    </a>
                    
                    <p style="margin-top: 30px;">
                        Start creating your first event and reach thousands of potential attendees!
                    </p>
                </div>
            </body>
        </html>
        """
    else:
        subject = "Partner Application Update"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Partner Application Update</h2>
                    <p>Hi {partner.business_name},</p>
                    <p>Thank you for your interest in becoming a partner with Niko Free.</p>
                    <p>Unfortunately, we are unable to approve your application at this time.</p>
                    <p><strong>Reason:</strong> {partner.rejection_reason}</p>
                    <p>If you have any questions, please contact our support team.</p>
                </div>
            </body>
        </html>
        """
    
    send_email(subject, partner.email, html_body)


def send_event_approval_email(event, approved=True):
    """Send event approval/rejection email"""
    partner = event.organizer
    
    if approved:
        subject = f"Event Approved: {event.title}"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50;">Your Event Has Been Approved! 🎉</h2>
                    <p>Hi {partner.business_name},</p>
                    <p>Your event <strong>{event.title}</strong> has been approved and is now live!</p>
                    
                    <a href="{current_app.config.get('FRONTEND_URL')}/events/{event.id}" 
                       style="display: inline-block; padding: 12px 30px; background-color: #4CAF50; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                        View Event
                    </a>
                </div>
            </body>
        </html>
        """
    else:
        subject = f"Event Update: {event.title}"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Event Update</h2>
                    <p>Hi {partner.business_name},</p>
                    <p>Your event <strong>{event.title}</strong> could not be approved.</p>
                    <p><strong>Reason:</strong> {event.rejection_reason}</p>
                    <p>Please review and resubmit your event with the necessary changes.</p>
                </div>
            </body>
        </html>
        """
    
    send_email(subject, partner.email, html_body)

