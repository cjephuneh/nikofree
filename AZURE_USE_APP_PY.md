# Using `python app.py` on Azure

## Problem
Azure can't find `app.py` when using `python app.py` as the startup command.

## Solution

### Step 1: Update app.py (Already Done ✅)

The `app.py` file has been updated to:
- Use Azure's `PORT` environment variable
- Disable debug mode in production
- Work correctly in Azure App Service

### Step 2: Ensure app.py is Deployed

Make sure `app.py` is in your repository root and committed:

```bash
# Check if app.py is tracked
git ls-files | grep app.py

# If not, add it
git add app.py
git commit -m "Ensure app.py is deployed"
git push
```

### Step 3: Set Startup Command in Azure

**Via Azure Portal:**
1. Go to **Azure Portal** → Your App Service (`nikofree`)
2. Navigate to: **Settings** → **Configuration** → **General settings**
3. Find **Startup Command** field
4. Set it to:
   ```
   python app.py
   ```
5. Click **Save**
6. **Restart** your App Service

**Via Azure CLI:**
```bash
az webapp config set \
  --name nikofree \
  --resource-group your-resource-group \
  --startup-file "python app.py"
```

### Step 4: Verify Deployment Structure

After deployment, `app.py` should be in `/home/site/wwwroot/`.

**Check via SSH/Kudu Console:**
```bash
# SSH into Azure
az webapp ssh --name nikofree --resource-group your-resource-group

# Then check:
cd /home/site/wwwroot
ls -la app.py
```

If `app.py` is missing:
1. **Redeploy** your application
2. Check **Deployment Center** → **Logs** for deployment errors
3. Verify `app.py` is committed to git

### Step 5: Check Logs

After restarting, check the logs:
```bash
az webapp log tail --name nikofree --resource-group your-resource-group
```

You should see:
- `Running on http://0.0.0.0:8000` (or the PORT Azure sets)
- No "can't open file" errors

## Important Notes

### ⚠️ Production Considerations

Using `python app.py` directly (Flask's development server) is **NOT recommended for production** because:
- It's single-threaded
- Not optimized for production workloads
- No worker processes
- Limited error handling

**For production, use gunicorn:**
```
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 app:app
```

However, if you specifically want to use `python app.py` for testing or development, it will work.

### Port Configuration

Azure App Service sets the `PORT` environment variable automatically. The updated `app.py` reads this:
- If `PORT` is set → uses that port
- If not set → defaults to 8000

### Environment Variables

Make sure these are set in **Azure App Settings**:
- `FLASK_ENV=production` (disables debug mode)
- `PORT` (automatically set by Azure, but you can override)
- All your other environment variables (database, email, etc.)

## Troubleshooting

### Issue: "can't open file '/home/site/wwwroot/app.py'"

**Solution:**
1. Verify `app.py` is in your repository root
2. Check it's committed: `git ls-files | grep app.py`
3. Redeploy the application
4. Check deployment logs for errors

### Issue: App starts but crashes

**Solution:**
1. Check application logs for Python errors
2. Verify all dependencies are installed (check `requirements.txt`)
3. Check environment variables are set correctly

### Issue: Port already in use

**Solution:**
- Azure sets `PORT` automatically - don't override it
- The updated `app.py` reads `PORT` from environment

## Quick Test

Once running, test the API:
```bash
curl https://your-app.azurewebsites.net/api/events
```

If you get a response, `app.py` is working!

## Alternative: Use Full Path

If Azure still can't find `app.py`, use the full path:

**Startup Command:**
```
cd /home/site/wwwroot && python app.py
```

This ensures you're in the right directory before running.

