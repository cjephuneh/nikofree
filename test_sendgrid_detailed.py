#!/usr/bin/env python3
"""
Detailed SendGrid Email Test with Error Handling
This script tests the SendGrid email setup with detailed error reporting.
"""

import os
import sys
import smtplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, mail
from flask_mail import Message

def test_smtp_connection():
    """Test SMTP connection directly"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 60)
        print("SendGrid SMTP Connection Test")
        print("=" * 60)
        
        mail_server = app.config.get('MAIL_SERVER')
        mail_port = app.config.get('MAIL_PORT', 587)
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')
        use_tls = app.config.get('MAIL_USE_TLS', False)
        use_ssl = app.config.get('MAIL_USE_SSL', False)
        timeout = app.config.get('MAIL_TIMEOUT', 30)
        
        print(f"\n📋 Configuration:")
        print(f"  Server: {mail_server}")
        print(f"  Port: {mail_port}")
        print(f"  Username: {mail_username}")
        print(f"  Password: {'*' * 20 if mail_password else 'NOT SET'}")
        print(f"  Use TLS: {use_tls}")
        print(f"  Use SSL: {use_ssl}")
        print(f"  Timeout: {timeout}s")
        
        if not mail_password:
            print("\n❌ ERROR: MAIL_PASSWORD is not set!")
            return False
        
        print(f"\n🔌 Testing SMTP connection to {mail_server}:{mail_port}...")
        
        try:
            if use_ssl:
                print("   Using SSL connection...")
                smtp = smtplib.SMTP_SSL(mail_server, mail_port, timeout=timeout)
            else:
                print("   Using TLS connection...")
                smtp = smtplib.SMTP(mail_server, mail_port, timeout=timeout)
                if use_tls:
                    print("   Starting TLS...")
                    smtp.starttls()
            
            print("   Authenticating...")
            smtp.login(mail_username, mail_password)
            print("   ✅ SMTP connection successful!")
            
            smtp.quit()
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"\n❌ Authentication failed!")
            print(f"   Error: {str(e)}")
            print(f"\n🔍 Troubleshooting:")
            print(f"   1. Check that MAIL_USERNAME is exactly 'apikey'")
            print(f"   2. Verify your SendGrid API key is correct")
            print(f"   3. Make sure the API key has 'Mail Send' permissions")
            return False
        except smtplib.SMTPException as e:
            print(f"\n❌ SMTP error: {str(e)}")
            return False
        except Exception as e:
            print(f"\n❌ Connection error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False

def test_email_sending():
    """Test email sending with Flask-Mail (synchronously)"""
    app = create_app('development')
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("SendGrid Email Sending Test (Synchronous)")
        print("=" * 60)
        
        if app.config.get('MAIL_SUPPRESS_SEND', False):
            print("\n⚠️  WARNING: MAIL_SUPPRESS_SEND is True - emails will not be sent!")
            return
        
        recipient = input("\n📧 Enter recipient email address: ").strip()
        if not recipient:
            print("❌ Recipient email is required")
            return
        
        sender = app.config.get('MAIL_DEFAULT_SENDER')
        print(f"\n📤 Sending test email:")
        print(f"   From: {sender}")
        print(f"   To: {recipient}")
        print(f"   Server: {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')}")
        
        try:
            msg = Message(
                subject="SendGrid Test Email - Niko Free",
                recipients=[recipient],
                sender=sender,
                html="""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #27aae2;">✅ SendGrid Email Test</h2>
                            <p>If you're reading this, your SendGrid configuration is working correctly.</p>
                            <p>This is a test email from the Niko Free application.</p>
                        </div>
                    </body>
                </html>
                """,
                body="SendGrid Email Test - If you're reading this, your SendGrid configuration is working correctly."
            )
            
            # Send synchronously (not async) to catch errors immediately
            print("\n   Attempting to send (synchronously)...")
            mail.send(msg)
            print("\n✅ Email sent successfully!")
            print(f"   Check your inbox at {recipient}")
            print("   (Also check spam/junk folder)")
            print("\n💡 Check SendGrid dashboard for delivery status")
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"\n❌ Authentication failed!")
            print(f"   Error: {str(e)}")
            print(f"\n🔍 This usually means:")
            print(f"   - MAIL_USERNAME should be exactly 'apikey' (not your email)")
            print(f"   - MAIL_PASSWORD should be your SendGrid API key (not your password)")
            print(f"   - API key might not have 'Mail Send' permissions")
            print(f"   - API key might be expired or revoked")
            import traceback
            traceback.print_exc()
        except smtplib.SMTPRecipientsRefused as e:
            print(f"\n❌ Recipient email rejected!")
            print(f"   Error: {str(e)}")
            print(f"   Check that the email address is valid")
        except smtplib.SMTPSenderRefused as e:
            print(f"\n❌ Sender email rejected!")
            print(f"   Error: {str(e)}")
            print(f"   Make sure '{sender}' is verified in SendGrid dashboard")
            print(f"   Go to Settings → Sender Authentication → Verify a Single Sender")
        except smtplib.SMTPException as e:
            print(f"\n❌ SMTP error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"\n❌ Error sending email: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    # First test SMTP connection
    connection_ok = test_smtp_connection()
    
    if connection_ok:
        # If connection works, test email sending
        test_email_sending()
    else:
        print("\n⚠️  Fix SMTP connection issues before testing email sending")

