from flask import current_app, render_template_string
from flask_mail import Message
from app import mail
from threading import Thread
from datetime import datetime
import socket
import smtplib


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            # Check if email sending is suppressed (for development)
            if app.config.get('MAIL_SUPPRESS_SEND', False):
                print(f"📧 [DEV MODE] Email suppressed: {msg.subject} to {msg.recipients}")
                return
            
            # Get SMTP connection with timeout
            mail_server = app.config.get('MAIL_SERVER')
            mail_port = app.config.get('MAIL_PORT', 587)
            mail_timeout = app.config.get('MAIL_TIMEOUT', 30)  # Increased for SendGrid
            
            print(f"📧 [EMAIL] Attempting to send email to {msg.recipients}")
            print(f"📧 [EMAIL] SMTP Server: {mail_server}:{mail_port}, Timeout: {mail_timeout}s")
            
            # Send email with explicit timeout handling
            mail.send(msg)
            print(f"✅ Email sent successfully: {msg.subject} to {msg.recipients}")
        except (socket.timeout, TimeoutError) as e:
            error_msg = f"❌ Email timeout error: {str(e)}. SMTP server {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')} is not responding (likely blocked by firewall)."
            print(error_msg)
            if hasattr(app, 'logger'):
                app.logger.error(error_msg)
        except (ConnectionError, ConnectionRefusedError, OSError) as e:
            error_msg = f"❌ Email connection error: {str(e)}. Cannot connect to SMTP server {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')}."
            print(error_msg)
            if hasattr(app, 'logger'):
                app.logger.error(error_msg)
        except smtplib.SMTPException as e:
            error_msg = f"❌ SMTP error: {str(e)} (Type: {type(e).__name__})"
            print(error_msg)
            if hasattr(app, 'logger'):
                app.logger.error(error_msg)
        except Exception as e:
            error_msg = f"❌ Error sending email: {str(e)} (Type: {type(e).__name__})"
            print(error_msg)
            import traceback
            traceback.print_exc()
            if hasattr(app, 'logger'):
                app.logger.error(error_msg, exc_info=True)


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
                    ⚠️ <strong>Important:</strong> Please change this password immediately after your first login for security. 
                    You can change it in your Profile section after logging in.
                </p>
            </div>
            """
        
        base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
        frontend_url = current_app.config.get('FRONTEND_URL', base_url)
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">🎉 Congratulations!</h1>
                    <p style="color: #ffffff; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Your Partner Account is Approved</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{partner.business_name}</strong>,</p>
                    <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">Great news! Your partner account has been approved and you can now start creating events on Niko Free.</p>
                    
                    {credentials_html}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{frontend_url}/partner/login" 
                           style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                                  color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(39, 170, 226, 0.3);">
                            🚀 Login to Dashboard
                        </a>
                    </div>
                    
                    <div style="background-color: #f8f9fa; border-left: 4px solid #27aae2; padding: 20px; margin: 30px 0; border-radius: 4px;">
                        <h3 style="margin: 0 0 15px 0; color: #27aae2; font-size: 18px;">📋 Next Steps:</h3>
                        <ol style="margin: 0; padding-left: 20px; color: #555;">
                            <li style="margin-bottom: 10px;">Login using the credentials above</li>
                            <li style="margin-bottom: 10px;">Go to <strong>Profile</strong> section and change your password</li>
                            <li style="margin-bottom: 10px;">Create your first event and start reaching thousands of attendees!</li>
                        </ol>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 25px; border-radius: 8px; margin: 30px 0;">
                        <h3 style="margin: 0 0 15px 0; color: #1e8bb8; font-size: 18px;">✨ Benefits of Niko Free</h3>
                        <ul style="margin: 0; padding-left: 20px; color: #555;">
                            <li style="margin-bottom: 8px;">📈 Reach over 2 Million potential attendees</li>
                            <li style="margin-bottom: 8px;">🔔 Instant notifications on bookings and RSVPs</li>
                            <li style="margin-bottom: 8px;">📊 Real-time analytics and attendance tracking</li>
                            <li style="margin-bottom: 8px;">🎫 Set attendee limits or unlimited tickets</li>
                            <li style="margin-bottom: 8px;">💰 Easy earnings withdrawal via M-Pesa</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid #e5e5e5;">
                        <p style="font-size: 14px; color: #999; margin: 0;">
                            Need help? Contact us at <a href="mailto:support@niko-free.com" style="color: #27aae2;">support@niko-free.com</a>
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                    <p style="font-size: 12px; color: #999; margin: 0;">
                        © {datetime.now().year} Niko Free. All rights reserved.
                    </p>
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


def send_payment_confirmation_email(booking, payment, tickets):
    """Send payment confirmation email to user"""
    user = booking.user
    event = booking.event
    
    subject = f"Payment Confirmed: {event.title}"
    
    tickets_html = ""
    for ticket in tickets:
        qr_url = ticket.qr_code if ticket.qr_code else ""
        tickets_html += f"""
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; background-color: #f9f9f9;">
            <p><strong>Ticket #{ticket.ticket_number}</strong></p>
            <p>Type: {ticket.ticket_type.name if ticket.ticket_type else 'General Admission'}</p>
            {f'<img src="{qr_url}" alt="QR Code" style="max-width: 200px; margin-top: 10px;">' if qr_url else ''}
        </div>
        """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Payment Confirmed! ✅</h2>
                <p>Hi {user.first_name},</p>
                <p>Your payment for <strong>{event.title}</strong> has been successfully processed!</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Payment Details</h3>
                    <p><strong>Transaction ID:</strong> {payment.transaction_id}</p>
                    <p><strong>MPesa Receipt:</strong> {payment.mpesa_receipt_number or 'Processing...'}</p>
                    <p><strong>Amount Paid:</strong> KES {payment.amount:,.2f}</p>
                    <p><strong>Payment Date:</strong> {payment.completed_at.strftime('%B %d, %Y at %I:%M %p') if payment.completed_at else 'N/A'}</p>
                </div>
                
                <div style="background-color: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Event Details</h3>
                    <p><strong>Event:</strong> {event.title}</p>
                    <p><strong>Date:</strong> {event.start_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Venue:</strong> {event.venue_name or event.venue_address or 'Online'}</p>
                    <p><strong>Booking Number:</strong> {booking.booking_number}</p>
                    <p><strong>Quantity:</strong> {booking.quantity} ticket(s)</p>
                </div>
                
                <h3>Your Tickets</h3>
                {tickets_html}
                
                <p style="margin-top: 30px;">
                    <strong>📱 Important:</strong> Please present your QR code at the event entrance for check-in.
                </p>
                
                <a href="{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/bookings/{booking.id}" 
                   style="display: inline-block; padding: 12px 30px; background-color: #4CAF50; 
                          color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                    View Booking Details
                </a>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="font-size: 14px; color: #666;">
                        If you have any questions or concerns, please contact our support team.
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


def send_booking_cancellation_email(user, booking, event):
    """Send booking cancellation email to user"""
    subject = f"Booking Cancelled: {event.title}"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">📝 Booking Cancelled</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{user.first_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">Your booking for <strong>{event.title}</strong> has been cancelled.</p>
                
                <div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 20px; margin: 30px 0; border-radius: 4px;">
                    <h3 style="margin: 0 0 15px 0; color: #e65100; font-size: 18px;">📋 Booking Details</h3>
                    <p style="margin: 5px 0;"><strong>Booking Number:</strong> {booking.booking_number}</p>
                    <p style="margin: 5px 0;"><strong>Event:</strong> {event.title}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {event.start_date.strftime('%B %d, %Y at %I:%M %p') if event.start_date else 'N/A'}</p>
                    <p style="margin: 5px 0;"><strong>Quantity:</strong> {booking.quantity} ticket(s)</p>
                    <p style="margin: 5px 0;"><strong>Amount:</strong> KES {booking.total_amount:,.2f}</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        💡 <strong>Note:</strong> If you paid for this booking, a refund will be processed according to our refund policy. 
                        You'll receive a notification once the refund is complete.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/bookings" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        View My Bookings
                    </a>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid #e5e5e5;">
                    <p style="font-size: 14px; color: #999; margin: 0;">
                        Questions? Contact us at <a href="mailto:support@niko-free.com" style="color: #27aae2;">support@niko-free.com</a>
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, user.email, html_body)


def send_booking_cancellation_to_partner_email(partner, booking, event):
    """Send booking cancellation email to partner"""
    subject = f"Booking Cancelled: {event.title}"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">📝 Booking Cancelled</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{partner.business_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">A booking for your event <strong>{event.title}</strong> has been cancelled.</p>
                
                <div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 20px; margin: 30px 0; border-radius: 4px;">
                    <h3 style="margin: 0 0 15px 0; color: #e65100; font-size: 18px;">📋 Booking Details</h3>
                    <p style="margin: 5px 0;"><strong>Booking Number:</strong> {booking.booking_number}</p>
                    <p style="margin: 5px 0;"><strong>Customer:</strong> {booking.user.first_name} {booking.user.last_name}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {booking.user.email}</p>
                    <p style="margin: 5px 0;"><strong>Quantity:</strong> {booking.quantity} ticket(s)</p>
                    <p style="margin: 5px 0;"><strong>Amount:</strong> KES {booking.total_amount:,.2f}</p>
                    <p style="margin: 5px 0;"><strong>Cancelled At:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/partner/dashboard" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        View Dashboard
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, partner.email, html_body)


def send_payment_failed_email(user, payment, event):
    """Send payment failed email to user"""
    subject = f"Payment Failed: {event.title}"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    error_message = payment.error_message or "Payment could not be processed"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">❌ Payment Failed</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{user.first_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">Unfortunately, your payment for <strong>{event.title}</strong> could not be processed.</p>
                
                <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 20px; margin: 30px 0; border-radius: 4px;">
                    <h3 style="margin: 0 0 15px 0; color: #c62828; font-size: 18px;">⚠️ Payment Details</h3>
                    <p style="margin: 5px 0;"><strong>Event:</strong> {event.title}</p>
                    <p style="margin: 5px 0;"><strong>Amount:</strong> KES {payment.amount:,.2f}</p>
                    <p style="margin: 5px 0;"><strong>Transaction ID:</strong> {payment.transaction_id}</p>
                    <p style="margin: 5px 0;"><strong>Reason:</strong> {error_message}</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #333; font-size: 18px;">💡 What to do next:</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                        <li style="margin-bottom: 8px;">Check that you have sufficient funds in your M-Pesa account</li>
                        <li style="margin-bottom: 8px;">Ensure your phone number is correct and registered with M-Pesa</li>
                        <li style="margin-bottom: 8px;">Try making the payment again</li>
                        <li style="margin-bottom: 8px;">If the problem persists, contact our support team</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/events/{event.id}" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        Try Again
                    </a>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid #e5e5e5;">
                    <p style="font-size: 14px; color: #999; margin: 0;">
                        Need help? Contact us at <a href="mailto:support@niko-free.com" style="color: #27aae2;">support@niko-free.com</a>
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, user.email, html_body)


def send_event_reminder_email(user, event):
    """Send event reminder email to user"""
    subject = f"Reminder: {event.title} is Tomorrow!"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">⏰ Event Reminder</h1>
                <p style="color: #ffffff; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Don't miss out!</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{user.first_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">This is a friendly reminder that <strong>{event.title}</strong> is happening tomorrow!</p>
                
                <div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); padding: 25px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #7b1fa2; font-size: 18px;">📅 Event Details</h3>
                    <p style="margin: 8px 0; color: #555;"><strong>Event:</strong> {event.title}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Date:</strong> {event.start_date.strftime('%A, %B %d, %Y') if event.start_date else 'N/A'}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Time:</strong> {event.start_date.strftime('%I:%M %p') if event.start_date else 'N/A'}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Venue:</strong> {event.venue_name or event.venue_address or 'Online'}</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #333; font-size: 18px;">📱 Don't forget:</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                        <li style="margin-bottom: 8px;">Bring your ticket QR code (on your phone or printed)</li>
                        <li style="margin-bottom: 8px;">Arrive early to avoid queues</li>
                        <li style="margin-bottom: 8px;">Check your booking details for any special instructions</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/events/{event.id}" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        View Event Details
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, user.email, html_body)


def send_new_booking_to_partner_email(partner, booking, event):
    """Send new booking notification email to partner"""
    subject = f"New Booking: {event.title}"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">🎉 New Booking!</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{partner.business_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">You have received a new booking for your event <strong>{event.title}</strong>!</p>
                
                <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 25px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #2e7d32; font-size: 18px;">📋 Booking Details</h3>
                    <p style="margin: 8px 0; color: #555;"><strong>Booking Number:</strong> {booking.booking_number}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Customer:</strong> {booking.user.first_name} {booking.user.last_name}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Email:</strong> {booking.user.email}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Phone:</strong> {booking.user.phone_number or 'N/A'}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Quantity:</strong> {booking.quantity} ticket(s)</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Total Amount:</strong> KES {booking.total_amount:,.2f}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Payment Status:</strong> <span style="color: {'#4caf50' if booking.payment_status == 'paid' else '#ff9800'};">{booking.payment_status.upper()}</span></p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/partner/dashboard" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        View Dashboard
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, partner.email, html_body)


def send_payout_approval_email(partner, payout):
    """Send payout approval email to partner"""
    subject = f"Payout Approved: KES {payout.amount:,.2f}"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">💰 Payout Approved!</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{partner.business_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">Great news! Your payout request has been approved and is being processed.</p>
                
                <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 25px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #2e7d32; font-size: 18px;">💵 Payout Details</h3>
                    <p style="margin: 8px 0; color: #555;"><strong>Reference Number:</strong> {payout.reference_number}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Amount:</strong> KES {payout.amount:,.2f}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Method:</strong> {payout.payout_method.replace('_', ' ').title()}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Account:</strong> {payout.account_number}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Status:</strong> <span style="color: #4caf50;">{payout.status.upper()}</span></p>
                    <p style="margin: 8px 0; color: #555;"><strong>Processed At:</strong> {payout.processed_at.strftime('%B %d, %Y at %I:%M %p') if payout.processed_at else 'Processing...'}</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        💡 <strong>Note:</strong> If you selected M-Pesa, the funds will be sent to your registered phone number within 24-48 hours. 
                        For bank transfers, processing may take 3-5 business days.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/partner/dashboard" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        View Dashboard
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, partner.email, html_body)


def send_partner_suspension_email(partner, reason):
    """Send partner suspension email"""
    subject = "Account Suspension Notice"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">⚠️ Account Suspended</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{partner.business_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">We regret to inform you that your partner account has been suspended.</p>
                
                <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 20px; margin: 30px 0; border-radius: 4px;">
                    <h3 style="margin: 0 0 15px 0; color: #c62828; font-size: 18px;">📋 Suspension Details</h3>
                    <p style="margin: 5px 0;"><strong>Reason:</strong> {reason}</p>
                    <p style="margin: 5px 0;"><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        During the suspension period, you will not be able to create new events or receive new bookings. 
                        If you believe this is an error or have questions, please contact our support team.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid #e5e5e5;">
                    <p style="font-size: 14px; color: #999; margin: 0;">
                        Contact us at <a href="mailto:support@niko-free.com" style="color: #27aae2;">support@niko-free.com</a>
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, partner.email, html_body)


def send_partner_activation_email(partner):
    """Send partner activation email"""
    subject = "Account Reactivated - Welcome Back!"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">✅ Account Reactivated</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{partner.business_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">Great news! Your partner account has been reactivated and you can now continue creating events.</p>
                
                <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 25px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #2e7d32; font-size: 18px;">🎉 You can now:</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                        <li style="margin-bottom: 8px;">Create and manage events</li>
                        <li style="margin-bottom: 8px;">Receive new bookings</li>
                        <li style="margin-bottom: 8px;">Access your dashboard and analytics</li>
                        <li style="margin-bottom: 8px;">Request payouts</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/partner/dashboard" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        Go to Dashboard
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, partner.email, html_body)


def send_event_edit_notification_to_admin(partner, event, changed_fields):
    """Send email to admin when partner edits an event"""
    from flask import current_app
    admin_email = current_app.config.get('ADMIN_EMAIL')
    
    if not admin_email:
        return
    
    subject = f"Event Edited: {event.title}"
    
    # Format changed fields list
    if changed_fields:
        fields_text = ", ".join(changed_fields)
        changes_html = f"""
        <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; 
                    border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #856404;">📝 Fields Changed:</h3>
            <p style="color: #856404; margin: 0;">{fields_text}</p>
        </div>
        """
    else:
        changes_html = """
        <div style="background-color: #e3f2fd; border: 1px solid #2196f3; padding: 15px; 
                    border-radius: 5px; margin: 20px 0;">
            <p style="color: #1976d2; margin: 0;">Event was updated (no specific fields tracked)</p>
        </div>
        """
    
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">✏️ Event Edited</h1>
                <p style="color: #ffffff; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Partner has updated an event</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hello Admin,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">
                    Partner <strong>{partner.business_name}</strong> has edited the event <strong>"{event.title}"</strong>.
                </p>
                
                {changes_html}
                
                <div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #333; font-size: 18px;">📋 Event Information</h3>
                    <p style="margin: 8px 0; color: #555;"><strong>Event ID:</strong> {event.id}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Event Title:</strong> {event.title}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Partner:</strong> {partner.business_name}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Partner Email:</strong> {partner.email}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Status:</strong> <span style="color: {'#4caf50' if event.status == 'approved' else '#ff9800' if event.status == 'pending' else '#f44336'};">{event.status.upper()}</span></p>
                    <p style="margin: 8px 0; color: #555;"><strong>Event Date:</strong> {event.start_date.strftime('%B %d, %Y at %I:%M %p') if event.start_date else 'TBA'}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/admin/events/{event.id}" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        Review Event Details
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Please review the changes to ensure the event meets our platform standards.
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free Admin Dashboard. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, admin_email, html_body)


def send_promotion_payment_success_email(partner, event):
    """Send promotion payment success email to partner"""
    subject = f"Promotion Payment Successful: {event.title}"
    base_url = current_app.config.get('BASE_URL', 'https://niko-free.com')
    frontend_url = current_app.config.get('FRONTEND_URL', base_url)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 0;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">⭐ Promotion Active!</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">Hi <strong>{partner.business_name}</strong>,</p>
                <p style="font-size: 16px; color: #555; margin: 0 0 30px 0;">Your promotion payment for <strong>{event.title}</strong> has been successfully processed!</p>
                
                <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding: 25px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #e65100; font-size: 18px;">🎯 Your Event is Now Promoted</h3>
                    <p style="margin: 8px 0; color: #555;"><strong>Event:</strong> {event.title}</p>
                    <p style="margin: 8px 0; color: #555;"><strong>Status:</strong> <span style="color: #ff9800;">FEATURED IN "CAN'T MISS" SECTION</span></p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        ✨ Your event will now appear in the "Can't Miss" section, giving it maximum visibility to thousands of potential attendees!
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/events/{event.id}" 
                       style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #27aae2 0%, #1e8bb8 100%); 
                              color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        View Event
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e5e5;">
                <p style="font-size: 12px; color: #999; margin: 0;">
                    © {datetime.now().year} Niko Free. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(subject, partner.email, html_body)

