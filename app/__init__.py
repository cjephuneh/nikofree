from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os
import smtplib

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure logging - suppress SQLAlchemy verbose logs, keep requests and errors
    import logging
    from logging import StreamHandler
    
    # Suppress SQLAlchemy engine logs (INFO level shows all queries)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
    
    # Keep Flask request logs at INFO level
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    
    # Set app logger to INFO (for our custom logs)
    app.logger.setLevel(logging.INFO)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Patch Flask-Mail to support timeout (only if email sending is enabled)
    # Flask-Mail doesn't expose timeout directly, so we patch the connection method
    # Note: This is optional since MAIL_SUPPRESS_SEND=True prevents email sending anyway
    if not app.config.get('MAIL_SUPPRESS_SEND', False):
        try:
            import flask_mail
            # Try to patch the Connection class's _get_smtp method
            if hasattr(flask_mail, 'Connection') and hasattr(flask_mail.Connection, '_get_smtp'):
                original_get_smtp = flask_mail.Connection._get_smtp
                
                def patched_get_smtp(self):
                    """Patched SMTP creation with timeout"""
                    mail_timeout = app.config.get('MAIL_TIMEOUT', 10)
                    if self.mail.use_ssl:
                        return smtplib.SMTP_SSL(
                            self.mail.server, 
                            self.mail.port, 
                            timeout=mail_timeout
                        )
                    else:
                        smtp = smtplib.SMTP(
                            self.mail.server, 
                            self.mail.port, 
                            timeout=mail_timeout
                        )
                        if self.mail.use_tls:
                            smtp.starttls()
                        return smtp
                
                flask_mail.Connection._get_smtp = patched_get_smtp
        except (AttributeError, ImportError, TypeError):
            # If patching fails, silently continue (not critical if MAIL_SUPPRESS_SEND=True)
            pass
    # Disable strict slashes to prevent redirects (must be before CORS)
    app.url_map.strict_slashes = False
    
    # Configure CORS to allow all origins
    CORS(app, 
         resources={
             r"/*": {
                 "origins": "*",
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
                 "supports_credentials": False,
                 "max_age": 3600,
                 "expose_headers": ["Content-Type", "Authorization"]
             }
         },
         supports_credentials=False,
         automatic_options=True)
    
    # Add CORS headers to all responses (including errors)
    # This is a fallback to ensure CORS headers are always present
    @app.after_request
    def after_request(response):
        # Don't add CORS headers to database files or other sensitive paths
        if request.path.endswith('.db') or '/nikofree.db' in request.path:
            return response
        
        # Allow all origins for all routes
        if 'Access-Control-Allow-Origin' not in response.headers:
            response.headers['Access-Control-Allow-Origin'] = '*'
        
        # Add standard CORS headers for all routes
        if 'Access-Control-Allow-Headers' not in response.headers:
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Accept'
        if 'Access-Control-Allow-Methods' not in response.headers:
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
        if 'Access-Control-Max-Age' not in response.headers:
            response.headers['Access-Control-Max-Age'] = '3600'
        if 'Access-Control-Allow-Credentials' not in response.headers:
            response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response
    
    # Custom error handler for rate limiting (429 errors)
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Return JSON error for rate limit instead of HTML"""
        from flask import jsonify
        response = jsonify({
            'error': 'Too many requests. Please try again later.',
            'message': 'You have exceeded the rate limit. Please wait a moment before trying again.'
        })
        response.status_code = 429
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
        return response
    
    # Error handler for 500 errors - ensures CORS headers are always present
    @app.errorhandler(500)
    def internal_error_handler(e):
        """Handle 500 errors with CORS headers"""
        from flask import jsonify
        import traceback
        app.logger.error(f'Internal Server Error: {str(e)}')
        app.logger.error(traceback.format_exc())
        response = jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.'
        })
        response.status_code = 500
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
        return response
    
    # Error handler for other HTTP errors (404, 403, etc.) - ensures CORS headers
    @app.errorhandler(404)
    def not_found_handler(e):
        """Handle 404 errors with CORS headers"""
        from flask import jsonify
        response = jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found.'
        })
        response.status_code = 404
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
        return response
    
    @app.errorhandler(403)
    def forbidden_handler(e):
        """Handle 403 errors with CORS headers"""
        from flask import jsonify
        response = jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.'
        })
        response.status_code = 403
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
        return response
    
    limiter.init_app(app)
    
    # Register blueprints
    from app.routes import auth, users, partners, admin, events, tickets, payments, notifications, seo, messages
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(partners.bp, url_prefix='/api/partners')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(events.bp, url_prefix='/api/events')
    app.register_blueprint(tickets.bp, url_prefix='/api/tickets')
    app.register_blueprint(payments.bp, url_prefix='/api/payments')
    app.register_blueprint(notifications.bp, url_prefix='/api/notifications')
    app.register_blueprint(messages.bp, url_prefix='/api/messages')
    app.register_blueprint(seo.bp)  # SEO routes (sitemap.xml, robots.txt)
    
    # Serve static files from uploads folder
    from flask import send_file, abort
    
    @app.route('/uploads/<path:filename>', methods=['GET', 'OPTIONS'])
    def uploaded_file(filename):
        """Serve uploaded files"""
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Max-Age', '3600')
            return response
        # Block database files and other sensitive files - this prevents CORS issues
        if filename.endswith('.db') or '.db/' in filename or 'nikofree.db' in filename.lower():
            abort(403)  # Forbidden - don't serve database files
        
        # Block other sensitive file types that shouldn't be served
        blocked_extensions = ['.sql', '.env', '.py', '.log', '.key', '.pem', '.p12', '.config']
        if any(filename.lower().endswith(ext) for ext in blocked_extensions):
            abort(403)  # Forbidden
        
        # Get upload folder from config (default: 'uploads')
        upload_folder_name = app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # Resolve the upload folder path relative to the project root (not app directory)
        # Flask app.root_path points to the app directory, so we need to go up one level
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_folder = os.path.join(project_root, upload_folder_name)
        
        # Log upload folder path for debugging (only in development)
        if app.config.get('DEBUG', False):
            current_app.logger.debug(f"Upload folder: {upload_folder}")
            current_app.logger.debug(f"Requested filename: {filename}")
        
        # Handle nested paths like events/filename.jpg
        # filename will be something like "events/1H5A3558_b3e59fa0.JPG"
        file_path = os.path.join(upload_folder, filename)
        
        # Security: Ensure the path is within uploads folder (prevent directory traversal)
        upload_folder_abs = os.path.abspath(upload_folder)
        file_path_abs = os.path.abspath(file_path)
        
        if not file_path_abs.startswith(upload_folder_abs):
            abort(403)  # Forbidden
        
        # Check if file exists
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            # Log the missing file for debugging
            current_app.logger.warning(f"Image not found: {file_path} (requested: {filename})")
            abort(404)  # Not found
        
        # Use send_file for nested paths with proper CORS headers
        try:
            response = make_response(send_file(file_path))
        except Exception as e:
            current_app.logger.error(f"Error serving file {file_path}: {str(e)}", exc_info=True)
            abort(500)
        
        # CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        
        # Enhanced caching headers for better performance
        # Cache for 1 year (31536000 seconds) with revalidation
        response.headers.add('Cache-Control', 'public, max-age=31536000, immutable')
        response.headers.add('Expires', 'Thu, 31 Dec 2025 23:59:59 GMT')
        
        # Add ETag for cache validation
        import hashlib
        import time
        try:
            file_stat = os.stat(file_path)
            etag = hashlib.md5(f"{file_path}{file_stat.st_mtime}".encode()).hexdigest()
            response.headers.add('ETag', f'"{etag}"')
        except Exception:
            pass  # If stat fails, skip ETag
        
        # Add content type for better browser handling
        from mimetypes import guess_type
        content_type, _ = guess_type(file_path)
        if content_type:
            response.headers.add('Content-Type', content_type)
        else:
            # Default to image/jpeg if type can't be determined
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                response.headers.add('Content-Type', 'image/jpeg')
        
        return response
    
    # Block direct access to database files - prevents CORS issues
    @app.route('/nikofree.db', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    @app.route('/<path:path>.db', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def block_database_files(path=None):
        """Block access to database files"""
        abort(403)  # Forbidden
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Niko Free API is running'}, 200
    
    @app.route('/')
    def index():
        return {
            'name': 'Niko Free API',
            'version': '1.0.0',
            'status': 'active'
        }, 200
    
    return app

# For Azure Oryx auto-detection: export app instance when imported as 'app:app'
# This allows gunicorn to find the app when Oryx generates 'gunicorn app:app'
# The app is created with 'production' config by default for deployment
import os
_app_instance = create_app(os.getenv('FLASK_ENV', 'production'))
app = _app_instance

