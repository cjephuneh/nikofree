# Fix Azure App Service Startup Issue

## Problem
Azure is trying to run `python app.py` but the file isn't found or the app isn't starting correctly.

## Solution: Update Azure App Service Startup Command

### Method 1: Via Azure Portal (Recommended)

1. **Go to Azure Portal** → Your App Service
2. Navigate to: **Settings** → **Configuration** → **General settings**
3. Find **Startup Command** field
4. Set it to:
   ```
   gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
   ```
5. Click **Save**
6. Restart your App Service

### Method 2: Via Azure CLI

```bash
az webapp config set \
  --name your-app-name \
  --resource-group your-resource-group \
  --startup-file "gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app"
```

### Method 3: Use startup.sh Script

1. **Ensure `startup.sh` is in your repository root** (it already exists)
2. **Make it executable** (if deploying via Git):
   ```bash
   chmod +x startup.sh
   ```
3. **In Azure Portal** → **Configuration** → **General settings**
4. Set **Startup Command** to:
   ```
   bash startup.sh
   ```

### Method 4: Create .deployment File (For Git Deployments)

Create a `.deployment` file in your repository root:

```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

And ensure `startup.sh` is executable and in the root.

## Verify Your Deployment Structure

Your Azure deployment should have this structure in `/home/site/wwwroot`:

```
/home/site/wwwroot/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   └── utils/
├── app.py
├── wsgi.py
├── config.py
├── requirements.txt
├── startup.sh
└── .env (or App Settings configured)
```

## Check Current Configuration

### Via Azure Portal:
1. Go to **Configuration** → **General settings**
2. Check **Startup Command** field
3. Check **Stack settings** (Python version should match your `runtime.txt`)

### Via Azure CLI:
```bash
az webapp config show --name your-app-name --resource-group your-resource-group --query "linuxFxVersion"
```

## Alternative: Use app.py Directly

If you prefer to use `app.py` directly (not recommended for production), set startup command to:

```bash
python app.py
```

But ensure:
1. `app.py` is in the root of your deployment
2. The app binds to the correct port (Azure uses port from `PORT` env var or 8000)
3. Update `app.py` to use the port from environment:

```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
```

## Recommended Production Setup

**Best practice for Azure App Service:**

1. **Use gunicorn with wsgi.py** (already configured)
2. **Set startup command:**
   ```
   gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
   ```
3. **Configure App Settings:**
   - `FLASK_ENV=production`
   - `PORT=8000` (or let Azure set it automatically)
   - All your email/SMS/database settings

## Verify It's Working

After updating the startup command:

1. **Restart the App Service**
2. **Check Log Stream:**
   - Azure Portal → **Monitoring** → **Log stream**
   - You should see gunicorn starting up
3. **Check Application Logs:**
   - Look for: `Starting gunicorn` or `Booting worker`

## Troubleshooting

### If still getting "can't open file" error:

1. **Check file structure in Azure:**
   ```bash
   # Via SSH or Kudu Console
   ls -la /home/site/wwwroot/
   ```

2. **Verify wsgi.py exists:**
   ```bash
   cat /home/site/wwwroot/wsgi.py
   ```

3. **Check if gunicorn is installed:**
   ```bash
   pip list | grep gunicorn
   ```

### If gunicorn command not found:

1. **Ensure requirements.txt includes gunicorn** (it does)
2. **Redeploy your application** to install dependencies
3. **Or install manually via SSH:**
   ```bash
   pip install gunicorn
   ```

### If port binding fails:

Azure App Service automatically sets the `PORT` environment variable. Update your startup command to use it:

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
```

Or update `wsgi.py` to read the port:

```python
import os
port = int(os.getenv('PORT', 8000))
# Then use in gunicorn command or app.run()
```

## Quick Fix Command (One-liner)

### Option A: Use app.py (Recommended if wsgi.py not found)
```bash
az webapp config set \
  --name your-app-name \
  --resource-group your-resource-group \
  --startup-file "gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --chdir /home/site/wwwroot app:app" && \
az webapp restart --name your-app-name --resource-group your-resource-group
```

### Option B: Use wsgi.py with explicit path
```bash
az webapp config set \
  --name your-app-name \
  --resource-group your-resource-group \
  --startup-file "gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --chdir /home/site/wwwroot wsgi:app" && \
az webapp restart --name your-app-name --resource-group your-resource-group
```

Replace `your-app-name` and `your-resource-group` with your actual values.

## If wsgi.py is missing: Use app.py instead

If you're getting `ModuleNotFoundError: No module named 'wsgi'`, you can use `app.py` directly:

**In Azure Portal → Configuration → General settings → Startup Command:**
```
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --chdir /home/site/wwwroot app:app
```

This uses `app.py` which creates the Flask app instance.

