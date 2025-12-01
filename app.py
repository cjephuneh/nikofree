import os
from app import create_app, db
from app.models import *

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Make database models available in flask shell"""
    return {
        'db': db,
        'User': User,
        'Partner': Partner,
        'Event': Event,
        'EventHost': EventHost,
        'EventInterest': EventInterest,
        'EventPromotion': EventPromotion,
        'Ticket': Ticket,
        'TicketType': TicketType,
        'Booking': Booking,
        'PromoCode': PromoCode,
        'Payment': Payment,
        'PartnerPayout': PartnerPayout,
        'Category': Category,
        'Location': Location,
        'Notification': Notification,
        'AdminLog': AdminLog
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def seed_db():
    """Seed the database with initial data"""
    from slugify import slugify
    
    # Create categories
    categories_data = [
        {'name': 'Travel', 'description': 'Travel and adventure events'},
        {'name': 'Sports & Fitness', 'description': 'Sports and fitness activities'},
        {'name': 'Social Activities', 'description': 'Social gatherings and networking'},
        {'name': 'Hobbies & Interests', 'description': 'Hobby clubs and interest groups'},
        {'name': 'Religious', 'description': 'Religious and spiritual events'},
        {'name': 'Pets & Animals', 'description': 'Pet-related events'},
        {'name': 'Autofest', 'description': 'Automotive events and car shows'},
        {'name': 'Health & Wellbeing', 'description': 'Health and wellness events'},
        {'name': 'Music & Culture', 'description': 'Music and cultural events'},
        {'name': 'Coaching & Support', 'description': 'Coaching and mentorship'},
        {'name': 'Dance', 'description': 'Dance events and classes'},
        {'name': 'Technology', 'description': 'Tech events and meetups'},
        {'name': 'Gaming', 'description': 'Gaming events and tournaments'},
        {'name': 'Shopping', 'description': 'Shopping and market events'}
    ]
    
    for idx, cat_data in enumerate(categories_data):
        cat = Category.query.filter_by(slug=slugify(cat_data['name'])).first()
        if not cat:
            cat = Category(
                name=cat_data['name'],
                slug=slugify(cat_data['name']),
                description=cat_data['description'],
                display_order=idx
            )
            db.session.add(cat)
    
    # Create locations
    locations_data = [
        {'name': 'Nairobi', 'latitude': -1.2921, 'longitude': 36.8219},
        {'name': 'Mombasa', 'latitude': -4.0435, 'longitude': 39.6682},
        {'name': 'Kisumu', 'latitude': -0.0917, 'longitude': 34.7680},
        {'name': 'Nakuru', 'latitude': -0.3031, 'longitude': 36.0800},
        {'name': 'Eldoret', 'latitude': 0.5143, 'longitude': 35.2698}
    ]
    
    for idx, loc_data in enumerate(locations_data):
        loc = Location.query.filter_by(slug=slugify(loc_data['name'])).first()
        if not loc:
            loc = Location(
                name=loc_data['name'],
                slug=slugify(loc_data['name']),
                latitude=loc_data['latitude'],
                longitude=loc_data['longitude'],
                display_order=idx
            )
            db.session.add(loc)
    
    db.session.commit()
    print('Database seeded!')


@app.cli.command()
def create_admin():
    """Create admin user"""
    from getpass import getpass
    
    email = input('Admin email: ').strip()
    password = getpass('Admin password: ')
    first_name = input('First name: ').strip()
    last_name = input('Last name: ').strip()
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if user:
        print('User with this email already exists!')
        return
    
    # Create admin user
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        oauth_provider='email',
        is_verified=True,
        email_verified=True
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    print(f'Admin user created: {email}')
    print('You can now login with these credentials.')


@app.cli.command()
def clean_db():
    """Clean database: delete all events and users except testuser, testpartner, admin"""
    from app.models import Booking, Ticket, Notification, Review
    
    print("="*50)
    print("DATABASE CLEANUP")
    print("="*50)
    print("\nThis will:")
    print("  - Delete ALL events (approved, unapproved, everything)")
    print("  - Delete ALL users EXCEPT: testuser, testpartner, admin")
    print("  - Keep all tables intact")
    print("\n⚠️  WARNING: This action cannot be undone!")
    confirm = input("\nType 'yes' to continue: ").strip().lower()
    
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    try:
        print("\nStarting database cleanup...")
        
        # Step 1: Delete all events
        print("\n1. Deleting all events...")
        events_count = Event.query.count()
        print(f"   Found {events_count} events to delete")
        deleted_events = Event.query.delete()
        print(f"   ✓ Deleted {deleted_events} events")
        
        # Step 2: Find users to keep
        print("\n2. Finding users to keep...")
        users_to_keep = []
        
        # Find testuser
        testuser = User.query.filter(User.email.ilike('%testuser%')).first()
        if testuser:
            users_to_keep.append(testuser.id)
            print(f"   Keeping: {testuser.email} (ID: {testuser.id})")
        
        # Find testpartner
        testpartner = User.query.filter(User.email.ilike('%testpartner%')).first()
        if testpartner and testpartner.id not in users_to_keep:
            users_to_keep.append(testpartner.id)
            print(f"   Keeping: {testpartner.email} (ID: {testpartner.id})")
        
        # Find admin user
        admin_user = User.query.filter(User.email.ilike('%admin%')).first()
        if admin_user and admin_user.id not in users_to_keep:
            users_to_keep.append(admin_user.id)
            print(f"   Keeping: {admin_user.email} (ID: {admin_user.id})")
        
        # Also check config admin email
        from flask import current_app
        admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@nikofree.com')
        config_admin = User.query.filter_by(email=admin_email).first()
        if config_admin and config_admin.id not in users_to_keep:
            users_to_keep.append(config_admin.id)
            print(f"   Keeping (from config): {config_admin.email} (ID: {config_admin.id})")
        
        # Step 3: Delete other users
        print(f"\n3. Deleting users (keeping {len(users_to_keep)} users)...")
        if users_to_keep:
            deleted_users = User.query.filter(~User.id.in_(users_to_keep)).delete(synchronize_session=False)
        else:
            deleted_users = User.query.delete()
        print(f"   ✓ Deleted {deleted_users} users")
        
        # Step 4: Clean orphaned records
        print("\n4. Cleaning orphaned records...")
        orphaned_bookings = Booking.query.filter(~Booking.event_id.in_(db.session.query(Event.id))).delete(synchronize_session=False)
        orphaned_tickets = Ticket.query.filter(~Ticket.booking_id.in_(db.session.query(Booking.id))).delete(synchronize_session=False)
        orphaned_notifications = Notification.query.filter(
            (Notification.event_id.isnot(None)) & 
            (~Notification.event_id.in_(db.session.query(Event.id)))
        ).delete(synchronize_session=False)
        orphaned_reviews = Review.query.filter(
            (Review.event_id.isnot(None)) & 
            (~Review.event_id.in_(db.session.query(Event.id)))
        ).delete(synchronize_session=False)
        
        print(f"   ✓ Deleted {orphaned_bookings} orphaned bookings")
        print(f"   ✓ Deleted {orphaned_tickets} orphaned tickets")
        print(f"   ✓ Deleted {orphaned_notifications} orphaned notifications")
        print(f"   ✓ Deleted {orphaned_reviews} orphaned reviews")
        
        # Commit
        print("\n5. Committing changes...")
        db.session.commit()
        print("   ✓ Changes committed")
        
        # Summary
        print("\n" + "="*50)
        print("CLEANUP SUMMARY")
        print("="*50)
        print(f"Events deleted: {deleted_events}")
        print(f"Users deleted: {deleted_users}")
        print(f"Users kept: {len(users_to_keep)}")
        print(f"Orphaned records cleaned: {orphaned_bookings + orphaned_tickets + orphaned_notifications + orphaned_reviews}")
        print("\n✓ Database cleanup completed!")
        print("="*50)
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

