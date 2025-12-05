#!/usr/bin/env python3
"""
Test SMTP connection to diagnose email issues
"""
import os
import sys
import smtplib
import socket
from dotenv import load_dotenv

load_dotenv()

def test_smtp_connection():
    """Test SMTP server connectivity"""
    mail_server = os.getenv('MAIL_SERVER', 'mail.truhost.co.ke')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    mail_use_ssl = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    mail_username = os.getenv('MAIL_USERNAME', 'noreply@niko-free.com')
    mail_password = os.getenv('MAIL_PASSWORD')
    
    print("=" * 60)
    print("SMTP Connection Test")
    print("=" * 60)
    print(f"Server: {mail_server}")
    print(f"Port: {mail_port}")
    print(f"TLS: {mail_use_tls}")
    print(f"SSL: {mail_use_ssl}")
    print(f"Username: {mail_username}")
    print(f"Password: {'*' * len(mail_password) if mail_password else 'NOT SET'}")
    print("=" * 60)
    print()
    
    # Test 1: DNS Resolution
    print("1. Testing DNS resolution...")
    try:
        ip_address = socket.gethostbyname(mail_server)
        print(f"   ✅ DNS resolved: {mail_server} -> {ip_address}")
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return False
    print()
    
    # Test 2: Port connectivity
    print("2. Testing port connectivity...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((mail_server, mail_port))
        sock.close()
        if result == 0:
            print(f"   ✅ Port {mail_port} is open and reachable")
        else:
            print(f"   ❌ Port {mail_port} is closed or unreachable")
            print(f"   💡 This might be a firewall issue. Try:")
            print(f"      - Check if port {mail_port} is blocked by your firewall")
            print(f"      - Try from your production server instead")
            return False
    except Exception as e:
        print(f"   ❌ Connection test failed: {e}")
        return False
    print()
    
    # Test 3: SMTP connection
    print("3. Testing SMTP connection...")
    try:
        if mail_use_ssl:
            print(f"   Attempting SSL connection to {mail_server}:{mail_port}...")
            smtp = smtplib.SMTP_SSL(mail_server, mail_port, timeout=10)
        else:
            print(f"   Attempting connection to {mail_server}:{mail_port}...")
            smtp = smtplib.SMTP(mail_server, mail_port, timeout=10)
            if mail_use_tls:
                print("   Starting TLS...")
                smtp.starttls()
        
        print("   ✅ SMTP connection established")
        
        # Test 4: Authentication
        if mail_username and mail_password:
            print("4. Testing authentication...")
            try:
                smtp.login(mail_username, mail_password)
                print("   ✅ Authentication successful")
            except Exception as e:
                print(f"   ❌ Authentication failed: {e}")
                print(f"   💡 Check your username and password in .env file")
                smtp.quit()
                return False
        else:
            print("4. Skipping authentication (credentials not set)")
        
        smtp.quit()
        print()
        print("=" * 60)
        print("✅ All tests passed! SMTP server is reachable.")
        print("=" * 60)
        return True
        
    except socket.timeout:
        print(f"   ❌ Connection timeout after 10 seconds")
        print(f"   💡 Possible issues:")
        print(f"      - SMTP server is down or unreachable")
        print(f"      - Firewall is blocking the connection")
        print(f"      - Network connectivity issues")
        print(f"      - Wrong server address or port")
        return False
    except Exception as e:
        print(f"   ❌ SMTP connection failed: {e}")
        print(f"   💡 Error type: {type(e).__name__}")
        return False

if __name__ == '__main__':
    if not os.getenv('MAIL_PASSWORD'):
        print("⚠️  WARNING: MAIL_PASSWORD not set in .env file")
        print()
    
    success = test_smtp_connection()
    sys.exit(0 if success else 1)

