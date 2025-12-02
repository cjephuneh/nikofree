from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.notification import Notification
from app.models.user import User
from app.models.partner import Partner
from app.utils.decorators import user_required, partner_required, admin_required
from app.utils.sms import (
    send_partner_approval_sms, 
    send_event_approval_sms, 
    send_event_notification_sms,
    send_event_rejection_sms,
    send_partner_rejection_sms,
    send_new_booking_sms_to_partner
)

bp = Blueprint('notifications', __name__)


def create_notification(user_id=None, partner_id=None, admin_id=None, title=None, message=None,
                       notification_type='general', event_id=None, booking_id=None,
                       action_url=None, action_text=None, send_email=False):
    """Helper function to create notification"""
    notification = Notification(
        user_id=user_id,
        partner_id=partner_id,
        admin_id=admin_id,
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
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(partner_id=current_partner.id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Safely convert notifications to dict
        notifications_list = []
        for notif in notifications.items:
            try:
                notifications_list.append(notif.to_dict())
            except Exception as e:
                # Skip notifications that can't be serialized
                print(f"Error serializing notification {notif.id}: {str(e)}")
                continue
        
        unread_count = Notification.query.filter_by(
            partner_id=current_partner.id,
            is_read=False
        ).count()
        
        return jsonify({
            'notifications': notifications_list,
            'total': notifications.total,
            'unread_count': unread_count,
            'page': notifications.page,
            'pages': notifications.pages
        }), 200
    except Exception as e:
        print(f"Error fetching partner notifications: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to fetch notifications',
            'message': str(e)
        }), 500


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


@bp.route('/admin', methods=['GET'])
@admin_required
def get_admin_notifications(current_admin):
    """Get admin notifications"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(admin_id=current_admin.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'notifications': [notif.to_dict() for notif in notifications.items],
        'total': notifications.total,
        'unread_count': Notification.query.filter_by(
            admin_id=current_admin.id,
            is_read=False
        ).count(),
        'page': notifications.page,
        'pages': notifications.pages
    }), 200


@bp.route('/admin/read-all', methods=['PUT'])
@admin_required
def mark_all_admin_read(current_admin):
    """Mark all admin notifications as read"""
    Notification.query.filter_by(
        admin_id=current_admin.id,
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
    # Send SMS notification
    send_partner_approval_sms(partner)


def notify_partner_rejected(partner, reason):
    """Send notification when partner is rejected"""
    create_notification(
        partner_id=partner.id,
        title='Application Update',
        message=f'Your partner application needs revision. Reason: {reason}',
        notification_type='rejection',
        action_url='/partner/apply',
        action_text='Reapply',
        send_email=True
    )
    # Send SMS notification
    send_partner_rejection_sms(partner, reason)


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
    # Send SMS notification to partner
    # Get partner using partner_id directly (more reliable than relationship)
    from app.models.partner import Partner
    partner = Partner.query.get(event.partner_id)
    if partner:
        print(f"📱 Sending event approval SMS to partner {partner.id} ({partner.business_name})")
        send_event_approval_sms(partner, event)
    else:
        print(f"⚠️ Partner not found for event {event.id} (partner_id: {event.partner_id})")


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
    # Send SMS notification to partner
    partner = event.organizer
    if partner:
        send_event_rejection_sms(partner, event, reason)


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
    # Send SMS notification to partner
    partner = event.organizer
    if partner:
        send_new_booking_sms_to_partner(partner, booking, event)


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
    # Send SMS reminder
    send_event_notification_sms(user, event, 'reminder')


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


@bp.route('/event/reminder', methods=['POST'])
@admin_required
def send_event_reminders(current_admin):
    """Send event reminders to users (can be called by scheduled task/cron)"""
    from app.models.event import Event
    from app.models.ticket import Booking
    from datetime import datetime, timedelta
    
    hours_before = request.json.get('hours_before', 24) if request.is_json else 24
    
    # Find events happening in the next 'hours_before' hours
    reminder_time = datetime.utcnow() + timedelta(hours=hours_before)
    time_window_start = datetime.utcnow() + timedelta(hours=hours_before - 1)
    time_window_end = datetime.utcnow() + timedelta(hours=hours_before + 1)
    
    # Get events in the time window
    events = Event.query.filter(
        Event.start_date >= time_window_start,
        Event.start_date <= time_window_end,
        Event.status == 'approved',
        Event.is_published == True
    ).all()
    
    reminders_sent = 0
    for event in events:
        # Get all confirmed bookings for this event
        bookings = Booking.query.filter_by(
            event_id=event.id,
            status='confirmed'
        ).all()
        
        for booking in bookings:
            if booking.user and booking.user.phone_number:
                try:
                    notify_event_reminder(booking.user, event, hours_before)
                    reminders_sent += 1
                except Exception as e:
                    print(f"Error sending reminder to user {booking.user.id}: {str(e)}")
    
    return jsonify({
        'message': f'Event reminders sent',
        'reminders_sent': reminders_sent,
        'events_processed': len(events)
    }), 200

