# SendGrid Email Setup Guide

This application uses SendGrid for sending emails. Follow these steps to configure SendGrid.

## 1. Create a SendGrid Account

1. Go to [SendGrid](https://sendgrid.com/) and sign up for a free account
2. Verify your email address
3. Complete the account setup process

## 2. Create a SendGrid API Key

1. Log in to your SendGrid dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Give it a name (e.g., "Niko Free Production")
5. Select **Full Access** or **Restricted Access** (with Mail Send permissions)
6. Click **Create & View**
7. **Copy the API key immediately** - you won't be able to see it again!

## 3. Verify a Sender Email

1. Go to **Settings** → **Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in the form with your sender details:
   - **From Email**: `noreply@niko-free.com` (or your preferred email)
   - **From Name**: Niko Free (or your preferred name)
   - **Reply To**: Your support email
   - **Company Address**: Your business address
4. Click **Create**
5. Check your email and click the verification link

## 4. Configure Environment Variables

Add these to your `.env` file:

```bash
# SendGrid Email Configuration
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=apikey
MAIL_PASSWORD=your_sendgrid_api_key_here
MAIL_DEFAULT_SENDER=noreply@niko-free.com
MAIL_TIMEOUT=30
MAIL_DEBUG=False
MAIL_SUPPRESS_SEND=False
```

**Important Notes:**
- `MAIL_USERNAME` must be exactly `apikey` (this is literal, not your email)
- `MAIL_PASSWORD` should be your SendGrid API Key (not your email password)
- `MAIL_DEFAULT_SENDER` must be a verified sender email in SendGrid
- For local development, you can set `MAIL_SUPPRESS_SEND=True` to disable email sending

## 5. Test Email Sending

You can test email sending using the admin test endpoint:

```bash
# Get admin JWT token first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-admin-email@example.com", "password": "your-password"}'

# Then test email
curl -X POST http://localhost:8000/api/admin/test-email \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"email": "test@example.com"}'
```

## SendGrid SMTP Settings Summary

- **SMTP Server**: `smtp.sendgrid.net`
- **Port**: `587` (TLS) or `465` (SSL)
- **Username**: `apikey` (literal string)
- **Password**: Your SendGrid API Key
- **Encryption**: TLS (port 587) or SSL (port 465)

## Troubleshooting

### Email not sending?

1. **Check API Key**: Make sure your API key is correct and has Mail Send permissions
2. **Verify Sender**: Ensure your sender email is verified in SendGrid
3. **Check Logs**: Look for error messages in your application logs
4. **Test Connection**: Use the test email endpoint to verify configuration
5. **Check Rate Limits**: Free SendGrid accounts have daily sending limits (100 emails/day)

### Common Errors

- **Authentication failed**: Check that `MAIL_USERNAME=apikey` and `MAIL_PASSWORD` is your API key
- **Sender not verified**: Verify your sender email in SendGrid dashboard
- **Connection timeout**: Check firewall settings and network connectivity

## Production Deployment

For production (Azure, etc.):

1. Set environment variables in your hosting platform
2. Make sure `MAIL_SUPPRESS_SEND=False` (or not set)
3. Use a verified sender email that matches your domain
4. Monitor SendGrid dashboard for delivery statistics

## SendGrid Free Tier Limits

- **100 emails/day** (free tier)
- Upgrade to paid plans for higher limits
- Monitor usage in SendGrid dashboard

