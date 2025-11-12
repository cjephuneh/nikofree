# Postman Collection Guide

Complete guide to using the Niko Free API Postman collection.

## 📦 Files Included

1. **Niko_Free_API.postman_collection.json** - Complete API collection (79+ endpoints)
2. **Niko_Free_Local.postman_environment.json** - Local development environment
3. **Niko_Free_Production.postman_environment.json** - Production environment

---

## 🚀 Quick Setup

### Step 1: Import Collection

1. Open Postman
2. Click **Import** button (top left)
3. Drag and drop `Niko_Free_API.postman_collection.json`
4. Click **Import**

### Step 2: Import Environment

1. Click **Import** again
2. Import `Niko_Free_Local.postman_environment.json`
3. (Optional) Import `Niko_Free_Production.postman_environment.json`

### Step 3: Select Environment

1. Click the environment dropdown (top right)
2. Select **"Niko Free - Local"**

### Step 4: Start Your Backend

```bash
cd /Users/mac/Documents/code/nikofree-server
source venv/bin/activate
flask run
```

Your API should be running at `http://localhost:5000`

---

## 📋 Collection Structure

The collection is organized into 8 folders:

```
Niko Free API/
├── 0. Health Check (2 requests)
├── 1. Authentication (8 requests)
│   ├── User (4 requests)
│   └── Partner (2 requests)
├── 2. Users (12 requests)
├── 3. Events (10 requests)
├── 4. Partners (17 requests)
├── 5. Tickets & Booking (6 requests)
├── 6. Payments (5 requests)
├── 7. Admin (21 requests)
│   ├── Partners (6 requests)
│   ├── Events (4 requests)
│   ├── Users (1 request)
│   ├── Categories (3 requests)
│   ├── Locations (2 requests)
│   └── Payouts (2 requests)
└── 8. Notifications (6 requests)
```

---

## 🔑 Authentication Flow

### Option 1: User Authentication

1. **Register User**
   - Folder: `1. Authentication > User`
   - Request: `Register User`
   - This will automatically set `access_token` and `user_id`

2. **Or Login User**
   - Request: `Login User`
   - Automatically saves tokens

3. **Test Authentication**
   - Go to `2. Users > Get Profile`
   - Should return your user data

### Option 2: Partner Authentication

1. **Register Partner**
   - Request: `1. Authentication > Partner > Register Partner`

2. **Login Partner**
   - Request: `Login Partner`
   - Saves access token

3. **Test**
   - Go to `4. Partners > Get Dashboard`

### Option 3: Admin Authentication

1. Create admin user via CLI:
```bash
flask create_admin
```

2. Login as User with admin email
3. Use admin endpoints in folder `7. Admin`

---

## 🎯 Testing Workflow

### Complete User Journey (Attendee)

**Step 1: Health Check**
```
0. Health Check > Health Check
```
Expected: `{"status": "healthy"}`

**Step 2: Register & Login**
```
1. Authentication > User > Register User
```
✅ Auto-saves: `access_token`, `user_id`

**Step 3: Browse Events**
```
3. Events > List All Events
3. Events > Get Categories
3. Events > This Weekend Events
```

**Step 4: View Event Details**
```
3. Events > Get Event Details
```
⚠️ Update `event_id` variable first

**Step 5: Book Event**
```
5. Tickets & Booking > Book Event
```
Body example:
```json
{
  "event_id": 1,
  "ticket_type_id": 1,
  "quantity": 2
}
```
✅ Auto-saves: `booking_id`

**Step 6: Pay for Booking** (if paid event)
```
6. Payments > Initiate Payment
```
Body:
```json
{
  "booking_id": 1,
  "phone_number": "+254712345678"
}
```

**Step 7: View Your Bookings**
```
2. Users > Get Bookings
```

### Complete Partner Journey (Organizer)

**Step 1: Register Partner**
```
1. Authentication > Partner > Register Partner
```

**Step 2: Login Partner**
```
1. Authentication > Partner > Login Partner
```
✅ Auto-saves: `access_token`

**Step 3: View Dashboard**
```
4. Partners > Get Dashboard
```

**Step 4: Create Event**
```
4. Partners > Create Event
```
Body example:
```json
{
  "title": "Tech Meetup",
  "description": "Monthly tech meetup",
  "category_id": 12,
  "start_date": "2024-12-15T18:00:00",
  "venue_name": "iHub Nairobi",
  "is_free": true
}
```

**Step 5: Upload Event Poster**
```
4. Partners > Upload Event Poster
```
Select image file in Body > form-data

**Step 6: Add Ticket Types**
```
4. Partners > Create Ticket Type
```

**Step 7: Create Promo Code**
```
4. Partners > Create Promo Code
```

**Step 8: View Attendees**
```
4. Partners > Get Event Attendees
```

**Step 9: Check-in Attendees**
```
5. Tickets & Booking > Scan QR Code
```

### Admin Journey

**Step 1: Login as Admin**
```
1. Authentication > User > Login User
(Use admin credentials)
```

**Step 2: View Dashboard**
```
7. Admin > Get Dashboard
```

**Step 3: Approve Pending Partners**
```
7. Admin > Partners > List Partners (status=pending)
7. Admin > Partners > Approve Partner
```

**Step 4: Approve Pending Events**
```
7. Admin > Events > List Events (status=pending)
7. Admin > Events > Approve Event
```

**Step 5: View Analytics**
```
7. Admin > Analytics
```

---

## 🔧 Environment Variables

The collection uses these variables:

