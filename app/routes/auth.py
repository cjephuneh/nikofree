from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from datetime import datetime, timedelta
from app import db, limiter
from app.models.user import User
from app.models.partner import Partner
from app.utils.validators import validate_email, validate_phone, validate_password
from app.utils.email import send_welcome_email, send_password_reset_email
from app.utils.sms import send_welcome_sms, send_partner_welcome_sms, send_password_reset_sms
import secrets

bp = Blueprint('auth', __name__)


# ============ USER AUTHENTICATION ============

@bp.route('/register', methods=['POST'])
@limiter.limit("100 per hour")  # Increased from 5 to 100 per hour
def register():
    """Register new user with email and password"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    email = data['email'].lower().strip()
    
    # Validate email
    if not validate_email(email):
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Validate password
    is_valid, error_msg = validate_password(data['password'])
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Handle phone number - strip and normalize
    phone_number = None
    if data.get('phone_number'):
        phone_number = data['phone_number'].strip()
        if phone_number:  # Only process if not empty after stripping
            if not validate_phone(phone_number):
            return jsonify({'error': 'Invalid phone number'}), 400
        
            if User.query.filter_by(phone_number=phone_number).first():
            return jsonify({'error': 'Phone number already registered'}), 409
        else:
            phone_number = None  # Convert empty string to None
    
    # Create new user
    user = User(
        email=email,
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        phone_number=phone_number,
        oauth_provider='email'
    )
    user.set_password(data['password'])
    
    if data.get('date_of_birth'):
        try:
            user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except:
            pass
    
    db.session.add(user)
    db.session.commit()
    
    # Send welcome email
    send_welcome_email(user)
    
    # Send welcome SMS if phone number provided
    if user.phone_number:
        send_welcome_sms(user)
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@bp.route('/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """Login with email and password"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data['email'].lower().strip()
    
    # Find user
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate tokens
    expires_delta = timedelta(days=30) if data.get('keep_logged_in') else None
    access_token = create_access_token(identity=user.id, expires_delta=expires_delta)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password():
    """Request password reset - sends reset token via email"""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    email = data['email'].lower().strip()
    
    # Validate email format
    if not validate_email(email):
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Find user
    user = User.query.filter_by(email=email).first()
    
    # For security, always return success even if user doesn't exist
    if not user:
        return jsonify({'message': 'If an account with that email exists, a password reset link has been sent'}), 200
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    
    db.session.commit()
    
    # Send password reset email
    send_password_reset_email(user, reset_token)
    
    # Send password reset SMS if phone number provided
    if user.phone_number:
        send_password_reset_sms(user, reset_token)
    
    return jsonify({'message': 'If an account with that email exists, a password reset link has been sent'}), 200


@bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    """Reset password using token"""
    data = request.get_json()
    
    if not data.get('token') or not data.get('password'):
        return jsonify({'error': 'Token and new password are required'}), 400
    
    # Validate password
    is_valid, error_msg = validate_password(data['password'])
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Find user with valid token
    user = User.query.filter_by(reset_token=data['token']).first()
    
    if not user:
        return jsonify({'error': 'Invalid or expired reset token'}), 400
    
    # Check if token is expired
    if user.reset_token_expires < datetime.utcnow():
        return jsonify({'error': 'Reset token has expired. Please request a new one'}), 400
    
    # Update password
    user.set_password(data['password'])
    user.reset_token = None
    user.reset_token_expires = None
    
    db.session.commit()
    
    return jsonify({'message': 'Password has been reset successfully'}), 200


