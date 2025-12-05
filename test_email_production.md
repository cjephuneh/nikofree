# Testing Email on Production Server

## Step 1: Update Production .env File

SSH into your production server and update the `.env` file:

```bash
# SSH into your production server
ssh user@your-production-server

# Navigate to your app directory
cd /path/to/nikofree-server

# Edit .env file
nano .env  # or use vim, vi, etc.
```

Update these settings in `.env`:

```env
# Production Email Settings (Secure SSL/TLS)
MAIL_SERVER=mail.niko-free.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=noreply@niko-free.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@niko-free.com

# IMPORTANT: Disable email suppression in production
MAIL_SUPPRESS_SEND=False
```

## Step 2: Test SMTP Connection

Upload the test script to your production server and run it:

```bash
# On production server
python test_smtp_connection.py
```

Expected output if working:
```
✅ DNS resolved: mail.niko-free.com -> 216.198.79.1
✅ Port 465 is open and reachable
✅ SMTP connection established
✅ Authentication successful
✅ All tests passed! SMTP server is reachable.
```

## Step 3: Test Email Sending

### Option A: Use Flask Shell

```bash
# On production server
cd /path/to/nikofree-server
source venv/bin/activate
flask shell
```

Then in the Flask shell:
```python
from app.utils.email import send_email

# Test email
send_email(
    subject="Test Email from Production",
    recipient="your-email@example.com",  # Use your real email
    html_body="<h1>Test Email</h1><p>This is a test email from production server.</p>"
)

# Check logs for success message
# You should see: ✅ Email sent successfully
```

### Option B: Create a Test Endpoint

Create a test route (temporary, remove after testing):

```python
# In app/routes/admin.py (or create test.py)
@bp.route('/test-email', methods=['POST'])
@admin_required
def test_email(current_admin):
    """Test email sending (temporary endpoint)"""
    from app.utils.email import send_email
    
    recipient = request.json.get('email', current_admin.email)
    
    try:
        send_email(
            subject="Production Email Test",
            recipient=recipient,
            html_body="""
            <h1>✅ Email Test Successful!</h1>
            <p>If you're reading this, emails are working correctly on production.</p>
            <p>Server: Production</p>
            <p>Time: """ + str(datetime.now()) + """</p>
            """
        )
        return jsonify({'message': 'Test email sent successfully', 'recipient': recipient}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

Then test via API:
```bash
curl -X POST http://your-production-server/api/admin/test-email \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'
```

## Step 4: Monitor Email Logs

Watch the application logs for email activity:

```bash
# If using systemd
sudo journalctl -u nikofree -f

# If using supervisor
sudo tail -f /var/log/nikofree/out.log

# If using gunicorn directly
tail -f /var/log/nikofree/access.log
```

Look for:
- `✅ Email sent successfully: [subject] to [recipient]`
- `❌ Error sending email: [error]` (if there are issues)

## Step 5: Test Real Email Functions

Test actual email functions in your app:

1. **Password Reset Email:**
   - Go to login page
   - Click "Forgot Password"
   - Enter your email
   - Check your inbox

2. **Welcome Email:**
   - Register a new test user
   - Check email inbox

3. **Booking Confirmation:**
   - Create a test booking
   - Check email inbox

## Troubleshooting

### If SMTP connection fails on production:

1. **Check firewall rules:**
   ```bash
   # Test port connectivity
   telnet mail.niko-free.com 465
   # or
   nc -zv mail.niko-free.com 465
   ```

2. **Check DNS resolution:**
   ```bash
   nslookup mail.niko-free.com
   dig mail.niko-free.com
   ```

3. **Check email credentials:**
   - Verify username/password in `.env`
   - Test login via webmail interface

4. **Check application logs:**
   ```bash
   tail -f /var/log/nikofree/error.log
   ```

### Common Issues:

- **Port 465 blocked:** Try port 587 with TLS
- **Authentication failed:** Check username/password
- **Connection timeout:** Check firewall/network rules
- **SSL errors:** Verify SSL certificate

## Cleanup

After testing, remove any test endpoints you created for security.

