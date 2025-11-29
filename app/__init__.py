from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config

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
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    # Disable strict slashes to prevent redirects (must be before CORS)
    app.url_map.strict_slashes = False
    
    # Configure CORS to handle preflight requests properly
    # Exclude database files and other sensitive paths
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "https://niko-free.com", "https://www.niko-free.com"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                 "supports_credentials": False,
                 "max_age": 3600,
                 "expose_headers": ["Content-Type", "Authorization"]
             },
             r"/uploads/*": {
                 "origins": ["*"],
                 "methods": ["GET", "OPTIONS"],
                 "allow_headers": ["Content-Type"],
                 "supports_credentials": False,
                 "max_age": 86400  # 24 hours for static files
             },
             r"/sitemap.xml": {
                 "origins": ["*"],
                 "methods": ["GET", "OPTIONS"],
                 "allow_headers": ["Content-Type"],
                 "supports_credentials": False
             },
             r"/robots.txt": {
                 "origins": ["*"],
                 "methods": ["GET", "OPTIONS"],
                 "allow_headers": ["Content-Type"],
                 "supports_credentials": False
             }
         },
         supports_credentials=False,
         automatic_options=True)
    
    # Handle OPTIONS requests explicitly for all routes
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
            response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS,PATCH")
            response.headers.add('Access-Control-Max-Age', "3600")
            return response
    
    # Add CORS headers to all responses (including errors)
    @app.after_request
    def after_request(response):
        # Don't add CORS headers to database files or other sensitive paths
        if request.path.endswith('.db') or '/nikofree.db' in request.path:
            return response
        
        # Add CORS headers for API routes
        if request.path.startswith('/api/'):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
            response.headers.add('Access-Control-Max-Age', '3600')
        # Add CORS headers for uploads (images)
        elif request.path.startswith('/uploads/'):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        # Add CORS headers for SEO routes
        elif request.path in ['/sitemap.xml', '/robots.txt']:
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        
        return response
    limiter.init_app(app)
    
    # Register blueprints
    from app.routes import auth, users, partners, admin, events, tickets, payments, notifications, seo
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(partners.bp, url_prefix='/api/partners')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(events.bp, url_prefix='/api/events')
    app.register_blueprint(tickets.bp, url_prefix='/api/tickets')
    app.register_blueprint(payments.bp, url_prefix='/api/payments')
    app.register_blueprint(notifications.bp, url_prefix='/api/notifications')
    app.register_blueprint(seo.bp)  # SEO routes (sitemap.xml, robots.txt)
    
    # Serve static files from uploads folder
    from flask import send_file, abort
    import os
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files"""
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
            abort(404)  # Not found
        
        # Use send_file for nested paths with proper CORS headers
        response = make_response(send_file(file_path))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        response.headers.add('Cache-Control', 'public, max-age=86400')  # Cache for 24 hours
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

