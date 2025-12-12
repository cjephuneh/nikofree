from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User
from app.models.partner import Partner


def user_required(fn):
    """Decorator to require user authentication"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.status_code = 200
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
            return response
        
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                response = jsonify({'msg': 'Invalid authentication token'})
                response.status_code = 401
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            user = User.query.get(current_user_id)
            
            if not user:
                response = jsonify({'msg': 'User not found'})
                response.status_code = 404
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            if not user.is_active:
                response = jsonify({'msg': 'Account is deactivated'})
                response.status_code = 403
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            return fn(current_user=user, *args, **kwargs)
        except Exception as e:
            from flask import current_app
            # Check if it's a JWT-related error (expired, invalid, malformed, etc.)
            error_msg = str(e).lower()
            error_type = type(e).__name__.lower()
            
            # Handle "Not enough segments" error (malformed token)
            if 'not enough segments' in error_msg or 'decodeerror' in error_type:
                current_app.logger.debug(f'Malformed JWT token: {str(e)}')
                response = jsonify({'msg': 'Invalid authentication token. Please log in again.'})
                response.status_code = 401
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            # Handle expired tokens and other JWT errors gracefully (don't log as errors)
            if ('expired' in error_msg or 'expired' in error_type or 
                'token' in error_msg or 'jwt' in error_msg or 
                'unauthorized' in error_msg or 'signature' in error_msg or
                'decode' in error_msg):
                # Log at debug level instead of error level for expired/invalid tokens
                current_app.logger.debug(f'JWT authentication failed: {str(e)}')
                response = jsonify({'msg': 'Invalid or expired token. Please log in again.'})
                response.status_code = 401
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            # Log unexpected errors at error level
            current_app.logger.error(f'Error in user_required decorator: {str(e)}', exc_info=True)
            response = jsonify({'msg': 'Authentication failed'})
            response.status_code = 401
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
            return response
    
    return wrapper


def partner_required(fn):
    """Decorator to require partner authentication"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.status_code = 200
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
            return response
        
        try:
            verify_jwt_in_request()
            current_partner_id = get_jwt_identity()
            partner = Partner.query.get(current_partner_id)
            
            if not partner:
                response = jsonify({'error': 'Partner not found'})
                response.status_code = 404
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            if not partner.is_active:
                response = jsonify({'error': 'Account is suspended'})
                response.status_code = 403
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            if partner.status != 'approved':
                response = jsonify({'error': 'Account not approved yet'})
                response.status_code = 403
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
                
            return fn(current_partner=partner, *args, **kwargs)
        except Exception as e:
            from flask import current_app
            error_msg = str(e).lower()
            error_type = type(e).__name__.lower()
            
            if 'not enough segments' in error_msg or 'decodeerror' in error_type:
                current_app.logger.debug(f'Malformed JWT token: {str(e)}')
                response = jsonify({'error': 'Invalid authentication token. Please log in again.'})
                response.status_code = 401
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            if ('expired' in error_msg or 'expired' in error_type or 
                'token' in error_msg or 'jwt' in error_msg or 
                'unauthorized' in error_msg or 'signature' in error_msg or
                'decode' in error_msg):
                current_app.logger.debug(f'JWT authentication failed: {str(e)}')
                response = jsonify({'error': 'Invalid or expired token. Please log in again.'})
                response.status_code = 401
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            current_app.logger.error(f'Error in partner_required decorator: {str(e)}', exc_info=True)
            response = jsonify({'error': 'Authentication failed'})
            response.status_code = 401
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
            return response
    
    return wrapper


def admin_required(fn):
    """Decorator to require admin authentication"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.status_code = 200
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
            return response
        
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                response = jsonify({'error': 'Invalid authentication token'})
                response.status_code = 401
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            user = User.query.get(current_user_id)
            
            if not user:
                response = jsonify({'error': 'User not found'})
                response.status_code = 404
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            # Check if user is admin (you can add an is_admin field to User model)
            # For now, checking if email matches admin email from config
            from flask import current_app
            if user.email != current_app.config.get('ADMIN_EMAIL'):
                response = jsonify({'error': 'Admin access required'})
                response.status_code = 403
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
                
            return fn(current_admin=user, *args, **kwargs)
        except Exception as e:
            from flask import current_app
            # Check if it's a JWT-related error (expired, invalid, malformed, etc.)
            error_msg = str(e).lower()
            error_type = type(e).__name__.lower()
            
            # Handle "Not enough segments" error (malformed token)
            if 'not enough segments' in error_msg or 'decodeerror' in error_type:
                current_app.logger.debug(f'Malformed JWT token: {str(e)}')
                response = jsonify({'error': 'Invalid authentication token. Please log in again.'})
                response.status_code = 401
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            # Handle expired tokens and other JWT errors gracefully
            if ('expired' in error_msg or 'expired' in error_type or 
                'token' in error_msg or 'jwt' in error_msg or 
                'unauthorized' in error_msg or 'signature' in error_msg or
                'decode' in error_msg):
                current_app.logger.debug(f'JWT authentication failed: {str(e)}')
                response = jsonify({'error': 'Invalid or expired token. Please log in again.'})
                response.status_code = 401
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
                return response
            
            # Log unexpected errors at error level
            current_app.logger.error(f'Error in admin_required decorator: {str(e)}', exc_info=True)
            response = jsonify({'error': 'Authentication failed'})
            response.status_code = 401
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS,PATCH')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
            return response
    
    return wrapper


def optional_user(fn):
    """Decorator for optional user authentication"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            return fn(current_user=user, *args, **kwargs)
        except:
            return fn(current_user=None, *args, **kwargs)
    
    return wrapper

