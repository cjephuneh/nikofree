from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.notification import Notification
from app.models.user import User
from app.models.partner import Partner
from app.utils.decorators import user_required, partner_required

bp = Blueprint('notifications', __name__)


def create_notification(user_id=None, partner_id=None, title=None, message=None,
                       notification_type='general', event_id=None, booking_id=None,
                       action_url=None, action_text=None, send_email=False):
    """Helper function to create notification"""
    notification = Notification(
        user_id=user_id,
        partner_id=partner_id,
        title=title,
        message=message,
        notification_type=notification_type,
        event_id=event_id,
        booking_id=booking_id,
        action_url=action_url,
        action_text=action_text,
        send_email=send_email
    )
    
    db.session.add(notification)
    db.session.commit()
    
    return notification


@bp.route('/user', methods=['GET'])
@user_required
def get_user_notifications(current_user):
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


@bp.route('/partner', methods=['GET'])
@partner_required
def get_partner_notifications(current_partner):
    """Get partner notifications"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(partner_id=current_partner.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'notifications': [notif.to_dict() for notif in notifications.items],
        'total': notifications.total,
        'unread_count': Notification.query.filter_by(
            partner_id=current_partner.id,
            is_read=False
        ).count(),
        'page': notifications.page,
        'pages': notifications.pages
    }), 200


@bp.route('/<int:notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Notification marked as read'
    }), 200


@bp.route('/read-all', methods=['PUT'])
@user_required
def mark_all_user_read(current_user):
    """Mark all user notifications as read"""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({
        'is_read': True,
        'read_at': datetime.utcnow()
    })
    
    db.session.commit()
    
    return jsonify({
        'message': 'All notifications marked as read'
    }), 200


@bp.route('/partner/read-all', methods=['PUT'])
@partner_required
def mark_all_partner_read(current_partner):
    """Mark all partner notifications as read"""
    Notification.query.filter_by(
        partner_id=current_partner.id,
        is_read=False
    ).update({
        'is_read': True,
        'read_at': datetime.utcnow()
    })
    
    db.session.commit()
    
    return jsonify({
        'message': 'All notifications marked as read'
    }), 200


@bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete notification"""
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({
        'message': 'Notification deleted'
    }), 200


# ============ NOTIFICATION HELPERS ============

def notify_booking_confirmed(booking):
    """Send notification when booking is confirmed"""
    create_notification(
        user_id=booking.user_id,
        title='Booking Confirmed!',
        message=f'Your booking for "{booking.event.title}" has been confirmed.',
        notification_type='booking',
        event_id=booking.event_id,
        booking_id=booking.id,
        action_url=f'/bookings/{booking.id}',
        action_text='View Booking',
        send_email=True
    )


def notify_partner_approved(partner):
    """Send notification when partner is approved"""
    create_notification(
        partner_id=partner.id,
        title='Partner Account Approved!',
        message='Your partner account has been approved. You can now start creating events.',
        notification_type='approval',
        action_url='/partner/dashboard',
        action_text='Go to Dashboard',
        send_email=True
    )


def notify_event_approved(event):
    """Send notification when event is approved"""
    create_notification(
        partner_id=event.partner_id,
        title='Event Approved!',
        message=f'Your event "{event.title}" has been approved and is now live.',
        notification_type='approval',
        event_id=event.id,
        action_url=f'/events/{event.id}',
        action_text='View Event',
        send_email=True
    )


def notify_event_rejected(event, reason):
    """Send notification when event is rejected"""
    create_notification(
        partner_id=event.partner_id,
        title='Event Update',
        message=f'Your event "{event.title}" needs revision. Reason: {reason}',
        notification_type='rejection',
        event_id=event.id,
        action_url=f'/partner/events/{event.id}/edit',
        action_text='Edit Event',
        send_email=True
    )


def notify_new_booking(event, booking):
    """Send notification to partner when new booking is made"""
    create_notification(
        partner_id=event.partner_id,
        title='New Booking!',
        message=f'You have a new booking for "{event.title}". {booking.quantity} ticket(s).',
        notification_type='booking',
        event_id=event.id,
        booking_id=booking.id,
        action_url=f'/partner/events/{event.id}/attendees',
        action_text='View Attendees'
    )


def notify_event_reminder(user, event, hours_before=24):
    """Send event reminder to user"""
    create_notification(
        user_id=user.id,
        title='Event Reminder',
        message=f'"{event.title}" is happening in {hours_before} hours!',
        notification_type='reminder',
        event_id=event.id,
        action_url=f'/events/{event.id}',
        action_text='View Event',
        send_email=True
    )


def notify_payment_completed(booking, payment):
    """Send notification to partner when payment is completed"""
    event = booking.event
    create_notification(
        partner_id=event.partner_id,
        title='Payment Received!',
        message=f'Payment of Ksh {payment.amount:,.2f} received for "{event.title}" booking.',
        notification_type='payment',
        event_id=event.id,
        booking_id=booking.id,
        action_url=f'/partner/events/{event.id}/attendees',
        action_text='View Booking',
        send_email=False
    )

