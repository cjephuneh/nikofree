# Azure Storage Setup for Images

## Problem
Azure App Service uses **ephemeral storage**, which means:
- Files uploaded after deployment are lost on restart
- Files can be lost during scaling operations
- Only files committed to git persist

## Current Status
✅ Uploads folder (41MB) is tracked in git and should be deployed
✅ Deployment workflow includes uploads folder

## Solutions

### Option 1: Use Azure Blob Storage (Recommended)

Azure Blob Storage provides persistent, scalable storage for images.

#### Setup Steps:

1. **Create Azure Storage Account**
   ```bash
   az storage account create \
     --name nikofreestorage \
     --resource-group your-resource-group \
     --location canadacentral \
     --sku Standard_LRS
   ```

2. **Create Container**
   ```bash
   az storage container create \
     --name uploads \
     --account-name nikofreestorage \
     --public-access blob
   ```

3. **Get Connection String**
   ```bash
   az storage account show-connection-string \
     --name nikofreestorage \
     --resource-group your-resource-group
   ```

4. **Update Environment Variables in Azure Portal**
   - `AZURE_STORAGE_CONNECTION_STRING` = (connection string from step 3)
   - `AZURE_STORAGE_CONTAINER` = `uploads`

5. **Update Code**
   - Modify `app/utils/file_upload.py` to upload to Azure Blob Storage
   - Update image serving to use Blob Storage URLs

### Option 2: Use Azure Files (Persistent Mount)

Mount Azure Files as a persistent drive in your App Service.

#### Setup Steps:

1. **Create Azure File Share**
   ```bash
   az storage share create \
     --name uploads \
     --account-name nikofreestorage \
     --quota 10
   ```

2. **Mount in App Service**
   - Go to Azure Portal → App Service → Configuration → Path Mappings
   - Add new mount: `/uploads` → Azure Files share

3. **Update Code**
   - Set `UPLOAD_FOLDER` environment variable to `/uploads`

### Option 3: Keep Current Setup (Temporary)

For now, ensure all images are committed to git before deployment:

```bash
# Before deploying, commit all new images
git add uploads/
git commit -m "Add new images"
git push
```

## Quick Fix: Verify Images Are Deployed

1. **Check Azure App Service Files**
   - Go to Azure Portal → App Service → Advanced Tools (Kudu)
   - Navigate to `/home/site/wwwroot/uploads`
   - Verify files exist

2. **Test Image URL**
   ```
   https://nikofree-arhecnfueegrasf8.canadacentral-01.azurewebsites.net/uploads/events/[filename]
   ```

3. **Check Logs**
   - Look for "Image not found" warnings in Application Insights
   - Check for 404 errors on `/uploads/` routes

## Recommended: Migrate to Azure Blob Storage

For production, Azure Blob Storage is the best solution:
- ✅ Persistent storage (never lost)
- ✅ Scalable (unlimited storage)
- ✅ CDN integration available
- ✅ Cost-effective
- ✅ Better performance with CDN

See `app/utils/azure_storage.py` (to be created) for implementation.

