# Deploying Database File to Azure

Since the database file (`nikofree.db`) is in `.gitignore`, you have two options to deploy it:

## Option 1: Temporarily Commit the Database File (Quick)

1. Temporarily remove `*.db` from `.gitignore` or add an exception:
   ```bash
   # In .gitignore, change:
   # *.db
   # To:
   *.db
   !nikofree.db
   ```

2. Commit and push the database file:
   ```bash
   git add nikofree.db
   git commit -m "Add database file for deployment"
   git push
   ```

3. After deployment, you can remove it from git again if needed.

## Option 2: Manual Upload via Azure Portal

1. Deploy the application first (without database)
2. Use Azure Portal's SSH or Kudu console to upload the database file
3. Place it in `/home/site/wwwroot/nikofree.db`

## Option 3: Use Azure CLI to Upload Database

After deployment, upload the database file:
```bash
az webapp deployment source config-zip \
  --resource-group <your-resource-group> \
  --name nikofree \
  --src database.zip
```

Where `database.zip` contains `nikofree.db`.

## Recommended Approach

For production, it's better to:
1. Use a managed database service (Azure SQL Database, PostgreSQL)
2. Or set up automated backups and restore on deployment
3. Or use Azure File Share for persistent storage

For now, Option 1 is the quickest way to get your existing database deployed.

