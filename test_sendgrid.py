#!/usr/bin/env python3
"""
Test SendGrid Email Configuration
This script tests the SendGrid email setup by sending a test email.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db, mail

def test_sendgrid():
    """Test SendGrid email sending"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 60)
        print("SendGrid Email Test")
        print("=" * 60)
        
        # Check configuration
        print("\n📋 Email Configuration:")
        print(f"  Server: {app.config.get('MAIL_SERVER')}")
        print(f"  Port: {app.config.get('MAIL_PORT')}")
        print(f"  Use TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"  Use SSL: {app.config.get('MAIL_USE_SSL')}")
        print(f"  Username: {app.config.get('MAIL_USERNAME')}")
        print(f"  Password: {'*' * 20 if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
        print(f"  Default Sender: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print(f"  Suppress Send: {app.config.get('MAIL_SUPPRESS_SEND')}")
        print(f"  Timeout: {app.config.get('MAIL_TIMEOUT')}s")
        
        # Check if email sending is suppressed
        if app.config.get('MAIL_SUPPRESS_SEND', False):
            print("\n⚠️  WARNING: MAIL_SUPPRESS_SEND is True - emails will not be sent!")
            print("   Set MAIL_SUPPRESS_SEND=False in .env to enable email sending")
            return
        
        # Check if password is set
        if not app.config.get('MAIL_PASSWORD'):
            print("\n❌ ERROR: MAIL_PASSWORD is not set!")
            print("   Please set your SendGrid API key in .env file:")
            print("   MAIL_PASSWORD=your_sendgrid_api_key_here")
            return
        
        # Get recipient email
        recipient = input("\n📧 Enter recipient email address (or press Enter for default): ").strip()
        if not recipient:
            recipient = app.config.get('ADMIN_EMAIL', 'admin@nikofree.com')
            print(f"   Using default: {recipient}")
        
        # Send test email SYNCHRONOUSLY to catch errors
        print(f"\n📤 Sending test email to {recipient}...")
        print("   Please wait...")
        
        try:
            # Import Flask-Mail Message directly for synchronous sending
            from flask_mail import Message
            
            msg = Message(
                subject="SendGrid Test Email - Niko Free",
                recipients=[recipient],
                html="""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #27aae2;">✅ SendGrid Email Test Successful!</h2>
                            <p>If you're reading this, your SendGrid configuration is working correctly.</p>
                            
                            <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; 
                                        border-radius: 5px; margin: 20px 0;">
                                <p style="margin: 0; color: #155724;">
                                    <strong>✓ Email Configuration:</strong><br>
                                    Server: smtp.sendgrid.net<br>
                                    Port: 587 (TLS)<br>
                                    Status: Connected and working!
                                </p>
                            </div>
                            
                            <p>This is a test email from the Niko Free application.</p>
                            
                            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                                Sent via SendGrid SMTP API
                            </p>
                        </div>
                    </body>
                </html>
                """,
                body="SendGrid Email Test Successful! If you're reading this, your SendGrid configuration is working correctly."
            )
            
            # Send synchronously (not async) to catch errors immediately
            print("   Sending synchronously to catch any errors...")
            mail.send(msg)
            
            print("\n✅ Test email sent successfully!")
            print(f"   Check your inbox at {recipient}")
            print("   (Also check spam/junk folder if you don't see it)")
            print("\n💡 Tip: Check SendGrid dashboard for delivery statistics")
            
        except Exception as e:
            print(f"\n❌ Error sending email: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            print("\n🔍 Troubleshooting:")
            print("   1. Check that MAIL_USERNAME is exactly 'apikey'")
            print("   2. Check that MAIL_PASSWORD is your SendGrid API key (starts with SG.)")
            print("   3. Verify your sender email (noreply@niko-free.com) in SendGrid dashboard")
            print("   4. Make sure API key has 'Mail Send' permissions")
            print("   5. Check SendGrid account status and limits")

if __name__ == '__main__':
    test_sendgrid()

