# Create Admin User Instructions

## Quick Setup

The admin user needs to be created in the database. Use one of these methods:

### Method 1: Using Flask CLI (Recommended)

```bash
cd /Users/mac/Documents/code/nikofree-server
flask create_admin
```

When prompted, enter:
- **Email**: `admin@nikofree.com`
- **Password**: `Admin@1234`
- **First name**: `System`
- **Last name**: `Administrator`

### Method 2: Using Python Script

```bash
cd /Users/mac/Documents/code/nikofree-server
python3 -c "
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Check if user exists
    user = User.query.filter_by(email='admin@nikofree.com').first()
    if user:
        print('User already exists!')
    else:
        # Create admin user
        admin = User(
            email='admin@nikofree.com',
            first_name='System',
            last_name='Administrator',
            oauth_provider='email',
            is_verified=True,
            email_verified=True,
            is_active=True
        )
        admin.set_password('Admin@1234')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully!')
        print('Email: admin@nikofree.com')
        print('Password: Admin@1234')
"

```

### Method 3: Using Python Interactive Shell

```bash
cd /Users/mac/Documents/code/nikofree-server
python3
```

Then run:
```python
from app import create_app, db
from app.models.user import User

app = create_app()
app.app_context().push()

# Check if user exists
user = User.query.filter_by(email='admin@nikofree.com').first()
if user:
    print('User already exists!')
else:
    # Create admin user
    admin = User(
        email='admin@nikofree.com',
        first_name='System',
        last_name='Administrator',
        oauth_provider='email',
        is_verified=True,
        email_verified=True,
        is_active=True
    )
    admin.set_password('Admin@1234')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created successfully!')
```

## Verify Admin Email in Config

Make sure `config.py` has:
```python
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@nikofree.com')
```

This is already set, so you're good!

## After Creating the User

1. Restart your Flask server (if it's running)
2. Try logging in with:
   - **Email**: `admin@nikofree.com`
   - **Password**: `Admin@1234`

## Troubleshooting

If you still get 401:
1. Check that the user was created: `User.query.filter_by(email='admin@nikofree.com').first()`
2. Verify the password: `user.check_password('Admin@1234')`
3. Make sure `ADMIN_EMAIL` in config matches the email you're using

