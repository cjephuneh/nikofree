# Email Configuration Guide

## Recommended Secure Settings (Port 465 with SSL)

Based on your email provider's recommendations, use these settings in your `.env` file:

```env
# Secure SSL/TLS Settings (Recommended)
MAIL_SERVER=mail.niko-free.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=noreply@niko-free.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@niko-free.com

# For local development (ports blocked by firewall)
MAIL_SUPPRESS_SEND=True
```

## Alternative Non-SSL Settings (Port 587 with TLS)

If port 465 doesn't work, you can use port 587 (less secure, not recommended):

```env
# Non-SSL Settings (NOT Recommended)
MAIL_SERVER=mail.niko-free.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=noreply@niko-free.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@niko-free.com
```

## Local Development

Since SMTP ports (465, 587) are typically blocked by local firewalls/ISPs:

1. **Set `MAIL_SUPPRESS_SEND=True`** in your `.env` file
2. Emails will be suppressed locally (no errors, no sending)
3. You'll see: `📧 [DEV MODE] Email suppressed` in logs

## Production

1. **Set `MAIL_SUPPRESS_SEND=False`** (or remove it) in production `.env`
2. Use the secure settings (port 465 with SSL)
3. Emails will send normally from production server

## Testing

Run the SMTP connection test:
```bash
python test_smtp_connection.py
```

This will test:
- DNS resolution
- Port connectivity
- SMTP connection
- Authentication
