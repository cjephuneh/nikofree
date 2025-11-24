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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

