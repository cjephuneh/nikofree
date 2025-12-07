#!/usr/bin/env python3
"""
Email Diagnostic Script
Run this to diagnose email issues
"""
import os
import sys
import socket
import smtplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_config():
    """Check email configuration"""
    print_section("1. Email Configuration Check")
    
    config = {
        'MAIL_SERVER': os.getenv('MAIL_SERVER'),
        'MAIL_PORT': os.getenv('MAIL_PORT', '465'),
        'MAIL_USE_SSL': os.getenv('MAIL_USE_SSL', 'True'),
        'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'False'),
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER'),
        'MAIL_SUPPRESS_SEND': os.getenv('MAIL_SUPPRESS_SEND', 'False'),
        'MAIL_TIMEOUT': os.getenv('MAIL_TIMEOUT', '10'),
    }
    
    issues = []
    
    print("\n📧 Current Configuration:")
    for key, value in config.items():
        if key == 'MAIL_PASSWORD':
            display = '*' * len(value) if value else 'NOT SET'
        else:
            display = value if value else 'NOT SET'
        print(f"   {key}: {display}")
        
        # Check for common issues
        if key == 'MAIL_SUPPRESS_SEND' and value == 'True':
            issues.append("❌ MAIL_SUPPRESS_SEND is True - emails are disabled!")
        if key == 'MAIL_SERVER' and not value:
            issues.append("❌ MAIL_SERVER is not set")
        if key == 'MAIL_USERNAME' and not value:
            issues.append("❌ MAIL_USERNAME is not set")
        if key == 'MAIL_PASSWORD' and not value:
            issues.append("❌ MAIL_PASSWORD is not set")
    
    if issues:
        print("\n⚠️  Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        return False, config
    else:
        print("\n✅ Configuration looks good!")
        return True, config

def test_dns(server):
    """Test DNS resolution"""
    print_section("2. DNS Resolution Test")
    
    try:
        ip = socket.gethostbyname(server)
        print(f"✅ DNS resolved: {server} -> {ip}")
        return True, ip
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False, None

def test_port(server, port):
    """Test port connectivity"""
    print_section("3. Port Connectivity Test")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((server, int(port)))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is open and reachable")
            return True
        else:
            print(f"❌ Port {port} is closed or unreachable")
            print(f"   Error code: {result}")
            return False
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        return False

def test_smtp_connection(config):
    """Test SMTP connection and authentication"""
    print_section("4. SMTP Connection & Authentication Test")
    
    server = config['MAIL_SERVER']
    port = int(config['MAIL_PORT'])
    use_ssl = config['MAIL_USE_SSL'] == 'True'
    use_tls = config['MAIL_USE_TLS'] == 'True'
    username = config['MAIL_USERNAME']
    password = config['MAIL_PASSWORD']
    timeout = int(config['MAIL_TIMEOUT'])
    
    try:
        print(f"Connecting to {server}:{port}...")
        
        if use_ssl:
            print("   Using SSL connection...")
            smtp = smtplib.SMTP_SSL(server, port, timeout=timeout)
        else:
            print("   Using plain connection...")
            smtp = smtplib.SMTP(server, port, timeout=timeout)
            if use_tls:
                print("   Starting TLS...")
                smtp.starttls()
        
        print("✅ SMTP connection established")
        
        if username and password:
            print("Authenticating...")
            smtp.login(username, password)
            print("✅ Authentication successful")
        else:
            print("⚠️  No credentials provided, skipping authentication")
        
        smtp.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("   💡 Check your username and password")
        return False
    except socket.timeout as e:
        print(f"❌ Connection timeout: {e}")
        print("   💡 Check firewall rules and network connectivity")
        return False
    except ConnectionRefusedError as e:
        print(f"❌ Connection refused: {e}")
        print("   💡 Check if SMTP server is running and port is correct")
        return False
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_email_send(config):
    """Test sending an actual email"""
    print_section("5. Test Email Send")
    
    recipient = input("Enter email address to send test email (or press Enter to skip): ").strip()
    
    if not recipient:
        print("Skipping test email send.")
        return True
    
    print(f"\n📧 Sending test email to {recipient}...")
    
    try:
        from app import create_app
        app = create_app(os.getenv('FLASK_ENV', 'production'))
        
        with app.app_context():
            from app.utils.email import send_email
            
            send_email(
                subject="Email Diagnostic Test - Niko Free",
                recipient=recipient,
                html_body="""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h1 style="color: #27aae2;">✅ Email Diagnostic Test</h1>
                    <p>If you're reading this, your email configuration is working correctly!</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        Server: Diagnostic Test<br>
                        Time: """ + str(__import__('datetime').datetime.now()) + """
                    </p>
                </body>
                </html>
                """
            )
            
            print("✅ Test email queued for sending!")
            print("   (Email is sent asynchronously - check logs for delivery status)")
            print("   (Check your inbox and spam folder)")
            return True
            
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("\n" + "=" * 60)
    print("  EMAIL DIAGNOSTIC TOOL")
    print("  Niko Free Email Configuration Checker")
    print("=" * 60)
    
    # Step 1: Check configuration
    config_ok, config = check_config()
    
    if not config_ok:
        print("\n⚠️  Please fix configuration issues before continuing.")
        response = input("\nContinue with tests anyway? (y/n): ").strip().lower()
        if response != 'y':
            sys.exit(1)
    
    # Check suppression
    if config['MAIL_SUPPRESS_SEND'] == 'True':
        print("\n⚠️  WARNING: MAIL_SUPPRESS_SEND=True")
        print("   Emails are suppressed and will NOT be sent!")
        print("   Set MAIL_SUPPRESS_SEND=False to enable email sending.")
        response = input("\nContinue with tests anyway? (y/n): ").strip().lower()
        if response != 'y':
            sys.exit(1)
    
    # Step 2: Test DNS
    server = config['MAIL_SERVER']
    if not server:
        print("\n❌ MAIL_SERVER not set. Cannot continue.")
        sys.exit(1)
    
    dns_ok, ip = test_dns(server)
    if not dns_ok:
        print("\n❌ DNS resolution failed. Cannot continue.")
        sys.exit(1)
    
    # Step 3: Test port
    port = config['MAIL_PORT']
    port_ok = test_port(server, port)
    if not port_ok:
        print("\n⚠️  Port connectivity failed.")
        print("   This might be a firewall issue.")
        response = input("\nContinue with SMTP test anyway? (y/n): ").strip().lower()
        if response != 'y':
            sys.exit(1)
    
    # Step 4: Test SMTP
    smtp_ok = test_smtp_connection(config)
    if not smtp_ok:
        print("\n❌ SMTP connection failed.")
        print("   Please check your SMTP settings and credentials.")
        sys.exit(1)
    
    # Step 5: Test email send
    send_ok = test_email_send(config)
    
    # Summary
    print_section("Summary")
    
    results = {
        "Configuration": "✅ OK" if config_ok else "❌ Issues found",
        "DNS Resolution": "✅ OK" if dns_ok else "❌ Failed",
        "Port Connectivity": "✅ OK" if port_ok else "❌ Failed",
        "SMTP Connection": "✅ OK" if smtp_ok else "❌ Failed",
        "Email Send": "✅ OK" if send_ok else "❌ Failed",
    }
    
    for test, result in results.items():
        print(f"   {test}: {result}")
    
    if all([config_ok, dns_ok, port_ok, smtp_ok]):
        print("\n🎉 All tests passed! Email should be working.")
        if config['MAIL_SUPPRESS_SEND'] == 'True':
            print("⚠️  BUT: MAIL_SUPPRESS_SEND=True - emails are still suppressed!")
            print("   Set MAIL_SUPPRESS_SEND=False to enable email sending.")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
    
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

