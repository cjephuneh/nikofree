import os
from urllib.parse import quote_plus
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Admin
    # Email address that is treated as the platform admin account
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@nikofree.com')
    
    # Database
    # PostgreSQL connection string format: postgresql://user:password@host:port/database
    # If DATABASE_URL is not set, construct from individual PostgreSQL environment variables
    if os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    else:
        # Construct from individual PostgreSQL environment variables
        pg_host = os.getenv('PGHOST', 'localhost')
        pg_port = os.getenv('PGPORT', '5432')
        pg_user = os.getenv('PGUSER', 'postgres')
        pg_password = os.getenv('PGPASSWORD', '')
        pg_database = os.getenv('PGDATABASE', 'postgres')
        
        if pg_host and pg_user and pg_database:
            # URL-encode password and other components to handle special characters
            pg_user_encoded = quote_plus(pg_user)
            pg_password_encoded = quote_plus(pg_password)
            pg_database_encoded = quote_plus(pg_database)
            SQLALCHEMY_DATABASE_URI = f"postgresql://{pg_user_encoded}:{pg_password_encoded}@{pg_host}:{pg_port}/{pg_database_encoded}"
        else:
            # Fallback to SQLite for local development if PostgreSQL vars not set
            SQLALCHEMY_DATABASE_URI = 'sqlite:///nikofree.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS - Allow Vite (5173) and React dev server (3000)
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173']
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Base URL for generating download links
    BASE_URL = os.getenv('BASE_URL', 'https://niko-free.com')
    
    # Email Configuration - SendGrid
    # Set these in .env file for security
    # SendGrid SMTP Settings:
    # - Server: smtp.sendgrid.net
    # - Port: 587 (TLS) or 465 (SSL)
    # - Username: apikey (this is literal, not your email)
    # - Password: Your SendGrid API Key (get from SendGrid dashboard)
    # - From Email: Your verified sender email in SendGrid
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))  # 587 for TLS (recommended), 465 for SSL
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'  # True for port 587 (TLS)
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False') == 'True'  # True for port 465 (SSL), False for port 587
    # SendGrid requires username to be 'apikey' (literal string)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'apikey')
    # MAIL_PASSWORD should be your SendGrid API Key (not your email password)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Set SENDGRID_API_KEY in .env file
    # This should be a verified sender email in your SendGrid account
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@niko-free.com')
    MAIL_SUPPRESS_SEND = os.getenv('MAIL_SUPPRESS_SEND', 'False') == 'True'  # Set to 'True' to disable emails in dev
    # SMTP timeout settings (in seconds)
    MAIL_TIMEOUT = int(os.getenv('MAIL_TIMEOUT', '30'))  # Connection timeout (increased for SendGrid)
    MAIL_DEBUG = os.getenv('MAIL_DEBUG', 'False') == 'True'  # Enable SMTP debug output 
    
    # SMS Configuration
    # Set SMS_SUPPRESS_SEND=False in production to enable SMS sending
    SMS_SUPPRESS_SEND = os.getenv('SMS_SUPPRESS_SEND', 'False') == 'True'  # Default: False (enabled), set to 'True' to disable
    
    # OAuth - Google Sign-In
    # Set these in .env file for security
    # Client ID: 1073896486118-9a3r6v5ek96l7gmai05de9mkt1pmo9f2.apps.googleusercontent.com
    # Client Secret: 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
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '1073896486118-9a3r6v5ek96l7gmai05de9mkt1pmo9f2.apps.googleusercontent.com')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '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')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
    
    APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID')
    APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID')
    APPLE_KEY_ID = os.getenv('APPLE_KEY_ID')
    APPLE_PRIVATE_KEY_PATH = os.getenv('APPLE_PRIVATE_KEY_PATH')
    
    # MPesa - Daraja Sandbox Credentials
    MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', 'wqhprq5SA5GDBM9xegDWJPQ20eZcEdG3LBN4UGXGw47D94Ay')
    MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', 'gBB3tVMdVG1d9GiMWgm493Iq1XyBNSPdOqGYdALNh9olB52Sum0pXlzTQICLRoVr')
    MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')  # Sandbox passkey
    MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '174379')  # Sandbox shortcode
    MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
    MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', 'https://nikofree-arhecnfueegrasf8.canadacentral-01.azurewebsites.net/api/payments/mpesa/callback')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'nikofree-uploads')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Business Logic
    PLATFORM_COMMISSION_RATE = float(os.getenv('PLATFORM_COMMISSION_RATE', '0.07'))
    PARTNER_APPROVAL_TIME = '24 hours'
    MAX_HOSTS_PER_EVENT = 2
    MAX_INTERESTS_PER_EVENT = 5
    PROMOTION_PRICE_PER_DAY = 400  # KES
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Disable SQL query logging


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Enable SMS in production
    SMS_SUPPRESS_SEND = os.getenv('SMS_SUPPRESS_SEND', 'False') == 'True'  # Disable only if explicitly set to 'True'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

