#!/usr/bin/env python3
"""
Script to create test partner applications for admin dashboard testing
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.partner import Partner
from app.models.category import Category
from datetime import datetime

def create_test_partners():
    app = create_app()
    
    with app.app_context():
        # Get first category
        category = Category.query.first()
        if not category:
            print("No categories found. Please run seed_db first.")
            return
        
        test_partners = [
            {
                'email': 'techhub@test.com',
                'business_name': 'Tech Hub Africa',
                'phone_number': '+254712345678',
                'location': 'Nairobi',
                'category_id': category.id,
                'status': 'pending'
            },
            {
                'email': 'fitnesspro@test.com',
                'business_name': 'Fitness Pro Kenya',
                'phone_number': '+254723456789',
                'location': 'Mombasa',
                'category_id': category.id,
                'status': 'pending'
            },
            {
                'email': 'creativearts@test.com',
                'business_name': 'Creative Arts Kenya',
                'phone_number': '+254734567890',
                'location': 'Nairobi',
                'category_id': category.id,
                'status': 'pending'
            },
        ]
        
        created = 0
        for partner_data in test_partners:
            # Check if partner already exists
            existing = Partner.query.filter_by(email=partner_data['email']).first()
            if existing:
                print(f"Partner {partner_data['email']} already exists, skipping...")
                continue
            
            partner = Partner(
                email=partner_data['email'],
                business_name=partner_data['business_name'],
                phone_number=partner_data['phone_number'],
                location=partner_data['location'],
                category_id=partner_data['category_id'],
                status=partner_data['status'],
                is_active=True,
                terms_accepted=True,
                contract_accepted=True,
                terms_accepted_at=datetime.utcnow(),
                contract_accepted_at=datetime.utcnow()
            )
            partner.set_password('Test@1234')
            
            db.session.add(partner)
            created += 1
        
        db.session.commit()
        print(f"✓ Created {created} test partner applications!")
        print("\nTest Partner Credentials:")
        for partner_data in test_partners:
            print(f"  Email: {partner_data['email']}")
            print(f"  Password: Test@1234")
            print(f"  Status: {partner_data['status']}")
            print()

if __name__ == '__main__':
    create_test_partners()

