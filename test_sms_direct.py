#!/usr/bin/env python3
"""
Direct test script to send SMS - shows full API interaction
"""

import requests
import json
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API Configuration
CELCOM_SMS_URL = "https://isms.celcomafrica.com/api/services/sendsms/"
CELCOM_API_KEY = "ffbf65bc0649575080064282d3a324f8"
CELCOM_PARTNER_ID = "946"
CELCOM_SHORTCODE = "NIKO FREE"

# Phone number
phone_number = "254708419386"  # Already formatted with country code

# Message (using plain text first to avoid encoding issues)
message = "Test SMS from Niko Free. This is a test message to verify the SMS API integration. If you receive this, the SMS service is working correctly! Thank you for testing!"

print("="*60)
print("DIRECT SMS API TEST")
print("="*60)
print(f"\nURL: {CELCOM_SMS_URL}")
print(f"API Key: {CELCOM_API_KEY}")
print(f"Partner ID: {CELCOM_PARTNER_ID}")
print(f"Shortcode: {CELCOM_SHORTCODE}")
print(f"Phone: {phone_number}")
print(f"\nMessage:\n{message}")
print("\n" + "="*60)

# Prepare payload (exactly as PHP example)
payload = {
    "apikey": CELCOM_API_KEY,
    "partnerID": CELCOM_PARTNER_ID,
    "message": message,
    "shortcode": CELCOM_SHORTCODE,
    "mobile": phone_number,
    "pass_type": "plain"
}

print("\n📤 Sending POST request...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        CELCOM_SMS_URL,
        json=payload,
        headers=headers,
        timeout=30,
        verify=False
    )
    
    print(f"\n📥 Response Status Code: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    print(f"📥 Response Text: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"\n📥 Response JSON:")
            print(json.dumps(result, indent=2))
            
            # Parse response
            if 'responses' in result and isinstance(result['responses'], list):
                for idx, response_item in enumerate(result['responses']):
                    print(f"\n--- Response Item {idx + 1} ---")
                    response_code = response_item.get('response-code') or response_item.get('respose-code')
                    mobile = response_item.get('mobile')
                    message_id = response_item.get('messageid')
                    description = response_item.get('response-description', 'N/A')
                    network_id = response_item.get('networkid', 'N/A')
                    
                    print(f"Response Code: {response_code}")
                    print(f"Mobile: {mobile}")
                    print(f"Message ID: {message_id}")
                    print(f"Description: {description}")
                    print(f"Network ID: {network_id}")
                    
                    if response_code == 200:
                        print(f"\n✅ SUCCESS! SMS sent successfully!")
                        print(f"   Message ID: {message_id}")
                    else:
                        print(f"\n❌ FAILED! Error Code: {response_code}")
                        print(f"   Description: {description}")
            else:
                print("\n⚠️ Unexpected response format")
                print(f"Response: {result}")
                
        except ValueError as e:
            print(f"\n❌ Failed to parse JSON response")
            print(f"Error: {e}")
            print(f"Raw response: {response.text}")
    else:
        print(f"\n❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Request Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test completed. Check your phone for the SMS.")
print("="*60)