@bp.route('/google', methods=['POST'])
@limiter.limit("10 per hour")
def google_login():
    """Login/Register with Google"""
    data = request.get_json()
    
    if not data.get('token'):
        return jsonify({'error': 'Google token is required'}), 400
    
    try:
        # Verify Google token
        from flask import current_app
        idinfo = id_token.verify_oauth2_token(
            data['token'],
            google_requests.Request(),
            current_app.config['GOOGLE_CLIENT_ID']
        )
        
        # Get user info from token
        email = idinfo.get('email')
        google_id = idinfo.get('sub')
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        profile_picture = idinfo.get('picture')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                google_id=google_id,
                first_name=first_name,
                last_name=last_name,
                profile_picture=profile_picture,
                oauth_provider='google',
                is_verified=True,
                email_verified=True
            )
            db.session.add(user)
            db.session.commit()
            
            # Send welcome email
            send_welcome_email(user)
        else:
            # Update Google ID if not set
            if not user.google_id:
                user.google_id = google_id
                user.oauth_provider = 'google'
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid Google token'}), 401


@bp.route('/apple', methods=['POST'])
@limiter.limit("10 per hour")
def apple_login():
    """Login/Register with Apple"""
    data = request.get_json()
    
    if not data.get('token'):
        return jsonify({'error': 'Apple token is required'}), 400
    
    # TODO: Implement Apple Sign In verification
    # This requires decoding and verifying the JWT token from Apple
    # For now, returning a placeholder
    
    return jsonify({
        'error': 'Apple Sign In not yet implemented',
        'message': 'Please use email/Google login for now'
    }), 501


#
# ============ PARTNER AUTHENTICATION ============
#