| Variable | Description | Auto-Set | Example |
|----------|-------------|----------|---------|
| `base_url` | API base URL | ❌ Manual | `http://localhost:5000` |
| `access_token` | JWT access token | ✅ Auto | From login/register |
| `refresh_token` | JWT refresh token | ✅ Auto | From login/register |
| `user_id` | Current user ID | ✅ Auto | From login/register |
| `event_id` | Current event ID | ⚠️ Manual | `1` |
| `booking_id` | Current booking ID | ✅ Auto | From book event |
| `partner_id` | Current partner ID | ⚠️ Manual | `1` |

### How to Update Variables

**Option 1: Via Postman UI**
1. Click 👁️ icon (top right)
2. Edit environment
3. Update values

**Option 2: Auto-Set (Recommended)**
- Login requests automatically save tokens
- Booking requests save booking_id
- Event details save event_id

---

## 💡 Pro Tips

### 1. Use Tests Tab
Some requests have **automatic scripts** that save variables:
- Login → Saves `access_token`
- Register → Saves `access_token` + `user_id`
- Book Event → Saves `booking_id`

### 2. Authorization
Most endpoints use **Bearer Token** auth:
- Collection-level auth is pre-configured
- Token: `{{access_token}}`
- Some endpoints (like browse events) don't need auth

### 3. Test Before Production
1. Test everything in **Local** environment
2. Switch to **Production** environment
3. Update `base_url` to your production URL

### 4. Common Patterns

**Pagination:**
```
?page=1&per_page=20
```

**Filtering:**
```
?status=pending&category=music&is_free=true
```

**Search:**
```
?search=concert&location=nairobi
```

### 5. File Uploads

For endpoints that upload files:
1. Select **Body** tab
2. Choose **form-data**
3. Key: `file`, Type: `File`
4. Select your file

Examples:
- Upload profile picture
- Upload partner logo
- Upload event poster

---

## 🐛 Troubleshooting

### Error: "Invalid token"
**Solution:** Login again to get fresh token
```
1. Authentication > User > Login User
```

### Error: "Event not found"
**Solution:** Update `event_id` variable
1. Get event ID from `3. Events > List All Events`
2. Set variable: `event_id = <actual_id>`

### Error: "Connection refused"
**Solution:** Start your backend
```bash
flask run
```

### Error: "Partner not approved"
**Solution:** Approve partner via admin
```
7. Admin > Partners > Approve Partner
```

### Error: "404 Not Found"
**Solution:** Check your `base_url`
- Local: `http://localhost:5000`
- Production: `https://api.nikofree.com`

---

## 📊 Testing Checklist

Use this to test all major features:

### User Features
- [ ] Register user
- [ ] Login user
- [ ] Get profile
- [ ] Browse events
- [ ] View event details
- [ ] Add to bucketlist
- [ ] Book free event
- [ ] Book paid event
- [ ] Make payment
- [ ] View bookings
- [ ] Get notifications

### Partner Features
- [ ] Register partner
- [ ] Login partner
- [ ] View dashboard
- [ ] Upload logo
- [ ] Create event
- [ ] Upload poster
- [ ] Add ticket types
- [ ] Create promo code
- [ ] View attendees
- [ ] Export attendees
- [ ] Check-in attendee
- [ ] Request payout

### Admin Features
- [ ] Login as admin
- [ ] View dashboard
- [ ] List pending partners
- [ ] Approve partner
- [ ] List pending events
- [ ] Approve event
- [ ] Feature event
- [ ] View analytics
- [ ] Approve payout
- [ ] View logs

### Payment Features
- [ ] Initiate payment
- [ ] Check payment status
- [ ] View payment history
- [ ] Pay for promotion

---

## 🔄 Example Workflows

### Test Complete Booking Flow

1. **Setup:** Login as user
2. **Browse:** Get all events
3. **Select:** Get event details (note event_id)
4. **Book:** Book the event
5. **Pay:** Initiate payment (if paid)
6. **Verify:** Check booking in user bookings

### Test Partner Event Creation

1. **Setup:** Register and login partner
2. **Wait:** Get approved by admin (or approve yourself)
3. **Create:** Create event
4. **Upload:** Add event poster
5. **Tickets:** Add ticket types
6. **Promo:** Create promo code
7. **Wait:** Event approval by admin
8. **Monitor:** Check attendees as bookings come in

### Test Admin Workflow

1. **Login:** As admin user
2. **Partners:** Approve pending partners
3. **Events:** Approve pending events
4. **Feature:** Feature top events
5. **Analytics:** View platform stats
6. **Payouts:** Process partner payouts

---

## 📝 Notes

- **Rate Limiting:** APIs are rate-limited (200/day, 50/hour)
- **File Size:** Max 16MB for uploads
- **Tokens:** Access tokens expire in 1 hour
- **Refresh:** Use refresh token to get new access token
- **Environment:** Always check which environment is selected

---

## 🆘 Support

**Issues with Collection:**
- Check `API_ENDPOINTS.md` for detailed documentation
- Review `README.md` for backend setup
- Ensure backend is running: `flask run`

**API Questions:**
- See `API_SUMMARY.md` for complete overview
- Check `FEATURES_CHECKLIST.md` for feature status

---

## ✨ Quick Commands

```bash
# Start backend
flask run

# Initialize DB (first time)
flask init_db
flask seed_db

# Create admin user
flask create_admin

# Check health
curl http://localhost:5000/health
```

---

**Happy Testing! 🚀**

All 79+ endpoints are ready to test in Postman.

