# Niko Free API Endpoints

Complete list of all API endpoints with request/response examples.

## Base URL
```
Development: http://localhost:5000
Production: https://api.nikofree.com
```

## Authentication

All authenticated requests require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 1. Authentication APIs

### 1.1 User Registration
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+254712345678",
  "date_of_birth": "1990-01-01"
}

Response 201:
{
  "message": "User registered successfully",
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### 1.2 User Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "keep_logged_in": true
}

Response 200:
{
  "message": "Login successful",
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### 1.3 Google Login
```http
POST /api/auth/google
Content-Type: application/json

{
  "token": "google_id_token"
}

Response 200:
{
  "message": "Login successful",
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### 1.4 Partner Registration
```http
POST /api/auth/partner/register
Content-Type: application/json

{
  "email": "partner@example.com",
  "password": "SecurePass123",
  "business_name": "Event Organizers Ltd",
  "phone_number": "+254712345678",
  "category_id": 1,
  "contract_accepted": true
}

Response 201:
{
  "message": "Partner registration submitted...",
  "partner": { ... }
}
```

### 1.5 Partner Login
```http
POST /api/auth/partner/login
Content-Type: application/json

{
  "email": "partner@example.com",
  "password": "SecurePass123"
}

Response 200:
{
  "message": "Login successful",
  "partner": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### 1.6 Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

Response 200:
{
  "access_token": "eyJ..."
}
```

---

## 2. User APIs

### 2.1 Get Profile
```http
GET /api/users/profile
Authorization: Bearer <token>

Response 200:
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  ...
}
```

### 2.2 Update Profile
```http
PUT /api/users/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+254712345678",
  "location": "Nairobi"
}

Response 200:
{
  "message": "Profile updated successfully",
  "user": { ... }
}
```

### 2.3 Get Bookings
```http
GET /api/users/bookings?status=upcoming&page=1&per_page=20
Authorization: Bearer <token>

