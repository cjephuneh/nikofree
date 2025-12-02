#!/usr/bin/env python3
"""
Test script to send a booking confirmation SMS
Usage: python test_booking_sms.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Event, Booking, Ticket, TicketType, Partner, Category
from app.utils.sms import send_booking_confirmation_sms

def test_booking_sms():
    """Send a test booking confirmation SMS"""
    app = create_app()
    
    with app.app_context():
        # Disable SMS suppression for testing
        app.config['SMS_SUPPRESS_SEND'] = False
        os.environ['SMS_SUPPRESS_SEND'] = 'False'
        
        print("="*60)
        print("BOOKING CONFIRMATION SMS TEST")
        print("="*60)
        
        # Find or create a test user with the phone number
        phone_number = "0708419386"
        test_email = "testuser@test.com"
        
        print(f"\n1. Setting up test user with phone: {phone_number}")
        user = User.query.filter_by(email=test_email).first()
        
        if not user:
            print("   Creating test user...")
            user = User(
                email=test_email,
                first_name="Test",
                last_name="User",
                phone_number=phone_number,
                is_active=True,
                is_verified=True,
                email_verified=True,
                oauth_provider='email'
            )
            user.set_password("test123")
            db.session.add(user)
            db.session.commit()
            print(f"   ✓ Created user: {user.email}")
        else:
            # Update phone number
            user.phone_number = phone_number
            db.session.commit()
            print(f"   ✓ Using existing user: {user.email}")
        
        # Find or create a test event
        print("\n2. Setting up test event...")
        partner = Partner.query.first()
        if not partner:
            print("   Creating test partner...")
            partner = Partner(
                email="testpartner@test.com",
                phone_number="254700000000",
                business_name="Test Event Organizer",
                password_hash="dummy",
                status="approved",
                is_active=True
            )
            db.session.add(partner)
            db.session.commit()
        
        category = Category.query.first()
        if not category:
            print("   Creating test category...")
            category = Category(
                name="Test Category",
                slug="test-category",
                is_active=True
            )
            db.session.add(category)
            db.session.commit()
        
        event = Event.query.filter_by(title="Test Event for SMS").first()
        if not event:
            print("   Creating test event...")
            event = Event(
                title="Test Event for SMS",
                description="This is a test event to verify booking confirmation SMS",
                partner_id=partner.id,
                category_id=category.id,
                start_date=datetime.utcnow() + timedelta(days=7),
                end_date=datetime.utcnow() + timedelta(days=7, hours=3),
                venue_name="Test Venue",
                venue_address="123 Test Street, Nairobi",
                is_free=True,
                status="approved",
                is_published=True
            )
            db.session.add(event)
            db.session.commit()
            print(f"   ✓ Created event: {event.title}")
        else:
            print(f"   ✓ Using existing event: {event.title}")
        
        # Create a test booking
        print("\n3. Creating test booking...")
        booking = Booking(
            booking_number=f"TEST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            user_id=user.id,
            event_id=event.id,
            quantity=2,
            total_amount=0.00,  # Free event
            discount_amount=0.00,
            status="confirmed",
            payment_status="paid",
            confirmed_at=datetime.utcnow()
        )
        db.session.add(booking)
        db.session.commit()
        print(f"   ✓ Created booking: {booking.booking_number}")
        
        # Create a ticket type for the event (if it doesn't exist)
        print("\n4. Creating ticket type...")
        ticket_type = TicketType.query.filter_by(event_id=event.id, name="General Admission").first()
        if not ticket_type:
            ticket_type = TicketType(
                event_id=event.id,
                name="General Admission",
                description="General admission ticket",
                price=0.00,  # Free event
                quantity_total=None,  # Unlimited
                is_active=True
            )
            db.session.add(ticket_type)
            db.session.commit()
            print(f"   ✓ Created ticket type: {ticket_type.name}")
        else:
            print(f"   ✓ Using existing ticket type: {ticket_type.name}")
        
        # Create test tickets
        print("\n5. Creating test tickets...")
        tickets = []
        for i in range(2):
            ticket = Ticket(
                booking_id=booking.id,
                ticket_type_id=ticket_type.id,
                is_valid=True
            )
            tickets.append(ticket)
            db.session.add(ticket)
        db.session.commit()
        print(f"   ✓ Created {len(tickets)} tickets")
        
        # Send booking confirmation SMS
        print("\n6. Sending booking confirmation SMS...")
        print(f"   To: {user.phone_number} ({user.first_name} {user.last_name})")
        print(f"   Event: {event.title}")
        print(f"   Booking: {booking.booking_number}")
        print(f"   Tickets: {len(tickets)}")
        
        try:
            send_booking_confirmation_sms(booking, tickets)
            print("\n   ✓ SMS sent! Check your phone in a few seconds.")
            print("\n   Waiting 5 seconds for async delivery...")
            import time
            time.sleep(5)
            print("\n   ✓ Test completed!")
        except Exception as e:
            print(f"\n   ❌ Error sending SMS: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
        print("Test Summary:")
        print(f"  User: {user.email} ({user.phone_number})")
        print(f"  Event: {event.title}")
        print(f"  Booking: {booking.booking_number}")
        print(f"  Tickets: {len(tickets)}")
        print("="*60)

if __name__ == '__main__':
    test_booking_sms()

