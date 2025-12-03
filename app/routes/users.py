from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from sqlalchemy import or_
from app import db, limiter
from app.models.user import User
from app.models.event import Event
from app.models.ticket import Booking
from app.models.notification import Notification
from app.utils.decorators import user_required
from app.utils.file_upload import upload_file

bp = Blueprint('users', __name__)


@bp.route('/profile', methods=['GET'])
@user_required
def get_profile(current_user):
    """Get current user profile"""
    return jsonify(current_user.to_dict(include_sensitive=True)), 200


@bp.route('/profile', methods=['PUT'])
@user_required
def update_profile(current_user):
    """Update user profile"""
    data = request.get_json()
    
    # Update allowed fields
    if data.get('first_name'):
        current_user.first_name = data['first_name'].strip()
    
    if data.get('last_name'):
        current_user.last_name = data['last_name'].strip()
    
    if data.get('phone_number') is not None:
        # Strip and normalize phone number
        phone_number = data['phone_number'].strip() if isinstance(data['phone_number'], str) else None
        if phone_number:  # Only process if not empty after stripping
            # Validate phone number
            from app.utils.validators import validate_phone
            if not validate_phone(phone_number):
                return jsonify({'error': 'Invalid phone number'}), 400
            
        # Check if phone is already taken
        existing = User.query.filter(
                User.phone_number == phone_number,
            User.id != current_user.id
        ).first()
        if existing:
            return jsonify({'error': 'Phone number already in use'}), 409
            current_user.phone_number = phone_number
        else:
            # Allow clearing phone number by setting to None
            current_user.phone_number = None
    
    if data.get('date_of_birth'):
        try:
            current_user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if data.get('location'):
        current_user.location = data['location']
    
    current_user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    }), 200


@bp.route('/profile/picture', methods=['POST'])
@user_required
def upload_profile_picture(current_user):
    """Upload profile picture"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    try:
        # Upload file
        file_path = upload_file(file, folder='profiles')
        
        if not file_path:
            return jsonify({'error': 'Failed to upload file'}), 500
        
        # Update user profile picture
        current_user.profile_picture = file_path
        db.session.commit()
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'profile_picture': file_path
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/bookings', methods=['GET'])
@limiter.exempt
@user_required
def get_bookings(current_user):
    """Get user's bookings"""
    # Get query parameters
    status = request.args.get('status')  # upcoming, past, cancelled
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Build query
    query = Booking.query.filter_by(user_id=current_user.id)
    
    # Filter by status
    if status == 'upcoming':
        query = query.join(Event).filter(
            Event.start_date > datetime.utcnow(),
            Booking.status == 'confirmed'
        )
    elif status == 'past':
        query = query.join(Event).filter(
            Event.start_date <= datetime.utcnow()
        )
    elif status == 'cancelled':
        query = query.filter(Booking.status == 'cancelled')
    elif status == 'pending':
        # Pending bookings are unpaid or failed bookings that haven't been cancelled
        # Include both 'unpaid' and 'failed' payment statuses since failed payments
        # are still pending and can be retried
        query = query.filter(
            Booking.status == 'pending',
            Booking.payment_status.in_(['unpaid', 'failed'])
        )
    
    # Order by date
    query = query.order_by(Booking.created_at.desc())
    
    # Paginate
    bookings = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'bookings': [booking.to_dict(include_event_stats=True) for booking in bookings.items],
        'total': bookings.total,
        'page': bookings.page,
        'pages': bookings.pages,
        'per_page': bookings.per_page
    }), 200


@bp.route('/bookings/<int:booking_id>', methods=['GET'])
@user_required
def get_booking(current_user, booking_id):
    """Get specific booking"""
    try:
        booking = Booking.query.filter_by(
            id=booking_id,
            user_id=current_user.id
        ).first()
        
        if not booking:
            return jsonify({'msg': 'Booking not found'}), 404
        
        booking_dict = booking.to_dict(include_event_stats=True)
        return jsonify({
            'booking': booking_dict
        }), 200
    except AttributeError as e:
        current_app.logger.error(f'Attribute error fetching booking {booking_id}: {str(e)}', exc_info=True)
        return jsonify({'msg': f'Failed to fetch booking: {str(e)}'}), 422
    except Exception as e:
        current_app.logger.error(f'Error fetching booking {booking_id}: {str(e)}', exc_info=True)
        return jsonify({'msg': f'Failed to fetch booking: {str(e)}'}), 500


@bp.route('/bucketlist', methods=['GET'])
@user_required
def get_bucketlist(current_user):
    """Get user's bucketlist/wishlist"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get all wishlist events (don't filter by published/approved so users can see all their liked events)
    # Users should be able to see events they liked even if they're pending or unpublished
    events = current_user.bucketlist.order_by(Event.start_date).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'events': [event.to_dict(include_stats=True) for event in events.items],
        'total': events.total,
        'page': events.page,
        'pages': events.pages
    }), 200


@bp.route('/bucketlist/<int:event_id>', methods=['POST'])
@user_required
def add_to_bucketlist(current_user, event_id):
    """Add event to bucketlist"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if event in current_user.bucketlist:
        return jsonify({'error': 'Event already in bucketlist'}), 409
    
    current_user.bucketlist.append(event)
    db.session.commit()
    
    return jsonify({'message': 'Event added to bucketlist'}), 200


@bp.route('/bucketlist/<int:event_id>', methods=['DELETE'])
@user_required
def remove_from_bucketlist(current_user, event_id):
    """Remove event from bucketlist"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if event not in current_user.bucketlist:
        return jsonify({'error': 'Event not in bucketlist'}), 404
    
    current_user.bucketlist.remove(event)
    db.session.commit()
    
    return jsonify({'message': 'Event removed from bucketlist'}), 200


@bp.route('/notifications', methods=['GET'])
@user_required
def get_notifications(current_user):
    """Get user notifications"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(user_id=current_user.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'notifications': [notif.to_dict() for notif in notifications.items],
        'total': notifications.total,
        'unread_count': Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count(),
        'page': notifications.page,
        'pages': notifications.pages
    }), 200


@bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@user_required
def mark_notification_read(current_user, notification_id):
    """Mark notification as read"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200


@bp.route('/notifications/read-all', methods=['PUT'])
@user_required
def mark_all_notifications_read(current_user):
    """Mark all notifications as read"""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({
        'is_read': True,
        'read_at': datetime.utcnow()
    })
    
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read'}), 200


@bp.route('/change-password', methods=['POST'])
@user_required
def change_password(current_user):
    """Change user password"""
    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    # Verify current password
    if not current_user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password
    from app.utils.validators import validate_password
    is_valid, error_msg = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Check if new password is same as current
    if current_user.check_password(data['new_password']):
        return jsonify({'error': 'New password must be different from current password'}), 400
    
    # Update password
    current_user.set_password(data['new_password'])
    current_user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Password changed successfully'
    }), 200


@bp.route('/search', methods=['GET'])
def search_users():
    """Search users (for event hosts)"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'error': 'Search query must be at least 2 characters'}), 400
    
    # Search by name or email
    users = User.query.filter(
        or_(
            User.first_name.ilike(f'%{query}%'),
            User.last_name.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%')
        ),
        User.is_active == True
    ).limit(10).all()
    
    return jsonify({
        'users': [{
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'profile_picture': user.profile_picture
        } for user in users]
    }), 200

