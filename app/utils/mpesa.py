import requests
import base64
from datetime import datetime
from flask import current_app
import json


class MPesaClient:
    """MPesa Daraja API Client"""
    
    def __init__(self):
        self.consumer_key = current_app.config.get('MPESA_CONSUMER_KEY')
        self.consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET')
        self.shortcode = current_app.config.get('MPESA_SHORTCODE')
        self.passkey = current_app.config.get('MPESA_PASSKEY')
        self.callback_url = current_app.config.get('MPESA_CALLBACK_URL')
        
        # Set API URLs based on environment
        env = current_app.config.get('MPESA_ENVIRONMENT', 'sandbox')
        if env == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
    
    def get_access_token(self):
        """Get OAuth access token"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Create basic auth header
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_base64}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            print(f"Error getting MPesa access token: {str(e)}")
            return None
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """
        Initiate STK Push (Lipa Na M-Pesa Online)
        
        Args:
            phone_number: Customer phone number (254XXXXXXXXX)
            amount: Amount to charge
            account_reference: Reference for the transaction
            transaction_desc: Description of transaction
            
        Returns:
            dict: API response
        """
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password_bytes = password_string.encode('ascii')
        password = base64.b64encode(password_bytes).decode('ascii')
        
        # Prepare request
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error initiating STK push: {str(e)}")
            return {'error': str(e)}
    
    def stk_query(self, checkout_request_id):
        """
        Query STK Push status
        
        Args:
            checkout_request_id: CheckoutRequestID from STK push response
            
        Returns:
            dict: API response
        """
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password_bytes = password_string.encode('ascii')
        password = base64.b64encode(password_bytes).decode('ascii')
        
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error querying STK push: {str(e)}")
            return {'error': str(e)}
    
    def b2c_payment(self, phone_number, amount, occasion=''):
        """
        Send money to customer (B2C - for partner payouts)
        
        Args:
            phone_number: Recipient phone number
            amount: Amount to send
            occasion: Reason for payment
            
        Returns:
            dict: API response
        """
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Security credential (you need to generate this)
        # For production, encrypt the initiator password with MPesa public key
        security_credential = 'YOUR_SECURITY_CREDENTIAL'
        
        payload = {
            'InitiatorName': 'testapi',
            'SecurityCredential': security_credential,
            'CommandID': 'BusinessPayment',
            'Amount': int(amount),
            'PartyA': self.shortcode,
            'PartyB': phone_number,
            'Remarks': occasion or 'Partner Payout',
            'QueueTimeOutURL': f"{self.callback_url}/timeout",
            'ResultURL': f"{self.callback_url}/b2c",
            'Occasion': occasion or 'Withdrawal'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error initiating B2C payment: {str(e)}")
            return {'error': str(e)}


def format_phone_number(phone):
    """
    Format phone number to MPesa format (254XXXXXXXXX)
    
    Args:
        phone: Phone number in various formats
        
    Returns:
        str: Formatted phone number
    """
    # Remove spaces, dashes, and parentheses
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Remove leading zeros
    phone = phone.lstrip('0')
    
    # Remove leading plus
    phone = phone.lstrip('+')
    
    # Add country code if not present
    if not phone.startswith('254'):
        phone = '254' + phone
    
    return phone

