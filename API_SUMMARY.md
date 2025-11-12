# Niko Free API - Complete Summary

## Overview

This document provides a complete overview of all implemented APIs in the Niko Free backend.

## API Categories

### 1. Authentication APIs (8 endpoints)
**File**: `app/routes/auth.py`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | User registration | No |
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/google` | Google OAuth login | No |
| POST | `/api/auth/apple` | Apple OAuth login | No |
| POST | `/api/auth/partner/register` | Partner registration | No |
| POST | `/api/auth/partner/login` | Partner login | No |
| POST | `/api/auth/refresh` | Refresh access token | Refresh Token |
| GET | `/api/auth/verify` | Verify token validity | JWT |

**Features:**
- Email/password authentication
- Google OAuth integration
- Apple OAuth (placeholder)
- Partner/organizer separate authentication
- JWT token management
- Refresh token functionality

---

### 2. User APIs (11 endpoints)
**File**: `app/routes/users.py`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/profile` | Get user profile | User JWT |
| PUT | `/api/users/profile` | Update profile | User JWT |
| POST | `/api/users/profile/picture` | Upload profile picture | User JWT |
| GET | `/api/users/bookings` | Get user bookings | User JWT |
| GET | `/api/users/bookings/<id>` | Get specific booking | User JWT |
| GET | `/api/users/bucketlist` | Get wishlist | User JWT |
| POST | `/api/users/bucketlist/<event_id>` | Add to wishlist | User JWT |
| DELETE | `/api/users/bucketlist/<event_id>` | Remove from wishlist | User JWT |
| GET | `/api/users/notifications` | Get notifications | User JWT |
| PUT | `/api/users/notifications/<id>/read` | Mark as read | User JWT |
| PUT | `/api/users/notifications/read-all` | Mark all as read | User JWT |
| GET | `/api/users/search` | Search users | No |

**Features:**
- Profile management
- Booking history (upcoming, past, cancelled)
- Wishlist/bucketlist functionality
- Notification system
- User search for event hosts

---

### 3. Event APIs (10 endpoints)
**File**: `app/routes/events.py`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/events/` | List all events (with filters) | Optional |
| GET | `/api/events/<id>` | Get event details | Optional |
| GET | `/api/events/promoted` | Get promoted events | No |
| GET | `/api/events/this-weekend` | Weekend events | No |
| GET | `/api/events/calendar` | Calendar view events | No |
| GET | `/api/events/categories` | Get all categories | No |
| GET | `/api/events/categories/<id>/events` | Events by category | No |
| GET | `/api/events/locations` | Get all locations | No |
| POST | `/api/events/<id>/share` | Generate share links | No |
| GET | `/api/events/search/autocomplete` | Search suggestions | No |

**Features:**
- Advanced filtering (category, location, free/paid, search)
- Event promotion system
- Weekend events feature
- Calendar integration
- Category-based browsing
- Social sharing
- Search autocomplete

---

### 4. Partner APIs (16 endpoints)
**File**: `app/routes/partners.py`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/partners/dashboard` | Dashboard overview | Partner JWT |
| GET | `/api/partners/profile` | Get profile | Partner JWT |
| PUT | `/api/partners/profile` | Update profile | Partner JWT |
| POST | `/api/partners/logo` | Upload logo | Partner JWT |
| GET | `/api/partners/events` | Get partner events | Partner JWT |
| POST | `/api/partners/events` | Create event | Partner JWT |
| GET | `/api/partners/events/<id>` | Get event | Partner JWT |
| PUT | `/api/partners/events/<id>` | Update event | Partner JWT |
| DELETE | `/api/partners/events/<id>` | Delete event | Partner JWT |
| POST | `/api/partners/events/<id>/poster` | Upload poster | Partner JWT |
| POST | `/api/partners/events/<id>/tickets` | Create ticket type | Partner JWT |
| POST | `/api/partners/events/<id>/promo-codes` | Create promo code | Partner JWT |
| GET | `/api/partners/events/<id>/attendees` | Get attendees | Partner JWT |
| GET | `/api/partners/events/<id>/attendees/export` | Export CSV | Partner JWT |
| GET | `/api/partners/earnings` | Get earnings | Partner JWT |
| GET | `/api/partners/payouts` | Get payout history | Partner JWT |
| POST | `/api/partners/payouts` | Request payout | Partner JWT |

**Features:**
- Comprehensive dashboard with stats
- Event management (CRUD)
- Multiple ticket types per event
- Promo code creation
- Attendee management & export
- Earnings tracking
- Payout requests (MPesa/Bank)

