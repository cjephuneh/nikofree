"""
Ticket PDF Generator
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os
from flask import current_app


def generate_ticket_pdf(booking, tickets):
    """
    Generate PDF ticket with QR code
    
    Args:
        booking: Booking object
        tickets: List of Ticket objects
        
    Returns:
        BytesIO: PDF file as BytesIO object
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        spaceAfter=10,
        alignment=TA_LEFT
    )
    
    # Title
    elements.append(Paragraph("NIKO FREE", title_style))
    elements.append(Paragraph("EVENT TICKET", heading_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Event Information
    event = booking.event
    elements.append(Paragraph(f"<b>Event:</b> {event.title}", normal_style))
    
    # Date and Time
    date_str = event.start_date.strftime('%A, %B %d, %Y')
    time_str = event.start_date.strftime('%I:%M %p')
    if event.end_date:
        end_time_str = event.end_date.strftime('%I:%M %p')
        time_str = f"{time_str} - {end_time_str}"
    
    elements.append(Paragraph(f"<b>Date:</b> {date_str}", normal_style))
    elements.append(Paragraph(f"<b>Time:</b> {time_str}", normal_style))
    
    # Venue
    venue = event.venue_name or event.venue_address or "Online Event"
    elements.append(Paragraph(f"<b>Venue:</b> {venue}", normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Booking Information
    elements.append(Paragraph("<b>Booking Details</b>", heading_style))
    elements.append(Paragraph(f"<b>Booking Number:</b> {booking.booking_number}", normal_style))
    elements.append(Paragraph(f"<b>Quantity:</b> {booking.quantity} ticket(s)", normal_style))
    elements.append(Paragraph(f"<b>Total Amount:</b> KES {booking.total_amount:,.2f}", normal_style))
    elements.append(Paragraph(f"<b>Status:</b> {booking.status.upper()}", normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # QR Code for each ticket
    for idx, ticket in enumerate(tickets, 1):
        if idx > 1:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("─" * 50, normal_style))
            elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph(f"<b>Ticket {idx}</b>", heading_style))
        elements.append(Paragraph(f"<b>Ticket Number:</b> {ticket.ticket_number}", normal_style))
        
        if ticket.ticket_type:
            elements.append(Paragraph(f"<b>Type:</b> {ticket.ticket_type.name}", normal_style))
        
        # QR Code Image
        if ticket.qr_code:
            qr_path = ticket.qr_code
            
            # Handle different path formats
            # QR code path is typically: /uploads/qrcodes/TKT-YYYYMMDD-XXXXXXXXXX.png
            if qr_path.startswith('/uploads/'):
                # Remove leading slash to make it relative
                qr_path = qr_path[1:]
            elif qr_path.startswith('uploads/'):
                # Already correct format
                pass
            elif not qr_path.startswith('http') and not os.path.isabs(qr_path):
                # Assume it's relative to uploads folder
                qr_path = f"uploads/{qr_path}"
            
            # Build absolute path
            try:
                # Get upload folder from Flask config
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            except RuntimeError:
                # Not in Flask context, use default
                upload_folder = 'uploads'
            
            # Get project root for alternative paths
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Construct full path
            if os.path.isabs(upload_folder):
                # Absolute path
                if qr_path.startswith('uploads/'):
                    qr_path = os.path.join(upload_folder, qr_path.replace('uploads/', '', 1))
                else:
                    qr_path = os.path.join(upload_folder, qr_path)
            else:
                # Relative to project root
                qr_path = os.path.join(project_root, qr_path)
            
            # Normalize path (resolve .. and .)
            qr_path = os.path.normpath(qr_path)
            
            # Check if file exists
            print(f"📄 [PDF] Looking for QR code at: {qr_path}")
            if os.path.exists(qr_path):
                try:
                    qr_image = Image(qr_path, width=2*inch, height=2*inch)
                    elements.append(Spacer(1, 0.1*inch))
                    elements.append(qr_image)
                    elements.append(Spacer(1, 0.1*inch))
                    elements.append(Paragraph("Scan this QR code at the event entrance", normal_style))
                    print(f"✅ [PDF] QR code image added successfully")
                except Exception as e:
                    print(f"❌ [PDF] Error loading QR code image: {e}")
                    import traceback
                    traceback.print_exc()
                    elements.append(Paragraph("QR Code: Available in app", normal_style))
            else:
                print(f"⚠️ [PDF] QR code file not found at: {qr_path}")
                # Try alternative paths
                qr_filename = os.path.basename(qr_path)
                alt_paths = [
                    os.path.join(project_root, 'uploads', 'qrcodes', qr_filename),
                    os.path.join(upload_folder, 'qrcodes', qr_filename) if not os.path.isabs(upload_folder) else os.path.join(upload_folder, 'qrcodes', qr_filename),
                ]
                found = False
                for alt_path in alt_paths:
                    alt_path = os.path.normpath(alt_path)
                    if os.path.exists(alt_path):
                        try:
                            qr_image = Image(alt_path, width=2*inch, height=2*inch)
                            elements.append(Spacer(1, 0.1*inch))
                            elements.append(qr_image)
                            elements.append(Spacer(1, 0.1*inch))
                            elements.append(Paragraph("Scan this QR code at the event entrance", normal_style))
                            print(f"✅ [PDF] QR code found at alternative path: {alt_path}")
                            found = True
                            break
                        except Exception as e:
                            print(f"❌ [PDF] Error loading QR code from alt path {alt_path}: {e}")
                            continue
                
                if not found:
                    print(f"⚠️ [PDF] QR code not found in any path. Ticket: {ticket.ticket_number}, QR path: {ticket.qr_code}")
                    elements.append(Paragraph("QR Code: Available in app", normal_style))
        else:
            print(f"⚠️ [PDF] No QR code path for ticket {ticket.ticket_number}")
            elements.append(Paragraph("QR Code: Available in app", normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        spaceBefore=20
    )
    elements.append(Paragraph("Thank you for using Niko Free!", footer_style))
    elements.append(Paragraph("Present this ticket or QR code at the event entrance", footer_style))
    elements.append(Paragraph("For support, contact: support@niko-free.com", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    buffer.seek(0)
    return buffer


def generate_ticket_pdf_file(booking, tickets, output_path):
    """
    Generate PDF ticket and save to file
    
    Args:
        booking: Booking object
        tickets: List of Ticket objects
        output_path: Path to save PDF file
        
    Returns:
        str: Path to saved PDF file
    """
    pdf_buffer = generate_ticket_pdf(booking, tickets)
    
    # Save to file
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.read())
    
    return output_path

