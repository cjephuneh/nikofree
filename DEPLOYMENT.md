# Deployment Guide

## Prerequisites

- Server with Ubuntu 20.04+ or similar Linux distribution
- PostgreSQL 12+
- Python 3.9+
- Nginx (for reverse proxy)
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

## Option 1: Deploy on VPS (Digital Ocean, AWS EC2, etc.)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.9 python3.9-venv python3-pip postgresql postgresql-contrib nginx supervisor -y

# Install Redis (optional, for caching)
sudo apt install redis-server -y
```

### 2. PostgreSQL Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE nikofree;
CREATE USER nikofree_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nikofree TO nikofree_user;
\q
```

### 3. Application Setup

```bash
# Create app directory
sudo mkdir -p /var/www/nikofree
sudo chown $USER:$USER /var/www/nikofree

# Clone repository
cd /var/www/nikofree
git clone <your-repo-url> .

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
nano .env
# Add your production configuration
```

### 4. Environment Variables (.env)

```bash
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

DATABASE_URL=postgresql://nikofree_user:your_secure_password@localhost:5432/nikofree

FRONTEND_URL=https://yourdomain.com

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/auth/google/callback

# MPesa Production
MPESA_CONSUMER_KEY=your-production-consumer-key
MPESA_CONSUMER_SECRET=your-production-consumer-secret
MPESA_PASSKEY=your-production-passkey
MPESA_SHORTCODE=your-shortcode
MPESA_ENVIRONMENT=production
MPESA_CALLBACK_URL=https://api.yourdomain.com/api/payments/mpesa/callback

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Admin
ADMIN_EMAIL=admin@yourdomain.com
```

### 5. Initialize Database

```bash
source venv/bin/activate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed_db
flask create_admin
```

### 6. Gunicorn Setup

Create `/var/www/nikofree/gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

accesslog = "/var/log/nikofree/access.log"
errorlog = "/var/log/nikofree/error.log"
loglevel = "info"

daemon = False
```

Create log directory:
```bash
sudo mkdir -p /var/log/nikofree
sudo chown $USER:$USER /var/log/nikofree
```

### 7. Supervisor Configuration

Create `/etc/supervisor/conf.d/nikofree.conf`:

```ini
[program:nikofree]
directory=/var/www/nikofree
command=/var/www/nikofree/venv/bin/gunicorn -c gunicorn_config.py app:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/nikofree/err.log
stdout_logfile=/var/log/nikofree/out.log
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start nikofree
sudo supervisorctl status nikofree
```

### 8. Nginx Configuration

Create `/etc/nginx/sites-available/nikofree`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/nikofree_access.log;
    error_log /var/log/nginx/nikofree_error.log;

    # Max upload size
    client_max_body_size 16M;

    # Static files (uploads)
    location /uploads {
        alias /var/www/nikofree/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/nikofree /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal is set up automatically
# Test renewal:
sudo certbot renew --dry-run
```

### 10. Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

---

## Option 2: Deploy with Docker

### 1. Create Dockerfile

Already included in the project.

### 2. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: nikofree
      POSTGRES_USER: nikofree_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn -w 4 -b 0.0.0.0:8000 app:app
    volumes:
      - .:/app
      - ./uploads:/app/uploads
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

volumes:
  postgres_data:
```

### 3. Deploy

```bash
docker-compose up -d
docker-compose exec web flask db upgrade
docker-compose exec web flask seed_db
docker-compose exec web flask create_admin
```

---

## Option 3: Deploy on Heroku

### 1. Install Heroku CLI

```bash
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

### 2. Create Heroku App

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
```

### 3. Set Environment Variables

```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret
# ... set all other env vars
```

### 4. Deploy

```bash
git push heroku main
heroku run flask db upgrade
heroku run flask seed_db
heroku run flask create_admin
```

---

## Post-Deployment Checklist

- [ ] Database is set up and migrated
- [ ] Environment variables are configured
- [ ] SSL certificate is installed
- [ ] Firewall is configured
- [ ] Admin user is created
- [ ] Categories and locations are seeded
- [ ] Email sending is working
- [ ] MPesa callback URL is publicly accessible
- [ ] File uploads directory has correct permissions
- [ ] Logs are being written
- [ ] Backups are configured
- [ ] Monitoring is set up (Sentry, New Relic, etc.)
- [ ] Domain DNS is configured correctly

## Monitoring & Maintenance

### Database Backup

```bash
# Create backup
pg_dump -U nikofree_user nikofree > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U nikofree_user nikofree < backup_20241201.sql
```

### View Logs

```bash
# Application logs
sudo tail -f /var/log/nikofree/error.log
sudo tail -f /var/log/nikofree/access.log

# Nginx logs
sudo tail -f /var/log/nginx/nikofree_error.log

# Supervisor logs
sudo supervisorctl tail -f nikofree stderr
```

### Update Application

```bash
cd /var/www/nikofree
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo supervisorctl restart nikofree
```

## Troubleshooting

### Application won't start

```bash
# Check supervisor status
sudo supervisorctl status nikofree

# Check logs
sudo supervisorctl tail nikofree stderr

# Restart
sudo supervisorctl restart nikofree
```

### Database connection issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U nikofree_user -d nikofree -h localhost
```

### Nginx issues

```bash
# Test configuration
sudo nginx -t

# Check status
sudo systemctl status nginx

# Restart
sudo systemctl restart nginx
```

## Security Recommendations

1. **Use strong passwords** for database and admin accounts
2. **Keep software updated** regularly
3. **Enable fail2ban** to prevent brute force attacks
4. **Use environment variables** for all secrets
5. **Enable CORS** only for your frontend domain
6. **Set up rate limiting** on sensitive endpoints
7. **Monitor logs** for suspicious activity
8. **Regular backups** of database and uploads
9. **Use HTTPS** everywhere
10. **Keep API keys secure** (never commit to git)

## Performance Optimization

1. **Use caching** (Redis) for frequently accessed data
2. **Enable gzip compression** in Nginx
3. **Optimize database** queries and add indexes
4. **Use CDN** for static files
5. **Monitor performance** with APM tools
6. **Scale horizontally** by adding more workers
7. **Database connection pooling** in production
8. **Async task processing** for heavy operations (Celery)

