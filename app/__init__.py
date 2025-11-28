from flask import Flask
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
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "*"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
             "supports_credentials": False,
             "max_age": 3600,
             "expose_headers": ["Content-Type", "Authorization"]
         }},
         supports_credentials=False,
         automatic_options=True)
    
    # Add CORS headers to error responses
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
        return response
    limiter.init_app(app)
    
    # Register blueprints
    from app.routes import auth, users, partners, admin, events, tickets, payments, notifications
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(partners.bp, url_prefix='/api/partners')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(events.bp, url_prefix='/api/events')
    app.register_blueprint(tickets.bp, url_prefix='/api/tickets')
    app.register_blueprint(payments.bp, url_prefix='/api/payments')
    app.register_blueprint(notifications.bp, url_prefix='/api/notifications')
    
    # Serve static files from uploads folder
    from flask import send_file, abort
    import os
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files"""
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
        
        # Use send_file for nested paths
        return send_file(file_path)
    
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

