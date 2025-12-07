# Manual Test Email Endpoint - Step by Step

## Prerequisites

1. **Server must be running:**
   ```bash
   python app.py
   # or
   flask run
   ```

2. **Know your admin credentials:**
   - Default admin email: `admin@nikofree.com`
   - Default admin password: (whatever you set when creating admin)

## Step 1: Get Admin JWT Token

```bash
curl -X POST http://localhost:8000/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@nikofree.com",
    "password": "your-admin-password"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {...},
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "..."
}
```

**Copy the `access_token` value!**

## Step 2: Test Email Endpoint

Replace `YOUR_ACCESS_TOKEN` with the token from Step 1:

```bash
curl -X POST http://localhost:8000/api/admin/test-email \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com"
  }'
```

**Expected Response:**
```json
{
  "message": "Test email sent",
  "recipient": "your-email@example.com",
  "note": "Check your inbox and spam folder"
}
```

## Quick Script Method

Use the provided script:

```bash
# Test with default admin email
./test_email_local.sh

# Test with custom email
./test_email_local.sh your-email@example.com
```

## Troubleshooting

### Issue: "Login failed"
- Check admin email/password
- Make sure admin user exists (create with `flask create_admin`)
- Check server is running

### Issue: "Unauthorized" or "Admin access required"
- Make sure you're using `/api/auth/admin/login` (not regular login)
- Verify the email matches `ADMIN_EMAIL` in config

### Issue: Email not received
- Check server logs for email delivery status
- Check spam folder
- Remember: Email is sent asynchronously, may take a few seconds
- If `MAIL_SUPPRESS_SEND=True`, emails are suppressed (check logs for suppression message)

## One-Liner (if you know admin password)

```bash
# Replace admin@nikofree.com and password123 with your credentials
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nikofree.com","password":"password123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8000/api/admin/test-email \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com"}'
```

