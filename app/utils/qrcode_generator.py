import qrcode
import os
from io import BytesIO
from PIL import Image
from flask import current_app


def generate_qr_code(data, ticket_number):
    """
    Generate QR code for ticket
    
    Args:
        data: String data to encode in QR code
        ticket_number: Ticket number for filename
        
    Returns:
        str: Path to saved QR code image
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to uploads folder
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    qr_folder = os.path.join(upload_folder, 'qrcodes')
    
    # Create directory if it doesn't exist
    os.makedirs(qr_folder, exist_ok=True)
    
    # Save image
    filename = f"{ticket_number}.png"
    filepath = os.path.join(qr_folder, filename)
    img.save(filepath)
    
    # Return relative path
    return f"/uploads/qrcodes/{filename}"


def verify_qr_code(qr_data, expected_ticket_number):
    """
    Verify QR code data
    
    Args:
        qr_data: Scanned QR code data
        expected_ticket_number: Expected ticket number
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Simple verification - check if ticket number matches
    # In production, you might want to add encryption/signing
    return qr_data == expected_ticket_number

