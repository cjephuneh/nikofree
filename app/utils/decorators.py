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
            return jsonify({}), 200
        
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                return jsonify({'msg': 'Invalid authentication token'}), 401
            
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'msg': 'User not found'}), 404
            
            if not user.is_active:
                return jsonify({'msg': 'Account is deactivated'}), 403
            
            return fn(current_user=user, *args, **kwargs)
        except Exception as e:
            from flask import current_app
            # Check if it's a JWT-related error (expired, invalid, malformed, etc.)
            error_msg = str(e).lower()
            error_type = type(e).__name__.lower()
            
            # Handle "Not enough segments" error (malformed token)
            if 'not enough segments' in error_msg or 'decodeerror' in error_type:
                current_app.logger.debug(f'Malformed JWT token: {str(e)}')
                return jsonify({'msg': 'Invalid authentication token. Please log in again.'}), 401
            
            # Handle expired tokens and other JWT errors gracefully (don't log as errors)
            if ('expired' in error_msg or 'expired' in error_type or 
                'token' in error_msg or 'jwt' in error_msg or 
                'unauthorized' in error_msg or 'signature' in error_msg or
                'decode' in error_msg):
                # Log at debug level instead of error level for expired/invalid tokens
                current_app.logger.debug(f'JWT authentication failed: {str(e)}')
                return jsonify({'msg': 'Invalid or expired token. Please log in again.'}), 401
            
            # Log unexpected errors at error level
            current_app.logger.error(f'Error in user_required decorator: {str(e)}', exc_info=True)
            return jsonify({'msg': 'Authentication failed'}), 401
    
    return wrapper


def partner_required(fn):
    """Decorator to require partner authentication"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        
        verify_jwt_in_request()
        current_partner_id = get_jwt_identity()
        partner = Partner.query.get(current_partner_id)
        
        if not partner:
            return jsonify({'error': 'Partner not found'}), 404
        
        if not partner.is_active:
            return jsonify({'error': 'Account is suspended'}), 403
        
        if partner.status != 'approved':
            return jsonify({'error': 'Account not approved yet'}), 403
            
        return fn(current_partner=partner, *args, **kwargs)
    
    return wrapper


def admin_required(fn):
    """Decorator to require admin authentication"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is admin (you can add an is_admin field to User model)
        # For now, checking if email matches admin email from config
        from flask import current_app
        if user.email != current_app.config.get('ADMIN_EMAIL'):
            return jsonify({'error': 'Admin access required'}), 403
            
        return fn(current_admin=user, *args, **kwargs)
    
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

