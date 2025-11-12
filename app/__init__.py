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
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
             "supports_credentials": False,
             "max_age": 3600
         }},
         supports_credentials=False,
         automatic_options=True)
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