@bp.route('/partner/apply', methods=['POST'])
@limiter.limit("3 per hour")
def partner_apply():
    """Apply to become a partner - awaits admin approval"""
    from app.utils.file_upload import upload_file
    import json
    
    # Get form data (multipart/form-data for file upload)
    business_name = request.form.get('business_name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    location = request.form.get('location')
    category_id = request.form.get('category_id')
    interests = request.form.get('interests')  # Optional, comma-separated or JSON array
    signature_name = request.form.get('signature_name')
    terms_accepted = request.form.get('terms_accepted')  # 'true' or 'false' string
    
    # Validate required fields
    if not all([business_name, email, phone_number, location, category_id, signature_name]):
        return jsonify({'error': 'business_name, email, phone_number, location, category_id, and signature_name are required'}), 400
    
    # Validate terms acceptance
    if terms_accepted != 'true':
        return jsonify({'error': 'You must accept the terms and conditions'}), 400
    
    email = email.lower().strip()
    
    # Validate email
    if not validate_email(email):
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Validate phone
    if not validate_phone(phone_number):
        return jsonify({'error': 'Invalid phone number'}), 400
    
    # Check if partner already exists
    existing = Partner.query.filter_by(email=email).first()
    if existing:
        if existing.status == 'pending':
            return jsonify({'error': 'Application already submitted and pending review'}), 409
        elif existing.status == 'approved':
            return jsonify({'error': 'Email already registered as partner'}), 409
        elif existing.status == 'rejected':
            return jsonify({'error': 'Previous application was rejected. Please contact support.'}), 409
    
    # Validate category exists
    from app.models.category import Category
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Invalid category'}), 400
    
    # Handle logo upload
    logo_path = None
    if 'logo' in request.files:
        file = request.files['logo']
        if file:
            try:
                logo_path = upload_file(file, folder='logos')
            except ValueError as e:
                return jsonify({'error': f'Logo upload error: {str(e)}'}), 400
    
    # Parse interests if provided
    interests_json = None
    if interests:
        try:
            # Try parsing as JSON array
            interests_list = json.loads(interests)
            interests_json = json.dumps(interests_list)
        except:
            # If not JSON, treat as comma-separated
            interests_list = [i.strip() for i in interests.split(',') if i.strip()]
            interests_json = json.dumps(interests_list)
    
    # Generate a temporary password (will be sent on approval)
    import secrets
    temp_password = secrets.token_urlsafe(12)
    
    # Create partner application
    partner = Partner(
        email=email,
        business_name=business_name.strip(),
        phone_number=phone_number,
        location=location,
        category_id=category_id,
        interests=interests_json,
        signature_name=signature_name.strip(),
        logo=logo_path,
        terms_accepted=True,
        terms_accepted_at=datetime.utcnow(),
        contract_accepted=True,
        contract_accepted_at=datetime.utcnow(),
        status='pending'  # Awaiting admin approval
    )
    
    # Set temporary password (will be sent in approval email)
    partner.set_password(temp_password)
    
    # Store temp password temporarily (you might want to encrypt this)
    partner.rejection_reason = f"TEMP_PASS:{temp_password}"  # Temporary storage
    
    db.session.add(partner)
    db.session.commit()
    
    # Send welcome SMS to partner
    send_partner_welcome_sms(partner)
    
    return jsonify({
        'message': 'Application submitted successfully! You will receive an email within 24 hours with login credentials if approved.',
        'application_id': partner.id,
        'status': 'pending'
    }), 201


@bp.route('/partner/register', methods=['POST'])
@limiter.limit("5 per hour")
def partner_register():
    """Register new partner"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'business_name', 'phone_number']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    email = data['email'].lower().strip()
    
    # Validate email
    if not validate_email(email):
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Validate password
    is_valid, error_msg = validate_password(data['password'])
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Validate phone
    if not validate_phone(data['phone_number']):
        return jsonify({'error': 'Invalid phone number'}), 400
    
    # Check if partner already exists
    if Partner.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Validate contract acceptance
    if not data.get('contract_accepted'):
        return jsonify({'error': 'You must accept the terms and conditions'}), 400
    
    # Create new partner
    partner = Partner(
        email=email,
        business_name=data['business_name'].strip(),
        phone_number=data['phone_number'],
        contact_person=data.get('contact_person'),
        category_id=data.get('category_id'),
        website=data.get('website'),
        contract_accepted=True,
        contract_accepted_at=datetime.utcnow(),
        status='pending'
    )
    partner.set_password(data['password'])
    
    db.session.add(partner)
    db.session.commit()
    
    # Send welcome SMS to partner
    send_partner_welcome_sms(partner)
    
    return jsonify({
        'message': 'Partner registration submitted. Please wait for admin approval (within 24 hours).',
        'partner': partner.to_dict()
    }), 201


@bp.route('/partner/login', methods=['POST'])
@limiter.limit("10 per hour")
def partner_login():
    """Partner login"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data['email'].lower().strip()
    
    # Find partner
    partner = Partner.query.filter_by(email=email).first()
    
    if not partner or not partner.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not partner.is_active:
        return jsonify({'error': 'Account is suspended'}), 403
    
    # Update last login
    partner.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=partner.id)
    refresh_token = create_refresh_token(identity=partner.id)
    
    return jsonify({
        'message': 'Login successful',
        'partner': partner.to_dict(include_sensitive=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


# ============ ADMIN AUTHENTICATION ============

@bp.route('/admin/login', methods=['POST'])
@limiter.limit("10 per hour")
def admin_login():
    """Admin login using admin email from configuration"""
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].lower().strip()

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    # Check if this user is allowed to be admin
    from flask import current_app
    admin_email = current_app.config.get('ADMIN_EMAIL')
    if not admin_email or user.email.lower() != admin_email.lower():
        return jsonify({'error': 'Admin access required'}), 403

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate tokens (reuse user JWTs)
    expires_delta = timedelta(days=30) if data.get('keep_logged_in') else None
    access_token = create_access_token(identity=user.id, expires_delta=expires_delta)
    refresh_token = create_refresh_token(identity=user.id)

    # Build response user object with is_admin flag for frontend
    user_data = user.to_dict(include_sensitive=True)
    user_data['is_admin'] = True

    return jsonify({
        'message': 'Login successful',
        'user': user_data,
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


# ============ TOKEN REFRESH ============

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token
    }), 200


@bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if token is valid"""
    current_user_id = get_jwt_identity()
    
    # Try to find user first
    user = User.query.get(current_user_id)
    if user:
        return jsonify({
            'valid': True,
            'user_type': 'user',
            'user': user.to_dict()
        }), 200
    
    # Try partner
    partner = Partner.query.get(current_user_id)
    if partner:
        return jsonify({
            'valid': True,
            'user_type': 'partner',
            'partner': partner.to_dict()
        }), 200
    
    return jsonify({'error': 'Invalid token'}), 401

