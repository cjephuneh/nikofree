# SMS Usage in Niko Free Application

This document lists all the places where SMS notifications are sent in the application.

## SMS Functions Available

All SMS functions are located in `app/utils/sms.py`:

### User SMS Functions

1. **`send_welcome_sms(user)`** - Welcome message for new users
2. **`send_booking_confirmation_sms(booking, tickets)`** - Booking confirmation with event details
3. **`send_payment_confirmation_sms(booking, payment)`** - Payment confirmation
4. **`send_payment_failed_sms(user, payment, event)`** - Payment failure notification
5. **`send_booking_cancellation_sms(user, booking, event)`** - Booking cancellation notification
6. **`send_password_reset_sms(user, reset_token)`** - Password reset code
7. **`send_event_notification_sms(user, event, notification_type)`** - Event reminders/updates

### Partner SMS Functions

8. **`send_partner_welcome_sms(partner)`** - Welcome message for new partners
9. **`send_partner_approval_sms(partner)`** - Partner account approval
10. **`send_partner_rejection_sms(partner, reason)`** - Partner application rejection
11. **`send_partner_suspension_sms(partner, reason)`** - Partner account suspension
12. **`send_partner_activation_sms(partner)`** - Partner account reactivation
13. **`send_event_approval_sms(partner, event)`** - Event approval notification
14. **`send_event_rejection_sms(partner, event, reason)`** - Event rejection notification
15. **`send_new_booking_sms_to_partner(partner, booking, event)`** - New booking notification to partner
16. **`send_booking_cancellation_to_partner_sms(partner, booking, event)`** - Booking cancellation notification to partner
17. **`send_payout_approval_sms(partner, payout)`** - Payout approval notification
18. **`send_promotion_payment_success_sms(partner, event)`** - Event promotion payment success

---

## Where SMS is Sent (By Route File)

### 1. **User Authentication** (`app/routes/auth.py`)

#### User Registration
- **Location**: `POST /api/auth/register`
- **SMS**: `send_welcome_sms(user)`
- **When**: After successful user registration (if phone number provided)

#### Password Reset
- **Location**: `POST /api/auth/forgot-password`
- **SMS**: `send_password_reset_sms(user, reset_token)`
- **When**: When user requests password reset (if phone number provided)

#### Partner Registration
- **Location**: `POST /api/auth/partner/register`
- **SMS**: `send_partner_welcome_sms(partner)`
- **When**: After partner submits application

#### Partner OAuth Registration
- **Location**: `POST /api/auth/partner/oauth`
- **SMS**: `send_partner_welcome_sms(partner)`
- **When**: After partner OAuth registration

---

### 2. **Ticket Bookings** (`app/routes/tickets.py`)

#### Create Booking
- **Location**: `POST /api/tickets/book`
- **SMS**: `send_booking_confirmation_sms(booking, tickets)`
- **When**: After successful booking creation

#### Cancel Booking
- **Location**: `POST /api/tickets/<booking_id>/cancel`
- **SMS**: 
  - `send_booking_cancellation_sms(user, booking, event)` - To user
  - `send_booking_cancellation_to_partner_sms(partner, booking, event)` - To partner
- **When**: When booking is cancelled

---

### 3. **Payments** (`app/routes/payments.py`)

#### Payment Success (MPesa Callback)
- **Location**: `POST /api/payments/mpesa/callback`
- **SMS**: 
  - `send_payment_confirmation_sms(booking, payment)` - Payment confirmation
  - `send_booking_confirmation_sms(booking, tickets)` - Booking confirmation
- **When**: When MPesa payment is successful

#### Payment Failed
- **Location**: `POST /api/payments/mpesa/callback`
- **SMS**: `send_payment_failed_sms(user, payment, event)`
- **When**: When MPesa payment fails

#### Event Promotion Payment Success
- **Location**: `POST /api/payments/mpesa/callback`
- **SMS**: `send_promotion_payment_success_sms(partner, event)`
- **When**: When event promotion payment is successful

---

### 4. **Admin Actions** (`app/routes/admin.py`)

#### Approve Partner
- **Location**: `PUT /api/admin/partners/<id>/approve`
- **SMS**: `send_partner_approval_sms(partner)`
- **When**: When admin approves a partner application

#### Reject Partner
- **Location**: `PUT /api/admin/partners/<id>/reject`
- **SMS**: `send_partner_rejection_sms(partner, reason)`
- **When**: When admin rejects a partner application

#### Suspend Partner
- **Location**: `PUT /api/admin/partners/<id>/suspend`
- **SMS**: `send_partner_suspension_sms(partner, reason)`
- **When**: When admin suspends a partner account

#### Activate Partner
- **Location**: `PUT /api/admin/partners/<id>/activate`
- **SMS**: `send_partner_activation_sms(partner)`
- **When**: When admin reactivates a suspended partner

#### Approve Payout
- **Location**: `PUT /api/admin/payouts/<id>/approve`
- **SMS**: `send_payout_approval_sms(partner, payout)`
- **When**: When admin approves a partner payout request

---

### 5. **Notifications** (`app/routes/notifications.py`)

#### Partner Approval Notification
- **Location**: `POST /api/notifications/partner/approve`
- **SMS**: `send_partner_approval_sms(partner)`
- **When**: When partner is approved

#### Partner Rejection Notification
- **Location**: `POST /api/notifications/partner/reject`
- **SMS**: `send_partner_rejection_sms(partner, reason)`
- **When**: When partner application is rejected

#### Event Approval Notification
- **Location**: `POST /api/notifications/event/approve`
- **SMS**: `send_event_approval_sms(partner, event)`
- **When**: When event is approved

#### Event Rejection Notification
- **Location**: `POST /api/notifications/event/reject`
- **SMS**: `send_event_rejection_sms(partner, event, reason)`
- **When**: When event is rejected

#### New Booking Notification
- **Location**: `POST /api/notifications/booking/new`
- **SMS**: `send_new_booking_sms_to_partner(partner, booking, event)`
- **When**: When a new booking is created for a partner's event

#### Event Reminder
- **Location**: `POST /api/notifications/event/reminder`
- **SMS**: `send_event_notification_sms(user, event, 'reminder')`
- **When**: When sending event reminders to users

---

## Summary by Category

### User-Facing SMS (Sent to Users)
1. Welcome message (registration)
2. Booking confirmation
3. Payment confirmation
4. Payment failure
5. Booking cancellation
6. Password reset code
7. Event reminders

### Partner-Facing SMS (Sent to Partners)
1. Welcome message (registration)
2. Account approval
3. Account rejection
4. Account suspension
5. Account reactivation
6. Event approval
7. Event rejection
8. New booking notification
9. Booking cancellation notification
10. Payout approval
11. Promotion payment success

---

## Configuration

SMS sending can be controlled via environment variable:
- `SMS_SUPPRESS_SEND=True` - Suppresses all SMS sending (useful for development)

All SMS functions check this configuration before sending.

---

## Phone Number Formatting

All phone numbers are automatically formatted to include the country code (254 for Kenya):
- `0708419386` → `254708419386`
- `+254708419386` → `254708419386`
- `254708419386` → `254708419386` (unchanged)

This is handled by the `format_phone_for_sms()` function.