Response 200:
{
  "bookings": [ ... ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

### 2.4 Get Bucketlist
```http
GET /api/users/bucketlist?page=1
Authorization: Bearer <token>

Response 200:
{
  "events": [ ... ],
  "total": 5,
  "page": 1,
  "pages": 1
}
```

### 2.5 Add to Bucketlist
```http
POST /api/users/bucketlist/123
Authorization: Bearer <token>

Response 200:
{
  "message": "Event added to bucketlist"
}
```

---

## 3. Event APIs

### 3.1 List Events
```http
GET /api/events/?page=1&per_page=20&category=music&location=nairobi&is_free=true&search=concert
Authorization: Bearer <token> (optional)

Response 200:
{
  "events": [ ... ],
  "total": 50,
  "page": 1,
  "pages": 3,
  "per_page": 20
}
```

### 3.2 Get Event Details
```http
GET /api/events/123
Authorization: Bearer <token> (optional)

Response 200:
{
  "id": 123,
  "title": "Music Concert",
  "description": "...",
  "start_date": "2024-12-31T18:00:00",
  "venue_name": "Carnivore",
  "category": { ... },
  "ticket_types": [ ... ],
  "in_bucketlist": false,
  ...
}
```

### 3.3 Get Promoted Events
```http
GET /api/events/promoted

Response 200:
{
  "events": [ ... ],
  "count": 5
}
```

### 3.4 This Weekend Events
```http
GET /api/events/this-weekend

Response 200:
{
  "events": [ ... ],
  "count": 10,
  "weekend_start": "2024-12-07T00:00:00",
  "weekend_end": "2024-12-08T23:59:59"
}
```

### 3.5 Get Categories
```http
GET /api/events/categories

Response 200:
{
  "categories": [
    {
      "id": 1,
      "name": "Music & Culture",
      "slug": "music-culture",
      "icon": "/uploads/icons/music.png"
    },
    ...
  ]
}
```

---

## 4. Partner APIs

### 4.1 Dashboard
```http
GET /api/partners/dashboard
Authorization: Bearer <partner_token>

Response 200:
{
  "partner": { ... },
  "stats": {
    "total_events": 10,
    "upcoming_events": 5,
    "total_attendees": 250,
    "total_earnings": 50000.00,
    "pending_earnings": 25000.00
  },
  "recent_bookings": [ ... ]
}
```

### 4.2 Create Event
```http
POST /api/partners/events
Authorization: Bearer <partner_token>
Content-Type: application/json

{
  "title": "Tech Meetup",
  "description": "Monthly tech meetup",
  "category_id": 12,
  "start_date": "2024-12-15T18:00:00",
  "end_date": "2024-12-15T21:00:00",
  "venue_name": "iHub",
  "venue_address": "Nairobi, Kenya",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "location_id": 1,
  "is_free": true,
  "interests": ["Technology", "Networking", "Startups"],
  "host_ids": [5, 10]
}

Response 201:
{
  "message": "Event created successfully...",
  "event": { ... }
}
```

### 4.3 Update Event
```http
PUT /api/partners/events/123
Authorization: Bearer <partner_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  ...
}

Response 200:
{
  "message": "Event updated successfully",
  "event": { ... }
}
```

### 4.4 Create Ticket Type
```http
POST /api/partners/events/123/tickets
Authorization: Bearer <partner_token>
Content-Type: application/json

{
  "name": "VIP",
  "description": "VIP access",
  "price": 5000.00,
  "quantity_total": 50,
  "min_per_order": 1,
  "max_per_order": 5
}

Response 201:
{
  "message": "Ticket type created successfully",
  "ticket_type": { ... }
}
```

### 4.5 Create Promo Code
```http
POST /api/partners/events/123/promo-codes
Authorization: Bearer <partner_token>
Content-Type: application/json

{
  "code": "EARLYBIRD",
  "discount_type": "percentage",
  "discount_value": 20,
  "max_uses": 100,
  "valid_from": "2024-12-01T00:00:00",
  "valid_until": "2024-12-15T23:59:59"
}

Response 201:
{
  "message": "Promo code created successfully",
  "promo_code": { ... }
}
```

### 4.6 Get Event Attendees
```http
GET /api/partners/events/123/attendees?page=1
Authorization: Bearer <partner_token>

Response 200:
{
  "attendees": [
    {
      "booking_number": "NF-20241201-ABC123",
      "user": { ... },
      "quantity": 2,
      "is_checked_in": false,
      ...
    },
    ...
  ],
  "total": 50,
  "page": 1,
  "pages": 3
}
```

### 4.7 Export Attendees CSV
```http
GET /api/partners/events/123/attendees/export
Authorization: Bearer <partner_token>

Response 200:
Content-Type: text/csv
Content-Disposition: attachment; filename=attendees_123.csv

Booking Number,Name,Email,Phone,Quantity,Total Amount,Checked In,Booking Date
...
```

### 4.8 Request Payout
```http
POST /api/partners/payouts
Authorization: Bearer <partner_token>
Content-Type: application/json

{
  "amount": 10000.00,
  "payout_method": "mpesa"
}

Response 201:
{
  "message": "Payout request submitted successfully",
  "payout": {
    "reference_number": "PO-20241201-XYZ789",
    "amount": 10000.00,
    "status": "pending",
    ...
  }
}
```

---

## 5. Ticket & Booking APIs

### 5.1 Book Event
```http
POST /api/tickets/book
Authorization: Bearer <token>
Content-Type: application/json

{
  "event_id": 123,
  "ticket_type_id": 5,
  "quantity": 2,
  "promo_code": "EARLYBIRD"
}

Response 201:
{
  "message": "Booking created. Please proceed to payment.",
  "booking": { ... },
  "requires_payment": true,
  "amount": 8000.00
}
```

### 5.2 Validate Promo Code
```http
POST /api/tickets/validate-promo
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "EARLYBIRD",
  "event_id": 123
}

Response 200:
{
  "valid": true,
  "promo_code": {
    "code": "EARLYBIRD",
    "discount_type": "percentage",
    "discount_value": 20
  }
}
```

### 5.3 Cancel Booking
```http
POST /api/tickets/bookings/456/cancel
Authorization: Bearer <token>

Response 200:
{
  "message": "Booking cancelled successfully"
}
```

### 5.4 Verify Ticket (Partner)
```http
GET /api/tickets/TKT-20241201-ABC123/verify
Authorization: Bearer <partner_token>

Response 200:
{
  "valid": true,
  "ticket": { ... },
  "booking": { ... },
  "attendee": { ... }
}
```

### 5.5 Check-in Ticket (Partner)
```http
POST /api/tickets/scan
Authorization: Bearer <partner_token>
Content-Type: application/json

{
  "qr_data": "TKT-20241201-ABC123"
}

Response 200:
{
  "success": true,
  "message": "Ticket checked in successfully",
  "ticket": { ... },
  "attendee": { ... }
}
```

---

## 6. Payment APIs

### 6.1 Initiate Payment
```http
POST /api/payments/initiate
Authorization: Bearer <token>
Content-Type: application/json

{
  "booking_id": 456,
  "phone_number": "+254712345678"
}

Response 200:
{
  "message": "Payment initiated. Please check your phone...",
  "payment_id": 789,
  "transaction_id": "NF-20241201120000-ABC123",
  "checkout_request_id": "ws_CO_01122024120000123"
}
```

### 6.2 Check Payment Status
```http
GET /api/payments/status/789
Authorization: Bearer <token>

Response 200:
{
  "payment": {
    "id": 789,
    "transaction_id": "NF-20241201120000-ABC123",
    "amount": 8000.00,
    "status": "completed",
    "mpesa_receipt_number": "QAR12345",
    ...
  },
  "booking": { ... }
}
```

### 6.3 Payment History
```http
GET /api/payments/history?page=1
Authorization: Bearer <token>

Response 200:
{
  "payments": [ ... ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

---

## 7. Admin APIs

### 7.1 Dashboard
```http
GET /api/admin/dashboard
Authorization: Bearer <admin_token>

Response 200:
{
  "stats": {
    "total_users": 1000,
    "total_partners": 50,
    "total_events": 200,
    "pending_partners": 5,
    "pending_events": 10,
    "total_revenue": 500000.00
  },
  "recent_users": [ ... ],
  "recent_partners": [ ... ],
  "recent_events": [ ... ]
}
```

### 7.2 Approve Partner
```http
POST /api/admin/partners/123/approve
Authorization: Bearer <admin_token>

Response 200:
{
  "message": "Partner approved successfully",
  "partner": { ... }
}
```

### 7.3 Reject Partner
```http
POST /api/admin/partners/123/reject
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "reason": "Incomplete business information"
}

Response 200:
{
  "message": "Partner rejected",
  "partner": { ... }
}
```

### 7.4 Approve Event
```http
POST /api/admin/events/456/approve
Authorization: Bearer <admin_token>

Response 200:
{
  "message": "Event approved successfully",
  "event": { ... }
}
```

### 7.5 Platform Analytics
```http
GET /api/admin/analytics?days=30
Authorization: Bearer <admin_token>

Response 200:
{
  "period_days": 30,
  "new_users": 150,
  "new_partners": 10,
  "new_events": 50,
  "new_bookings": 200,
  "revenue": 250000.00,
  "platform_fees": 17500.00,
  "top_categories": [ ... ],
  "top_partners": [ ... ]
}
```

### 7.6 Create Category
```http
POST /api/admin/categories
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "New Category",
  "description": "Description here",
  "display_order": 10
}

Response 201:
{
  "message": "Category created successfully",
  "category": { ... }
}
```

---

## Error Responses

All endpoints may return error responses:

```json
// 400 Bad Request
{
  "error": "field is required"
}

// 401 Unauthorized
{
  "error": "Invalid token"
}

// 403 Forbidden
{
  "error": "Account is suspended"
}

// 404 Not Found
{
  "error": "Resource not found"
}

// 409 Conflict
{
  "error": "Email already registered"
}

// 500 Internal Server Error
{
  "error": "An internal error occurred"
}
```

## Rate Limiting

API is rate limited to:
- 200 requests per day per IP
- 50 requests per hour per IP
- Special limits on auth endpoints (5-10 per hour)

Rate limit headers:
```
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 195
X-RateLimit-Reset: 1638360000
```

