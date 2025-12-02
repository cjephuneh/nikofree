#!/usr/bin/env python3
"""
Test script to send an SMS
Usage: python test_sms.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.sms import send_sms, format_phone_for_sms

def test_sms():
    """Send a test SMS"""
    app = create_app()
    
    with app.app_context():
        # Temporarily disable SMS suppression for testing
        # This ensures the SMS is actually sent (not suppressed in dev mode)
        import os
        os.environ['SMS_SUPPRESS_SEND'] = 'False'
        app.config['SMS_SUPPRESS_SEND'] = False
        
        phone_number = "0708419386"  # Will be formatted automatically
        message = "Test SMS from Niko Free. This is a test message to verify the SMS API integration. If you receive this, the SMS service is working correctly! Thank you for testing!"
        
        print("="*50)
        print("SMS TEST")
        print("="*50)
        print(f"\nSending test SMS to: {phone_number}")
        print(f"Message: {message[:100]}...")
        print("\nSending...")
        
        # Format phone number
        formatted_phone = format_phone_for_sms(phone_number)
        print(f"Formatted phone: {formatted_phone}")
        
        # Send SMS
        send_sms(formatted_phone, message)
        
        print("\n✓ SMS queued! Check your phone in a few seconds.")
        print("="*50)
        print("\nNote: The SMS is sent asynchronously. Waiting 5 seconds for delivery...")
        import time
        time.sleep(5)  # Wait a bit for async thread to complete
        print("\n✓ Test completed. Check the logs above for delivery status.")

if __name__ == '__main__':
    test_sms()

