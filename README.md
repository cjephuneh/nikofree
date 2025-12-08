
# Niko Free Backend API

Flask backend API for Niko Free - an event management and ticketing platform for Kenya.

## Features

- **User Management**: Registration, authentication (email, Google, Apple), profile management
- **Partner Management**: Partner registration, approval workflow, event management
- **Event Management**: Create, publish, and manage events with categories and locations
- **Ticket Management**: Multiple ticket types, promo codes, QR code generation
- **Payment Integration**: MPesa Daraja API integration for ticket payments
- **Admin Dashboard**: Approve partners/events, analytics, content management
- **Notifications**: In-app and email notifications
- **Booking System**: Event bookings, check-ins, attendee management

## Tech Stack

- **Framework**: Flask 3.0
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Authentication**: JWT tokens, OAuth (Google, Apple)
- **Payment**: MPesa Daraja API
- **Email**: Flask-Mail
- **File Storage**: Local or AWS S3
- **QR Codes**: qrcode library

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis (optional, for rate limiting)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd nikofree-server
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
flask init_db
flask seed_db
```

6. **Create admin user**
```bash
flask create_admin
```

7. **Run the application**
```bash
flask run
# Or for development with auto-reload
python app.py
```

The API will be available at `http://localhost:5000`

## Database Migrations

Using Flask-Migrate for database migrations:

```bash
# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## API Documentation

### Authentication Endpoints

#### User Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/google` - Login with Google
- `POST /api/auth/apple` - Login with Apple
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/verify` - Verify token

#### Partner Authentication
- `POST /api/auth/partner/register` - Register as partner
- `POST /api/auth/partner/login` - Partner login

### User Endpoints

- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/profile/picture` - Upload profile picture
- `GET /api/users/bookings` - Get user bookings
- `GET /api/users/bookings/<id>` - Get specific booking
- `GET /api/users/bucketlist` - Get wishlist
- `POST /api/users/bucketlist/<event_id>` - Add to wishlist
- `DELETE /api/users/bucketlist/<event_id>` - Remove from wishlist
- `GET /api/users/notifications` - Get notifications
- `PUT /api/users/notifications/<id>/read` - Mark as read

### Event Endpoints

- `GET /api/events/` - List all events (with filters)
- `GET /api/events/<id>` - Get event details
- `GET /api/events/promoted` - Get promoted events
- `GET /api/events/this-weekend` - Get weekend events
- `GET /api/events/calendar` - Get calendar events
- `GET /api/events/categories` - Get categories
- `GET /api/events/locations` - Get locations
- `POST /api/events/<id>/share` - Generate share links

### Partner Endpoints

- `GET /api/partners/dashboard` - Dashboard overview
- `GET /api/partners/profile` - Get profile
- `PUT /api/partners/profile` - Update profile
- `POST /api/partners/logo` - Upload logo
- `GET /api/partners/events` - Get partner events
- `POST /api/partners/events` - Create event
- `GET /api/partners/events/<id>` - Get event
- `PUT /api/partners/events/<id>` - Update event
- `DELETE /api/partners/events/<id>` - Delete event
- `POST /api/partners/events/<id>/poster` - Upload poster
- `POST /api/partners/events/<id>/tickets` - Create ticket type
- `POST /api/partners/events/<id>/promo-codes` - Create promo code
- `GET /api/partners/events/<id>/attendees` - Get attendees
- `GET /api/partners/events/<id>/attendees/export` - Export CSV
- `GET /api/partners/earnings` - Get earnings
- `GET /api/partners/payouts` - Get payouts
- `POST /api/partners/payouts` - Request payout

### Ticket/Booking Endpoints

- `POST /api/tickets/validate-promo` - Validate promo code
- `POST /api/tickets/book` - Book event tickets
- `POST /api/tickets/bookings/<id>/cancel` - Cancel booking
- `GET /api/tickets/<ticket_number>/verify` - Verify ticket
- `POST /api/tickets/<ticket_number>/checkin` - Check-in ticket
- `POST /api/tickets/scan` - Scan QR code

### Payment Endpoints

- `POST /api/payments/initiate` - Initiate payment
- `POST /api/payments/mpesa/callback` - MPesa callback (webhook)
- `GET /api/payments/status/<id>` - Check payment status
- `GET /api/payments/history` - Payment history
- `POST /api/payments/promote-event` - Pay for event promotion

### Admin Endpoints

- `GET /api/admin/dashboard` - Admin dashboard
- `GET /api/admin/partners` - List partners
- `GET /api/admin/partners/<id>` - Get partner details
- `POST /api/admin/partners/<id>/approve` - Approve partner
- `POST /api/admin/partners/<id>/reject` - Reject partner
- `POST /api/admin/partners/<id>/suspend` - Suspend partner
- `GET /api/admin/events` - List events
- `POST /api/admin/events/<id>/approve` - Approve event
- `POST /api/admin/events/<id>/reject` - Reject event
- `POST /api/admin/events/<id>/feature` - Feature event
- `GET /api/admin/users` - List users
- `GET /api/admin/categories` - Manage categories
- `POST /api/admin/categories` - Create category
- `PUT /api/admin/categories/<id>` - Update category
- `GET /api/admin/locations` - Manage locations
- `POST /api/admin/locations` - Create location
- `GET /api/admin/analytics` - Platform analytics
- `GET /api/admin/payouts` - List payout requests
- `POST /api/admin/payouts/<id>/approve` - Approve payout
- `GET /api/admin/logs` - Admin activity logs

### Notification Endpoints

- `GET /api/notifications/user` - User notifications
- `GET /api/notifications/partner` - Partner notifications
- `PUT /api/notifications/<id>/read` - Mark as read
- `PUT /api/notifications/read-all` - Mark all as read
- `DELETE /api/notifications/<id>` - Delete notification

## Configuration

Key configuration variables in `.env`:

```env
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nikofree

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# MPesa
MPESA_CONSUMER_KEY=your-mpesa-consumer-key
MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://your-domain.com/api/payments/mpesa/callback

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Business Logic
PLATFORM_COMMISSION_RATE=0.07
```

## MPesa Integration

The platform uses MPesa Daraja API for payments:

1. **STK Push**: For ticket payments
2. **B2C**: For partner payouts

### MPesa Setup

1. Register at [Safaricom Daraja](https://developer.safaricom.co.ke/)
2. Create an app and get credentials
3. Configure callback URL (must be publicly accessible)
4. Add credentials to `.env`

## Deployment

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set up email service (SendGrid, AWS SES, etc.)
- [ ] Configure MPesa production credentials
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure CORS for frontend domain
- [ ] Set up file storage (AWS S3 recommended)
- [ ] Configure Redis for rate limiting
- [ ] Set up monitoring and logging

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app
```

## Project Structure

```
nikofree-server/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── partner.py
│   │   ├── event.py
│   │   ├── ticket.py
│   │   ├── payment.py
│   │   ├── category.py
│   │   ├── notification.py
│   │   └── admin.py
│   ├── routes/              # API routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── partners.py
│   │   ├── events.py
│   │   ├── tickets.py
│   │   ├── payments.py
│   │   ├── notifications.py
│   │   └── admin.py
│   └── utils/               # Utility functions
│       ├── decorators.py
│       ├── email.py
│       ├── qrcode_generator.py
│       ├── file_upload.py
│       ├── mpesa.py
│       └── validators.py
├── uploads/                 # File uploads
├── migrations/              # Database migrations
├── config.py               # Configuration
├── app.py                  # Application entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## License

Proprietary - All rights reserved

## Support

For support, email support@nikofree.com

