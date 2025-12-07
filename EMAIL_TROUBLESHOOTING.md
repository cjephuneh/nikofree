# Email Troubleshooting Guide - Complete Fix

## Quick Diagnostic Steps

### Step 1: Check if Email is Suppressed

**The most common issue:** `MAIL_SUPPRESS_SEND=True` is blocking all emails.

**Check in Azure:**
1. Go to **Configuration** → **Application settings**
2. Look for `MAIL_SUPPRESS_SEND`
3. **MUST be `False` for production** (or not set at all)

**Check in Local:**
```bash
# In your .env file
MAIL_SUPPRESS_SEND=False  # NOT True!
```

### Step 2: Verify SMTP Credentials

**In Azure App Settings, verify:**
```
MAIL_SERVER=mail.niko-free.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=noreply@niko-free.com
MAIL_PASSWORD=your-actual-password-here
MAIL_DEFAULT_SENDER=noreply@niko-free.com
MAIL_SUPPRESS_SEND=False  # ⚠️ CRITICAL
```

### Step 3: Test SMTP Connection

Run the diagnostic script:
```bash
python email_diagnostic.py
```

This will test:
- ✅ Configuration values
- ✅ DNS resolution
- ✅ Port connectivity
- ✅ SMTP authentication
- ✅ Actual email send

### Step 4: Check Application Logs

**In Azure:**
```bash
az webapp log tail --name nikofree --resource-group your-resource-group
```

**Look for:**
- `📧 [EMAIL] Attempting to send email...`
- `✅ Email sent successfully...`
- `❌ Error sending email...`

### Step 5: Common Issues & Fixes

#### Issue 1: "Email suppressed" message
**Fix:** Set `MAIL_SUPPRESS_SEND=False` in Azure App Settings

#### Issue 2: "Connection timeout"
**Possible causes:**
- Firewall blocking port 465
- Wrong SMTP server
- Network issues

**Fixes:**
- Try port 587 with TLS: `MAIL_PORT=587`, `MAIL_USE_TLS=True`, `MAIL_USE_SSL=False`
- Verify SMTP server is correct: `nslookup mail.niko-free.com`
- Check Azure outbound firewall rules

#### Issue 3: "Authentication failed"
**Fix:** 
- Verify username/password in Azure App Settings
- Test login via webmail interface
- Check if password has special characters (may need URL encoding)

#### Issue 4: "Module not found" or import errors
**Fix:** 
- Ensure Flask-Mail is installed: `pip install Flask-Mail`
- Check `requirements.txt` includes `Flask-Mail==0.9.1`

## Quick Test Endpoint

Add this to `app/routes/admin.py` for testing:

```python
@bp.route('/test-email', methods=['POST'])
@admin_required
def test_email_endpoint(current_admin):
    """Test email sending"""
    from app.utils.email import send_email
    
    recipient = request.json.get('email', current_admin.email)
    
    try:
        send_email(
            subject="Email Test from Niko Free",
            recipient=recipient,
            html_body="<h1>Test Email</h1><p>If you see this, email is working!</p>"
        )
        return jsonify({
            'message': 'Test email sent',
            'recipient': recipient,
            'note': 'Check logs for delivery status'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

Then test:
```bash
curl -X POST https://your-app.azurewebsites.net/api/admin/test-email \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'
```

## Step-by-Step Fix Checklist

- [ ] `MAIL_SUPPRESS_SEND=False` in Azure App Settings
- [ ] `MAIL_SERVER` is correct (mail.niko-free.com)
- [ ] `MAIL_PORT` is correct (465 for SSL, 587 for TLS)
- [ ] `MAIL_USERNAME` is correct (noreply@niko-free.com)
- [ ] `MAIL_PASSWORD` is correct (no typos)
- [ ] `MAIL_USE_SSL=True` for port 465
- [ ] `MAIL_USE_TLS=False` for port 465 (or True for port 587)
- [ ] SMTP server is reachable (test with `telnet mail.niko-free.com 465`)
- [ ] Credentials work (test via webmail)
- [ ] Application logs show email attempts
- [ ] No firewall blocking outbound port 465/587

## Still Not Working?

1. **Check logs first** - they tell you exactly what's wrong
2. **Test SMTP manually** - use the diagnostic script
3. **Try alternative port** - switch to 587 with TLS
4. **Verify credentials** - login via webmail to confirm
5. **Check spam folder** - emails might be going there

## Need More Help?

Share these details:
1. Error message from logs
2. Configuration values (hide password)
3. Output from diagnostic script
4. Whether emails work via webmail interface

