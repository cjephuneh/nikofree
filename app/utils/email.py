from flask import current_app, render_template_string
from flask_mail import Message
from app import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            # Check if email sending is suppressed (for development)
            if app.config.get('MAIL_SUPPRESS_SEND', False):
                print(f"📧 [DEV MODE] Email suppressed: {msg.subject} to {msg.recipients}")
                return
            
            mail.send(msg)
            print(f"✅ Email sent: {msg.subject} to {msg.recipients}")
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")


def send_email(subject, recipient, html_body, text_body=None):
    """Send email (async and non-blocking)"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient] if isinstance(recipient, str) else recipient,
            html=html_body,
            body=text_body or html_body
        )
        
        app = current_app._get_current_object()
        
        # Start thread and don't wait for it
        thread = Thread(target=send_async_email, args=(app, msg))
        thread.daemon = True  # Daemon thread won't block app shutdown
        thread.start()
    except Exception as e:
        # Don't let email errors crash the app
        print(f"❌ Error creating email: {str(e)}")


def send_password_reset_email(user, reset_token):
    """Send password reset email"""
    subject = "Reset Your Niko Free Password"
    reset_url = f"{current_app.config.get('FRONTEND_URL')}/reset-password?token={reset_token}"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #27aae2;">Reset Your Password</h2>
                <p>Hi {user.first_name},</p>
                <p>We received a request to reset your password for your Niko Free account.</p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; 
                            border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;">
                        <strong>⚠️ Security Notice:</strong> This link will expire in 1 hour.
                    </p>
                </div>
                
                <p>Click the button below to reset your password:</p>
                
                <a href="{reset_url}" 
                   style="display: inline-block; padding: 12px 30px; background-color: #27aae2; 
                          color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                    Reset Password
                </a>
                
                <p style="margin-top: 30px; font-size: 14px; color: #666;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{reset_url}" style="color: #27aae2; word-break: break-all;">{reset_url}</a>
                </p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="font-size: 14px; color: #666;">
                        <strong>Didn't request this?</strong><br>
                        If you didn't request a password reset, you can safely ignore this email. 
                        Your password will remain unchanged.
                    </p>
                </div>
                
                <p style="margin-top: 30px; font-size: 12px; color: #999;">
                    Best regards,<br>
                    The Niko Free Team
                </p>
            </div>
        </body>
    </html>
    """
    
    send_email(subject, user.email, html_body)


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


def send_partner_approval_email(partner, approved=True, temp_password=None):
    """Send partner approval/rejection email"""
    if approved:
        subject = "Your Partner Account Has Been Approved! 🎉"
        
        # Include credentials if provided
        credentials_html = ""
        if temp_password:
            credentials_html = f"""
            <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; 
                        border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #856404;">Your Login Credentials</h3>
                <p><strong>Email:</strong> {partner.email}</p>
                <p><strong>Temporary Password:</strong> <code style="background-color: #fff; 
                   padding: 5px 10px; border-radius: 3px; font-size: 16px;">{temp_password}</code></p>
                <p style="color: #856404; font-size: 14px; margin-top: 15px;">
                    ⚠️ Please change this password immediately after your first login for security.
                </p>
            </div>
            """
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50;">Congratulations! Your Account is Approved</h2>
                    <p>Hi {partner.business_name},</p>
                    <p>Great news! Your partner account has been approved and you can now start creating events.</p>
                    
                    {credentials_html}
                    
                    <a href="{current_app.config.get('FRONTEND_URL')}/partner/login" 
                       style="display: inline-block; padding: 12px 30px; background-color: #4CAF50; 
                              color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                        Login to Dashboard
                    </a>
                    
                    <p style="margin-top: 30px;">
                        Start creating your first event and reach thousands of potential attendees!
                    </p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                        <h3>Benefits of Niko Free</h3>
                        <ul>
                            <li>Over 2 Million Users visibility</li>
                            <li>Instant notifications on RSVPs</li>
                            <li>Know estimated event attendance</li>
                            <li>Set attendees limit or unlimited tickets</li>
                            <li>Comprehensive dashboard with analytics</li>
                        </ul>
                    </div>
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
                    
                    <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; 
                                padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>Reason:</strong> {partner.rejection_reason}</p>
                    </div>
                    
                    <p>If you believe this is an error or have any questions, please contact our support team.</p>
                    
                    <p style="margin-top: 30px;">
                        <strong>Email:</strong> support@nikofree.com<br>
                        <strong>Phone:</strong> +254 700 000 000
                    </p>
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

