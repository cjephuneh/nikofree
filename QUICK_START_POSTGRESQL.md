# Quick Start: PostgreSQL Migration

## 1. Set Environment Variables

```bash
export PGHOST=nikofreedb.postgres.database.azure.com
export PGUSER=nikofreeadmin
export PGPORT=5432
export PGDATABASE=postgres
export PGPASSWORD="NiFree@2025!"
```

Or add to `.env`:
```env
PGHOST=nikofreedb.postgres.database.azure.com
PGUSER=nikofreeadmin
PGPORT=5432
PGDATABASE=postgres
PGPASSWORD=NiFree@2025!
BASE_URL=https://niko-free.com
```

## 2. Install Dependencies

```bash
pip install psycopg2-binary
```

## 3. Run Migration

```bash
python migrate_to_postgresql.py
```

The script will:
- ✅ Connect to both databases
- ✅ Create PostgreSQL schema
- ✅ Transfer all data
- ✅ Preserve relationships

## 4. Verify

After migration, restart your application. The app will automatically use PostgreSQL when environment variables are set.

## 5. Frontend Configuration

For production, set the frontend API URL:

```env
VITE_API_BASE_URL=https://niko-free.com
```

Images will automatically work because:
- Backend serves images via `/uploads/<path>` route
- Frontend `getImageUrl()` prepends `API_BASE_URL` to relative paths
- `BASE_URL` is set to `https://niko-free.com` in config

## Troubleshooting

**Connection Error?**
- Verify PostgreSQL environment variables
- Check firewall allows your IP
- Test: `psql -h $PGHOST -U $PGUSER -d $PGDATABASE`

**Images Not Loading?**
- Verify `BASE_URL` is set correctly
- Check `VITE_API_BASE_URL` in frontend
- Ensure `uploads/` directory exists and is accessible

**Migration Errors?**
- Check error messages for specific issues
- Verify foreign key constraints
- Review migration log output

