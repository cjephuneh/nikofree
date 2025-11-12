import re
import phonenumbers
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_email(email):
    """Validate email address"""
    try:
        validate_email_lib(email)
        return True
    except EmailNotValidError:
        return False


def validate_phone(phone_number, country='KE'):
    """Validate phone number"""
    try:
        parsed = phonenumbers.parse(phone_number, country)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False


def validate_password(password):
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, None


def sanitize_string(text, max_length=None):
    """Sanitize string input"""
    if not text:
        return None
    
    # Strip whitespace
    text = text.strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

