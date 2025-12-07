# Switch to Port 587 (TLS) for Email Testing

## Quick Change

To test with port 587 instead of 465, update your `.env` file:

```env
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

Or set these environment variables before running the server:

```bash
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USE_SSL=False
python app.py
```

## Test Port 587

After updating, restart your server and test:

```bash
./test_email_port587.sh your-email@example.com
```

## Why Port 587?

- **Port 465**: Uses SSL (implicit encryption) - often blocked by firewalls
- **Port 587**: Uses TLS (STARTTLS) - sometimes less restricted

## Note

Port 587 might also be blocked, but it's worth testing. If both ports are blocked locally, you'll need to test on Azure where there are no firewall restrictions.

## After Testing

**For Production (Azure):**
- Use port 465 with SSL (more secure)
- Set in Azure App Settings:
  ```
  MAIL_PORT=465
  MAIL_USE_SSL=True
  MAIL_USE_TLS=False
  ```

**For Local Development:**
- Use `MAIL_SUPPRESS_SEND=True` to avoid connection errors

