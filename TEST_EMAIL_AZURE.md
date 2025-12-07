# Testing Email on Azure Production Server

## Quick Test Guide for Azure App Service

### Method 1: Using Azure Cloud Shell / SSH (Recommended)

If you have SSH enabled on your Azure App Service:

```bash
# 1. Connect to your Azure App Service via SSH
# In Azure Portal: Your App Service → Development Tools → SSH
# Or use Azure CLI:
az webapp ssh --name your-app-name --resource-group your-resource-group

# 2. Navigate to your app directory
cd /home/site/wwwroot

# 3. Upload the test script (or create it directly)
# Option A: Create the script directly on server
cat > test_email_production.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
load_dotenv()

def test_email_config():
    print("=" * 60)
    print("Production Email Configuration Test")
    print("=" * 60)
    print()
    
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = os.getenv('MAIL_PORT', '465')
    mail_use_ssl = os.getenv('MAIL_USE_SSL', 'True') == 'True'
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_suppress = os.getenv('MAIL_SUPPRESS_SEND', 'False') == 'True'
    
    print("📧 Email Configuration:")
    print(f"   Server: {mail_server}")
    print(f"   Port: {mail_port}")
    print(f"   SSL: {mail_use_ssl}")
    print(f"   Username: {mail_username}")
    print(f"   Password: {'*' * len(mail_password) if mail_password else 'NOT SET'}")
    print(f"   Suppress Send: {mail_suppress}")
    print()
    
    if mail_suppress:
        print("⚠️  WARNING: MAIL_SUPPRESS_SEND=True")
        print("   → Set MAIL_SUPPRESS_SEND=False in Azure App Settings")
        return False
    
    try:
        import smtplib
        import socket
        
        print("1. Testing DNS resolution...")
        ip = socket.gethostbyname(mail_server)
        print(f"   ✅ DNS resolved: {mail_server} -> {ip}")
        print()
        
        print("2. Testing port connectivity...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((mail_server, int(mail_port)))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Port {mail_port} is open and reachable")
        else:
            print(f"   ❌ Port {mail_port} is closed or unreachable")
            return False
        print()
        
        print("3. Testing SMTP connection...")
        if mail_use_ssl:
            smtp = smtplib.SMTP_SSL(mail_server, int(mail_port), timeout=10)
        else:
            smtp = smtplib.SMTP(mail_server, int(mail_port), timeout=10)
            if os.getenv('MAIL_USE_TLS', 'False') == 'True':
                smtp.starttls()
        
        print("   ✅ SMTP connection established")
        print()
        
        if mail_username and mail_password:
            print("4. Testing authentication...")
            smtp.login(mail_username, mail_password)
            print("   ✅ Authentication successful")
            print()
        
        smtp.quit()
        
        print("=" * 60)
        print("✅ All tests passed! Email configuration is correct.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == '__main__':
    test_email_config()
EOF

# 4. Make it executable
chmod +x test_email_production.py

# 5. Run the test
python3 test_email_production.py
```

### Method 2: Using Azure App Service Console (Kudu)

1. Go to Azure Portal → Your App Service
2. Navigate to: **Development Tools** → **Advanced Tools (Kudu)** → **Go**
3. Click **Debug console** → **CMD** or **PowerShell**
4. Navigate to your app directory: `cd site\wwwroot` (Windows) or `cd site/wwwroot` (Linux)
5. Create and run the test script as shown above

### Method 3: Test via Flask Shell (Most Reliable)

```bash
# 1. SSH into Azure App Service (see Method 1)

# 2. Activate Python environment (if using virtual env)
# Azure App Service usually has Python in the path already

# 3. Set environment variables (if not already set in App Settings)
export FLASK_APP=app
export FLASK_ENV=production

# 4. Run Flask shell
python3 -c "
from app import create_app
app = create_app('production')
with app.app_context():
    from app.utils.email import send_email
    print('Testing email...')
    send_email(
        subject='Test Email from Azure Production',
        recipient='your-email@example.com',  # Use your real email
        html_body='<h1>Test Email</h1><p>This is a test from Azure production server.</p>'
    )
    print('✅ Email sent! Check your inbox.')
"
```

### Method 4: Create a Temporary Test Endpoint

Add this to your `app/routes/admin.py` (temporary, remove after testing):

```python
@bp.route('/test-email', methods=['POST'])
@admin_required
def test_email(current_admin):
    """Test email sending (temporary endpoint - REMOVE AFTER TESTING)"""
    from app.utils.email import send_email
    from datetime import datetime
    
    recipient = request.json.get('email', current_admin.email)
    
    try:
        send_email(
            subject="Production Email Test - Azure",
            recipient=recipient,
            html_body=f"""
            <h1>✅ Email Test Successful!</h1>
            <p>If you're reading this, emails are working correctly on Azure production.</p>
            <p>Server: Azure App Service</p>
            <p>Time: {datetime.now()}</p>
            """
        )
        return jsonify({
            'message': 'Test email sent successfully', 
            'recipient': recipient
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

Then test via API:
```bash
curl -X POST https://your-app.azurewebsites.net/api/admin/test-email \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'
```

## Verify Azure App Settings

1. Go to Azure Portal → Your App Service → **Configuration** → **Application settings**
2. Verify these settings are set:

```
MAIL_SERVER=mail.niko-free.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=noreply@niko-free.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@niko-free.com
MAIL_SUPPRESS_SEND=False  # ⚠️ IMPORTANT: Must be False in production
MAIL_TIMEOUT=10
```

3. Click **Save** and restart your app service

## Check Application Logs

### Via Azure Portal:
1. Go to **Monitoring** → **Log stream** (real-time logs)
2. Or **Monitoring** → **App Service logs** → Download logs

### Via Azure CLI:
```bash
az webapp log tail --name your-app-name --resource-group your-resource-group
```

Look for:
- `✅ Email sent successfully: [subject] to [recipient]`
- `❌ Error sending email: [error]`

## Test Real Email Functions

1. **Password Reset:**
   - Go to `https://www.niko-free.com/login`
   - Click "Forgot Password"
   - Enter your email
   - Check inbox

2. **Booking Confirmation:**
   - Create a test booking
   - Check email inbox

3. **Partner Application:**
   - Submit a test partner application
   - Check email inbox

## Troubleshooting on Azure

### Issue: Connection Timeout
- **Check:** Azure App Service outbound IP restrictions
- **Solution:** Ensure port 465 is allowed in Azure Network Security Groups

### Issue: DNS Resolution Fails
- **Check:** Azure App Service DNS settings
- **Test:** `nslookup mail.niko-free.com` in Azure console

### Issue: Authentication Failed
- **Check:** Email credentials in Azure App Settings
- **Verify:** Login via webmail interface to confirm credentials work

### Issue: Port 465 Blocked
- **Try:** Port 587 with TLS instead:
  ```
  MAIL_PORT=587
  MAIL_USE_TLS=True
  MAIL_USE_SSL=False
  ```

## Quick Test Command (One-liner)

```bash
# SSH into Azure, then run:
python3 -c "from app import create_app; from app.utils.email import send_email; app = create_app('production'); app.app_context().push(); send_email('Test', 'your@email.com', '<h1>Test</h1>'); print('✅ Sent!')"
```

## Cleanup

After testing, **REMOVE** any test endpoints you created for security.

