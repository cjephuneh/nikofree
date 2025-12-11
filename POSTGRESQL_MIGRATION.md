# PostgreSQL Migration Guide

This guide will help you migrate your data from SQLite to PostgreSQL and ensure images load correctly in production.

## Prerequisites

1. PostgreSQL database is set up and accessible
2. Environment variables are configured (see below)
3. All dependencies are installed

## Step 1: Set Environment Variables

Set the following environment variables for PostgreSQL connection:

```bash
export PGHOST=nikofreedb.postgres.database.azure.com
export PGUSER=nikofreeadmin
export PGPORT=5432
export PGDATABASE=postgres
export PGPASSWORD="NiFree@2025!"
```

Or add them to your `.env` file:

```env
PGHOST=nikofreedb.postgres.database.azure.com
PGUSER=nikofreeadmin
PGPORT=5432
PGDATABASE=postgres
PGPASSWORD=NiFree@2025!
```

## Step 2: Install PostgreSQL Dependencies

The `psycopg2-binary` package has been added to `requirements.txt`. Install it:

```bash
pip install psycopg2-binary
```

Or reinstall all dependencies:

```bash
pip install -r requirements.txt
```

## Step 3: Create PostgreSQL Schema

The migration script will automatically create the schema in PostgreSQL. However, you can also use Flask-Migrate:

```bash
# Initialize migrations (if not already done)
flask db init

# Create migration for PostgreSQL
flask db migrate -m "Initial PostgreSQL migration"

# Apply migrations
flask db upgrade
```

## Step 4: Run Data Migration

Run the migration script to transfer all data from SQLite to PostgreSQL:

```bash
python migrate_to_postgresql.py
```

The script will:
- Connect to both databases
- Create/update the PostgreSQL schema
- Transfer all data in the correct order (respecting foreign key dependencies)
- Skip records that already exist (to allow re-running)
- Show progress for each table

## Step 5: Update Application Configuration

The `config.py` has been updated to automatically use PostgreSQL when environment variables are set. The application will:

1. First check for `DATABASE_URL` environment variable
2. If not set, construct from individual PostgreSQL variables (`PGHOST`, `PGUSER`, etc.)
3. Fall back to SQLite only if PostgreSQL variables are not set

## Step 6: Verify Images in Production

### Backend Configuration

The `BASE_URL` in `config.py` is set to `https://niko-free.com` by default. This ensures all image URLs are generated correctly.

You can override it with an environment variable:

```env
BASE_URL=https://niko-free.com
```

### Frontend Configuration

The frontend uses `getImageUrl()` helper function which:
- Handles relative paths (e.g., `/uploads/events/image.jpg`)
- Handles full URLs (e.g., `https://example.com/image.jpg`)
- Prepends `API_BASE_URL` for relative paths

Make sure `API_BASE_URL` in `niko_free/src/config/api.ts` points to your production API:

```typescript
export const API_BASE_URL = process.env.VITE_API_BASE_URL || 'https://niko-free.com';
```

### Image Serving

Images are served via the `/uploads/<path:filename>` route in `app/__init__.py`. This route:
- Serves files from the `uploads/` directory
- Includes proper CORS headers
- Caches images for 24 hours
- Blocks sensitive files (`.db`, `.env`, etc.)

### Upload Directory Structure

Ensure your `uploads/` directory structure is preserved:
```
uploads/
├── events/
│   └── [event images]
├── partners/
│   └── [partner logos]
├── profiles/
│   └── [user profile pictures]
└── qrcodes/
    └── [QR code images]
```

## Step 7: Test the Migration

1. **Verify Data Transfer**:
   ```bash
   # Connect to PostgreSQL and check record counts
   psql -h nikofreedb.postgres.database.azure.com -U nikofreeadmin -d postgres
   ```

2. **Test Image Loading**:
   - Check that event images load correctly
   - Verify profile pictures display
   - Test partner logos
   - Ensure QR codes are accessible

3. **Test Application**:
   - Login/Registration
   - Event creation/editing
   - Ticket booking
   - Payment processing
   - All CRUD operations

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Verify PostgreSQL environment variables are set correctly
2. Check firewall rules allow connections from your IP
3. Verify PostgreSQL server is running and accessible
4. Test connection manually:
   ```bash
   psql -h nikofreedb.postgres.database.azure.com -U nikofreeadmin -d postgres
   ```

### Migration Errors

If migration fails:
1. Check error messages for specific table/record issues
2. Verify foreign key constraints are satisfied
3. Check for duplicate unique constraints
4. Review the migration log output

### Image Loading Issues

If images don't load:
1. Verify `BASE_URL` is set correctly
2. Check that `uploads/` directory exists and is accessible
3. Verify file permissions on uploaded files
4. Check CORS headers in browser console
5. Ensure `API_BASE_URL` in frontend matches your backend URL

### Schema Issues

If you get schema errors:
1. Run Flask-Migrate to ensure schema is up to date:
   ```bash
   flask db upgrade
   ```
2. Check that all migrations have been applied
3. Verify model definitions match database schema

## Rollback Plan

If you need to rollback to SQLite:

1. Update `config.py` to use SQLite:
   ```python
   SQLALCHEMY_DATABASE_URI = 'sqlite:///nikofree.db'
   ```

2. Restart the application

3. Your SQLite database should still be intact (migration doesn't delete it)

## Next Steps

After successful migration:

1. Update production environment variables
2. Restart the application
3. Monitor for any issues
4. Consider setting up database backups
5. Update deployment documentation

## Support

If you encounter issues:
1. Check application logs
2. Review PostgreSQL logs
3. Verify environment variables
4. Test database connectivity
5. Check image file permissions