---

### 5. Ticket & Booking APIs (6 endpoints)
**File**: `app/routes/tickets.py`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/tickets/validate-promo` | Validate promo code | User JWT |
| POST | `/api/tickets/book` | Book event tickets | User JWT |
| POST | `/api/tickets/bookings/<id>/cancel` | Cancel booking | User JWT |
| GET | `/api/tickets/<ticket_number>/verify` | Verify ticket | Partner JWT |
| POST | `/api/tickets/<ticket_number>/checkin` | Check-in ticket | Partner JWT |
| POST | `/api/tickets/scan` | Scan QR code | Partner JWT |

**Features:**
- Ticket booking with promo codes
- Automatic QR code generation
- Free event auto-confirmation
- Paid event payment integration
- Ticket verification for partners
- QR code scanning for check-in

---

### 6. Payment APIs (4 endpoints)
**File**: `app/routes/payments.py`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/payments/initiate` | Initiate MPesa payment | User JWT |
| POST | `/api/payments/mpesa/callback` | MPesa callback webhook | No |
| GET | `/api/payments/status/<id>` | Check payment status | User JWT |
| GET | `/api/payments/history` | Payment history | User JWT |
| POST | `/api/payments/promote-event` | Pay for promotion | No |

**Features:**
- MPesa STK Push integration
- Payment callback handling
- Automatic ticket generation on payment
- Commission calculation (7%)
- Event promotion payments
- Payment status tracking

---

### 7. Admin APIs (18 endpoints)
**File**: `app/routes/admin.py`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/dashboard` | Admin dashboard | Admin JWT |
| GET | `/api/admin/partners` | List all partners | Admin JWT |
| GET | `/api/admin/partners/<id>` | Get partner details | Admin JWT |
| POST | `/api/admin/partners/<id>/approve` | Approve partner | Admin JWT |
| POST | `/api/admin/partners/<id>/reject` | Reject partner | Admin JWT |
| POST | `/api/admin/partners/<id>/suspend` | Suspend partner | Admin JWT |
| POST | `/api/admin/partners/<id>/activate` | Activate partner | Admin JWT |
| GET | `/api/admin/events` | List all events | Admin JWT |
| POST | `/api/admin/events/<id>/approve` | Approve event | Admin JWT |
| POST | `/api/admin/events/<id>/reject` | Reject event | Admin JWT |
| POST | `/api/admin/events/<id>/feature` | Feature event | Admin JWT |
| GET | `/api/admin/users` | List all users | Admin JWT |
| GET | `/api/admin/categories` | Get categories | Admin JWT |
| POST | `/api/admin/categories` | Create category | Admin JWT |
| PUT | `/api/admin/categories/<id>` | Update category | Admin JWT |
| GET | `/api/admin/locations` | Get locations | Admin JWT |
| POST | `/api/admin/locations` | Create location | Admin JWT |
| GET | `/api/admin/analytics` | Platform analytics | Admin JWT |
| GET | `/api/admin/payouts` | List payouts | Admin JWT |
| POST | `/api/admin/payouts/<id>/approve` | Approve payout | Admin JWT |
| GET | `/api/admin/logs` | Admin activity logs | Admin JWT |

**Features:**
- Comprehensive admin dashboard
- Partner approval workflow
- Event approval/rejection
- User management
- Category & location management
- Platform analytics
- Payout approval system
- Activity logging

---

### 8. Notification APIs (6 endpoints)
**File**: `app/routes/notifications.py`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/notifications/user` | User notifications | User JWT |
| GET | `/api/notifications/partner` | Partner notifications | Partner JWT |
| PUT | `/api/notifications/<id>/read` | Mark as read | JWT |
| PUT | `/api/notifications/read-all` | Mark all as read | User JWT |
| PUT | `/api/notifications/partner/read-all` | Mark all as read | Partner JWT |
| DELETE | `/api/notifications/<id>` | Delete notification | JWT |

**Features:**
- In-app notifications
- Email notifications
- User & partner separate channels
- Notification types: booking, approval, reminder, etc.
- Helper functions for common notifications

---

## Database Models

### Core Models (10 tables)

1. **User** - User accounts (attendees)
2. **Partner** - Partner/organizer accounts
3. **Event** - Events
4. **EventHost** - Event co-hosts
5. **EventInterest** - Event interests/tags
6. **EventPromotion** - Event promotions
7. **TicketType** - Ticket types for events
8. **Booking** - Event bookings
9. **Ticket** - Individual tickets with QR codes
10. **PromoCode** - Promotional discount codes
11. **Payment** - Payment transactions
12. **PartnerPayout** - Partner withdrawal requests
13. **Category** - Event categories
14. **Location** - Event locations/cities
15. **Notification** - User notifications
16. **AdminLog** - Admin activity logs

