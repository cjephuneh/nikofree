#!/usr/bin/env python3
"""
Production Email Test Script
Run this on your production server to test email functionality
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test email configuration"""
    print("=" * 60)
    print("Production Email Configuration Test")
    print("=" * 60)
    print()
    
    # Check configuration
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = os.getenv('MAIL_PORT')
    mail_use_ssl = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_suppress = os.getenv('MAIL_SUPPRESS_SEND', 'False') == 'True'
    
    print("📧 Email Configuration:")
    print(f"   Server: {mail_server}")
    print(f"   Port: {mail_port}")
    print(f"   SSL: {mail_use_ssl}")
    print(f"   Username: {mail_username}")
    print(f"   Password: {'*' * len(mail_password) if mail_password else 'NOT SET'}")
    print(f"   Suppress Send: {mail_suppress}")
    print()
    
    # Check if suppression is enabled
    if mail_suppress:
        print("⚠️  WARNING: MAIL_SUPPRESS_SEND=True")
        print("   → Emails are suppressed and will NOT be sent")
        print("   → Set MAIL_SUPPRESS_SEND=False for production")
        print()
        return False
    
    # Test SMTP connection
    print("🔍 Testing SMTP Connection...")
    print()
    
    try:
        import smtplib
        import socket
        
        # Test DNS
        print("1. Testing DNS resolution...")
        ip = socket.gethostbyname(mail_server)
        print(f"   ✅ DNS resolved: {mail_server} -> {ip}")
        print()
        
        # Test port
        print("2. Testing port connectivity...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((mail_server, int(mail_port)))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Port {mail_port} is open and reachable")
        else:
            print(f"   ❌ Port {mail_port} is closed or unreachable")
            return False
        print()
        
        # Test SMTP connection
        print("3. Testing SMTP connection...")
        if mail_use_ssl:
            smtp = smtplib.SMTP_SSL(mail_server, int(mail_port), timeout=10)
        else:
            smtp = smtplib.SMTP(mail_server, int(mail_port), timeout=10)
            if os.getenv('MAIL_USE_TLS', 'False') == 'True':
                smtp.starttls()
        
        print("   ✅ SMTP connection established")
        print()
        
        # Test authentication
        if mail_username and mail_password:
            print("4. Testing authentication...")
            smtp.login(mail_username, mail_password)
            print("   ✅ Authentication successful")
            print()
        
        smtp.quit()
        
        print("=" * 60)
        print("✅ All tests passed! Email configuration is correct.")
        print("=" * 60)
        print()
        print("📝 Next steps:")
        print("   1. Test sending an actual email using Flask shell:")
        print("      flask shell")
        print("      >>> from app.utils.email import send_email")
        print("      >>> send_email('Test', 'your@email.com', '<h1>Test</h1>')")
        print()
        print("   2. Monitor logs for email activity:")
        print("      tail -f /var/log/nikofree/out.log")
        print()
        
        return True
        
    except socket.timeout:
        print("   ❌ Connection timeout")
        print("   💡 Check firewall rules and network connectivity")
        return False
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print("   💡 Check username and password in .env file")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   💡 Error type: {type(e).__name__}")
        return False

def send_test_email():
    """Send a test email (optional)"""
    recipient = input("\nEnter email address to send test email (or press Enter to skip): ").strip()
    
    if not recipient:
        print("Skipping test email send.")
        return
    
    print(f"\n📧 Sending test email to {recipient}...")
    
    try:
        # Import Flask app
        from app import create_app
        app = create_app('production')
        
        with app.app_context():
            from app.utils.email import send_email
            
            send_email(
                subject="Production Email Test - Niko Free",
                recipient=recipient,
                html_body="""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h1 style="color: #27aae2;">✅ Email Test Successful!</h1>
                    <p>If you're reading this, emails are working correctly on your production server.</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        Server: Production<br>
                        Time: """ + str(__import__('datetime').datetime.now()) + """
                    </p>
                </body>
                </html>
                """
            )
            
            print("✅ Test email sent! Check your inbox.")
            print("   (Note: Email is sent asynchronously, check logs for confirmation)")
            
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        print("   Make sure Flask app is properly configured")

if __name__ == '__main__':
    success = test_email_config()
    
    if success:
        send_test = input("\nWould you like to send a test email? (y/n): ").strip().lower()
        if send_test == 'y':
            send_test_email()
    
    sys.exit(0 if success else 1)

