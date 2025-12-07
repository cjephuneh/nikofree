# Fix "ModuleNotFoundError: No module named 'app'" on Azure

## Problem
Gunicorn can't find the `app` or `wsgi` module, even though the files exist.

## Root Cause
The Python path or working directory isn't set correctly when gunicorn starts.

## Solution 1: Use Updated startup.sh (Recommended)

The `startup.sh` script has been updated to:
1. Set the working directory explicitly
2. Add the deployment directory to PYTHONPATH
3. Check for files before starting
4. Fallback from `wsgi.py` to `app.py`

**In Azure Portal:**
1. Go to **Configuration** → **General settings**
2. Set **Startup Command** to:
   ```
   bash startup.sh
   ```
3. **Save** and **Restart**

## Solution 2: Direct Command with Explicit Path

**In Azure Portal:**
1. Go to **Configuration** → **General settings**
2. Set **Startup Command** to:
   ```
   cd /home/site/wwwroot && export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH && gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
   ```
3. **Save** and **Restart**

## Solution 3: Use Python Path in Command

**In Azure Portal:**
1. Go to **Configuration** → **General settings**
2. Set **Startup Command** to:
   ```
   PYTHONPATH=/home/site/wwwroot gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --chdir /home/site/wwwroot --access-logfile - --error-logfile - wsgi:app
   ```
3. **Save** and **Restart**

## Solution 4: Verify Files Are Deployed

If files are missing, check via SSH/Kudu:

```bash
# SSH into Azure App Service
# Then run:
cd /home/site/wwwroot
ls -la

# Should see:
# - app.py
# - wsgi.py
# - app/ directory
# - config.py
# - requirements.txt
```

If files are missing:
1. **Redeploy** your application
2. Check **Deployment Center** logs for deployment errors
3. Verify files are committed to git and pushed

## Solution 5: Use Azure CLI

```bash
az webapp config set \
  --name nikofree \
  --resource-group your-resource-group \
  --startup-file "bash startup.sh"
```

## Debugging Steps

### 1. Check Current Startup Command
```bash
az webapp config show \
  --name nikofree \
  --resource-group your-resource-group \
  --query "linuxFxVersion"
```

### 2. Check Files via SSH
```bash
# SSH into Azure
az webapp ssh --name nikofree --resource-group your-resource-group

# Then:
cd /home/site/wwwroot
pwd
ls -la
python3 -c "import sys; print(sys.path)"
```

### 3. Test Import Manually
```bash
# In Azure SSH:
cd /home/site/wwwroot
python3 -c "import wsgi; print('wsgi.py found')"
python3 -c "import app; print('app.py found')"
```

### 4. Check Logs
```bash
# View real-time logs
az webapp log tail --name nikofree --resource-group your-resource-group
```

## Common Issues

### Issue: Files not deployed
**Solution:** Redeploy via GitHub Actions or Azure Portal Deployment Center

### Issue: Wrong working directory
**Solution:** Use `--chdir /home/site/wwwroot` or `cd` in startup command

### Issue: Python path not set
**Solution:** Add `export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH` to startup command

### Issue: Oryx build process
**Solution:** Check if Oryx is moving files. Verify deployment structure in logs.

## Recommended Final Configuration

**Startup Command:**
```
bash startup.sh
```

This uses the updated `startup.sh` which handles all edge cases automatically.

## Verify It's Working

After updating, check logs:
```bash
az webapp log tail --name nikofree --resource-group your-resource-group
```

You should see:
- `Starting gunicorn with wsgi.py...` or `Starting gunicorn with app.py...`
- `Booting worker with pid: XXXX`
- No `ModuleNotFoundError`

## Quick Test

Once running, test the API:
```bash
curl https://your-app.azurewebsites.net/api/health
# or
curl https://your-app.azurewebsites.net/api/events
```

If you get a response (even an error), the app is running!