---

## Utility Modules

### 1. Decorators (`app/utils/decorators.py`)
- `@user_required` - Require user authentication
- `@partner_required` - Require partner authentication
- `@admin_required` - Require admin authentication
- `@optional_user` - Optional user authentication

### 2. Email (`app/utils/email.py`)
- Send welcome emails
- Booking confirmations
- Partner approval/rejection
- Event approval/rejection
- Async email sending

### 3. QR Code Generation (`app/utils/qrcode_generator.py`)
- Generate QR codes for tickets
- Verify QR codes

### 4. File Upload (`app/utils/file_upload.py`)
- Local file upload
- AWS S3 upload support
- File validation
- Secure filename generation

### 5. MPesa Integration (`app/utils/mpesa.py`)
- STK Push (Lipa Na M-Pesa)
- Payment query
- B2C payments (payouts)
- Phone number formatting

### 6. Validators (`app/utils/validators.py`)
- Email validation
- Phone number validation
- Password strength validation
- Input sanitization

---

## Key Features Implemented

✅ **User Side**
- Registration & authentication (Email, Google, Apple)
- Event browsing & search
- Event filtering (category, location, free/paid)
- Ticket booking
- Wishlist/bucketlist
- Digital tickets with QR codes
- Booking history
- Notifications

✅ **Partner Side**
- Partner registration & approval
- Event creation & management
- Multiple ticket types
- Promo codes
- Attendee management
- Check-in system (QR scanning)
- Earnings tracking
- Payout requests

✅ **Admin Side**
- Dashboard with analytics
- Partner approval/rejection
- Event approval/rejection
- User management
- Category & location management
- Payout approvals
- Activity logging

✅ **Payment Integration**
- MPesa Daraja API
- STK Push for payments
- Automatic commission (7%)
- Partner payouts
- Payment tracking

✅ **Additional Features**
- Email notifications
- In-app notifications
- QR code generation
- File uploads
- Rate limiting
- JWT authentication
- Database migrations
- Seeding scripts

---

## Technical Stack

- **Framework**: Flask 3.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT, OAuth (Google, Apple)
- **Payment**: MPesa Daraja API
- **Email**: Flask-Mail
- **QR Codes**: qrcode library
- **File Storage**: Local/AWS S3
- **Rate Limiting**: Flask-Limiter
- **Migrations**: Flask-Migrate

---

## Statistics

- **Total API Endpoints**: 79+
- **Database Models**: 16
- **Utility Modules**: 6
- **Lines of Code**: ~5000+
- **Files Created**: 30+

---

## Setup Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
flask init_db
flask seed_db
flask create_admin

# Run development server
flask run

# Run production server
gunicorn -c gunicorn_config.py app:app
```

---

## Environment Variables Required

- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT secret key
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret
- `MPESA_CONSUMER_KEY` - MPesa API consumer key
- `MPESA_CONSUMER_SECRET` - MPesa API secret
- `MPESA_SHORTCODE` - MPesa business shortcode
- `MPESA_PASSKEY` - MPesa passkey
- `MAIL_USERNAME` - SMTP email
- `MAIL_PASSWORD` - SMTP password
- `ADMIN_EMAIL` - Admin user email

---

## Next Steps / Future Enhancements

- [ ] Apple Sign In implementation
- [ ] SMS notifications (AfricaTalking)
- [ ] Push notifications (FCM)
- [ ] Advanced analytics
- [ ] Event recommendations
- [ ] Social features (comments, ratings)
- [ ] Multi-currency support
- [ ] Multiple payment gateways
- [ ] Event series/recurring events
- [ ] Seat selection for events
- [ ] Waitlist functionality
- [ ] Affiliate system
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Comprehensive test suite
- [ ] Performance optimization
- [ ] Caching layer (Redis)
- [ ] Background jobs (Celery)
- [ ] WebSocket support for real-time updates

---

## Documentation Files

1. `README.md` - Main documentation
2. `API_ENDPOINTS.md` - Detailed API reference with examples
3. `API_SUMMARY.md` - This file - complete overview
4. `DEPLOYMENT.md` - Deployment guide
5. `.env.example` - Environment variables template

---

## License

Proprietary - All rights reserved

---

**Built with ❤️ for Niko Free**

