from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db, limiter
from app.models.user import User
from app.models.partner import Partner, PartnerSupportRequest
from app.models.event import Event
from app.models.ticket import Booking
from app.models.payment import Payment, PartnerPayout
from app.models.category import Category, Location
from app.models.admin import AdminLog
from app.utils.decorators import admin_required
from app.utils.email import send_partner_approval_email, send_event_approval_email, send_partner_suspension_email, send_partner_activation_email, send_payout_approval_email, send_email
from app.routes.notifications import notify_event_approved, notify_event_rejected, notify_partner_approved, notify_partner_rejected
from app.utils.sms import send_partner_suspension_sms, send_partner_activation_sms, send_payout_approval_sms

bp = Blueprint('admin', __name__)


def log_admin_action(admin, action, resource_type, resource_id, description=None, changes=None):
    """Helper to log admin actions"""
    log = AdminLog(
        admin_id=admin.id,
        admin_email=admin.email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        changes=changes,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log)


@bp.route('/dashboard', methods=['GET'])
@limiter.exempt
@admin_required
def get_dashboard(current_admin):
    """Get admin dashboard overview"""
    try:
        # Get stats
        total_users = User.query.count()
        total_partners = Partner.query.filter_by(status='approved').count()
        total_events = Event.query.filter_by(status='approved').count()
        total_bookings = Booking.query.count()
        
        # Pending approvals - get details
        pending_partners_list = Partner.query.filter_by(status='pending').order_by(Partner.created_at.desc()).limit(5).all()
        pending_events_list = Event.query.filter_by(status='pending').order_by(Event.created_at.desc()).limit(5).all()
        
        pending_partners_count = Partner.query.filter_by(status='pending').count()
        pending_events_count = Event.query.filter_by(status='pending').count()
        
        # Revenue
        total_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        
        platform_fees = db.session.query(func.sum(Payment.platform_fee)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        
        # Recent activity - get recent users, partners, events
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_partners = Partner.query.order_by(Partner.created_at.desc()).limit(5).all()
        recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
        
        # Recent admin activity logs
        recent_admin_logs = AdminLog.query.order_by(AdminLog.created_at.desc()).limit(10).all()
        
        # Calculate month-over-month changes (simplified - last 30 days vs previous 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        
        users_this_month = User.query.filter(User.created_at >= thirty_days_ago).count()
        users_last_month = User.query.filter(
            User.created_at >= sixty_days_ago,
            User.created_at < thirty_days_ago
        ).count()
        users_change = ((users_this_month - users_last_month) / users_last_month * 100) if users_last_month > 0 else 0
        
        partners_this_month = Partner.query.filter(
            Partner.created_at >= thirty_days_ago,
            Partner.status == 'approved'
        ).count()
        partners_last_month = Partner.query.filter(
            Partner.created_at >= sixty_days_ago,
            Partner.created_at < thirty_days_ago,
            Partner.status == 'approved'
        ).count()
        partners_change = ((partners_this_month - partners_last_month) / partners_last_month * 100) if partners_last_month > 0 else 0
        
        events_this_month = Event.query.filter(
            Event.created_at >= thirty_days_ago,
            Event.status == 'approved'
        ).count()
        events_last_month = Event.query.filter(
            Event.created_at >= sixty_days_ago,
            Event.created_at < thirty_days_ago,
            Event.status == 'approved'
        ).count()
        events_change = events_this_month - events_last_month
        
        # Safely get category and partner names
        pending_partners_data = []
        for p in pending_partners_list:
            try:
                category_name = p.category.name if p.category else 'N/A'
            except:
                category_name = 'N/A'
            pending_partners_data.append({
                'id': p.id,
                'name': p.business_name,
                'email': p.email,
                'category': category_name,
                'submittedDate': p.created_at.isoformat() if p.created_at else '',
                'status': p.status
            })
        
        pending_events_data = []
        for e in pending_events_list:
            try:
                partner_name = e.organizer.business_name if e.organizer else 'N/A'
            except:
                partner_name = 'N/A'
            try:
                category_name = e.category.name if e.category else 'N/A'
            except:
                category_name = 'N/A'
            pending_events_data.append({
                'id': e.id,
                'title': e.title,
                'partner': partner_name,
                'category': category_name,
                'date': e.start_date.isoformat() if e.start_date else None,
                'status': e.status
            })
        
        response = jsonify({
            'stats': {
                'total_users': total_users,
                'total_partners': total_partners,
                'total_events': total_events,
                'total_bookings': total_bookings,
                'pending_partners': pending_partners_count,
                'pending_events': pending_events_count,
                'total_revenue': float(total_revenue),
                'platform_fees': float(platform_fees),
                'users_change': round(users_change, 1),
                'partners_change': round(partners_change, 1),
                'events_change': events_change
            },
            'pending_partners': pending_partners_data,
            'pending_events': pending_events_data,
            'recent_users': [user.to_dict() for user in recent_users],
            'recent_partners': [partner.to_dict() for partner in recent_partners],
            'recent_events': [event.to_dict() for event in recent_events],
            'recent_activity': [log.to_dict() for log in recent_admin_logs]
        })
        return response, 200
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        response = jsonify({'error': f'Internal server error: {error_msg}'})
        return response, 500


# ============ PARTNER MANAGEMENT ============

@bp.route('/partners/stats', methods=['GET'])
@admin_required
def get_partner_stats(current_admin):
    """Get partner statistics"""
    # Total partners
    total_partners = Partner.query.count()
    
    # Pending partners
    pending_partners = Partner.query.filter_by(status='pending').count()
    
    # Suspended partners
    suspended_partners = Partner.query.filter_by(status='suspended').count()
    
    # Active/Approved partners
    active_partners = Partner.query.filter_by(status='approved').count()
    
    return jsonify({
        'total_partners': total_partners,
        'pending_partners': pending_partners,
        'suspended_partners': suspended_partners,
        'active_partners': active_partners
    }), 200


@bp.route('/partners', methods=['GET'])
@admin_required
def get_partners(current_admin):
    """Get all partners"""
    status = request.args.get('status')  # pending, approved, rejected, suspended
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Partner.query
    
    if status:
        query = query.filter_by(status=status)
    
    partners = query.order_by(Partner.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Add event counts and revenue to each partner
    partners_data = []
    for partner in partners.items:
        partner_dict = partner.to_dict()
        # Count events for this partner
        event_count = Event.query.filter_by(partner_id=partner.id).count()
        partner_dict['total_events'] = event_count
        # Calculate total revenue from confirmed bookings
        total_revenue = db.session.query(func.sum(Booking.total_amount)).join(Event).filter(
            Event.partner_id == partner.id,
            Booking.status == 'confirmed'
        ).scalar() or 0
        partner_dict['total_revenue'] = float(total_revenue)
        partners_data.append(partner_dict)
    
    return jsonify({
        'partners': partners_data,
        'total': partners.total,
        'page': partners.page,
        'pages': partners.pages
    }), 200


@bp.route('/partners/<int:partner_id>', methods=['GET'])
@admin_required
def get_partner(current_admin, partner_id):
    """Get partner details"""
    partner = Partner.query.get(partner_id)
    
    if not partner:
        return jsonify({'error': 'Partner not found'}), 404
    
    # Get partner's events
    events = Event.query.filter_by(partner_id=partner_id).all()
    
    # Get earnings
    total_bookings = db.session.query(func.count(Booking.id)).join(Event).filter(
        Event.partner_id == partner_id,
        Booking.status == 'confirmed'
    ).scalar() or 0
    
    return jsonify({
        'partner': partner.to_dict(include_sensitive=True),
        'events': [event.to_dict(include_stats=True) for event in events],
        'total_bookings': total_bookings
    }), 200


@bp.route('/partners/<int:partner_id>/approve', methods=['POST'])
@admin_required
def approve_partner(current_admin, partner_id):
    """Approve partner application"""
    partner = Partner.query.get(partner_id)
    
    if not partner:
        return jsonify({'error': 'Partner not found'}), 404
    
    if partner.status != 'pending':
        return jsonify({'error': 'Partner is not pending approval'}), 400
    
    # Extract temporary password if stored, or generate new one
    import secrets
    temp_password = None
    if partner.rejection_reason and partner.rejection_reason.startswith('TEMP_PASS:'):
        temp_password = partner.rejection_reason.replace('TEMP_PASS:', '')
    else:
        # Generate new temporary password if not stored
        temp_password = secrets.token_urlsafe(12)
        partner.set_password(temp_password)
    
    partner.status = 'approved'
    partner.approved_by = current_admin.id
    partner.approved_at = datetime.utcnow()
    partner.is_verified = True
    partner.rejection_reason = None  # Clear the temp password field
    
    # Log action
    log_admin_action(
        current_admin,
        'approve_partner',
        'partner',
        partner_id,
        f"Approved partner: {partner.business_name}"
    )
    
    db.session.commit()
    
    # Send approval email with credentials
    send_partner_approval_email(partner, approved=True, temp_password=temp_password)
    
    # Send approval notification (includes SMS)
    notify_partner_approved(partner)
    
    return jsonify({
        'message': 'Partner approved successfully. Credentials sent to partner email.',
        'partner': partner.to_dict()
    }), 200


@bp.route('/partners/<int:partner_id>/reject', methods=['POST'])
@admin_required
def reject_partner(current_admin, partner_id):
    """Reject partner application"""
    partner = Partner.query.get(partner_id)
    
    if not partner:
        return jsonify({'error': 'Partner not found'}), 404
    
    data = request.get_json()
    reason = data.get('reason', 'Application does not meet requirements')
    
    partner.status = 'rejected'
    partner.rejection_reason = reason
    
    # Log action
    log_admin_action(
        current_admin,
        'reject_partner',
        'partner',
        partner_id,
        f"Rejected partner: {partner.business_name}. Reason: {reason}"
    )
    
    db.session.commit()
    
    # Send rejection email
    send_partner_approval_email(partner, approved=False)
    
    # Send rejection notification (includes SMS)
    notify_partner_rejected(partner, reason)
    
    return jsonify({
        'message': 'Partner rejected',
        'partner': partner.to_dict()
    }), 200


@bp.route('/partners/<int:partner_id>/suspend', methods=['POST'])
@admin_required
def suspend_partner(current_admin, partner_id):
    """Suspend partner account"""
    partner = Partner.query.get(partner_id)
    
    if not partner:
        return jsonify({'error': 'Partner not found'}), 404
    
    data = request.get_json()
    
    partner.status = 'suspended'
    partner.is_active = False
    
    # Log action
    log_admin_action(
        current_admin,
        'suspend_partner',
        'partner',
        partner_id,
        f"Suspended partner: {partner.business_name}"
    )
    
    db.session.commit()
    
    # Send suspension SMS and email to partner
    reason = data.get('reason')
    try:
        send_partner_suspension_sms(partner, reason)
    except Exception as sms_error:
        current_app.logger.warning(f'Failed to send suspension SMS: {str(sms_error)}')
    
    try:
        send_partner_suspension_email(partner, reason)
    except Exception as email_error:
        current_app.logger.warning(f'Failed to send suspension email: {str(email_error)}')
    
    return jsonify({
        'message': 'Partner suspended successfully'
    }), 200


@bp.route('/partners/<int:partner_id>/activate', methods=['POST'])
@admin_required
def activate_partner(current_admin, partner_id):
    """Activate suspended partner"""
    partner = Partner.query.get(partner_id)
    
    if not partner:
        return jsonify({'error': 'Partner not found'}), 404
    
    partner.status = 'approved'
    partner.is_active = True
    
    # Log action
    log_admin_action(
        current_admin,
        'activate_partner',
        'partner',
        partner_id,
        f"Activated partner: {partner.business_name}"
    )
    
    db.session.commit()
    
    # Send activation SMS and email to partner
    try:
        send_partner_activation_sms(partner)
    except Exception as sms_error:
        current_app.logger.warning(f'Failed to send activation SMS: {str(sms_error)}')
    
    try:
        send_partner_activation_email(partner)
    except Exception as email_error:
        current_app.logger.warning(f'Failed to send activation email: {str(email_error)}')
    
    return jsonify({
        'message': 'Partner activated successfully'
    }), 200


# ============ EVENT MANAGEMENT ============

@bp.route('/events/stats', methods=['GET'])
@admin_required
def get_event_stats(current_admin):
    """Get event statistics"""
    from datetime import datetime
    from sqlalchemy import and_, or_
    
    # Total events
    total_events = Event.query.count()
    
    # Free events
    free_events = Event.query.filter_by(is_free=True).count()
    
    # Paid events
    paid_events = Event.query.filter_by(is_free=False).count()
    
    # Multiday events (events with end_date that is different from start_date)
    now = datetime.utcnow()
    multiday_events = Event.query.filter(
        Event.end_date.isnot(None),
        Event.end_date != Event.start_date
    ).count()
    
    return jsonify({
        'total_events': total_events,
        'free_events': free_events,
        'paid_events': paid_events,
        'multiday_events': multiday_events
    }), 200


@bp.route('/events', methods=['GET'])
@admin_required
def get_events(current_admin):
    """Get all events"""
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Event.query
    
    if status:
        query = query.filter_by(status=status)
    
    events = query.order_by(Event.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Check if events are promoted
    from app.models.event import EventPromotion
    from datetime import datetime
    now = datetime.utcnow()
    
    events_data = []
    for event in events.items:
        event_dict = event.to_dict(include_stats=True)
        # Check if event has an active promotion
        active_promotion = EventPromotion.query.filter(
            EventPromotion.event_id == event.id,
            EventPromotion.is_active == True,
            EventPromotion.start_date <= now,
            EventPromotion.end_date >= now
        ).first()
        
        event_dict['is_promoted'] = active_promotion is not None
        if active_promotion:
            event_dict['promotion_id'] = active_promotion.id
        events_data.append(event_dict)
    
    return jsonify({
        'events': events_data,
        'total': events.total,
        'page': events.page,
        'pages': events.pages
    }), 200


@bp.route('/events/<int:event_id>/approve', methods=['POST'])
@admin_required
def approve_event(current_admin, event_id):
    """Approve event"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if event.status != 'pending':
        return jsonify({'error': 'Event is not pending approval'}), 400
    
    event.status = 'approved'
    event.approved_by = current_admin.id
    event.approved_at = datetime.utcnow()
    event.is_published = True
    event.published_at = datetime.utcnow()
    
    # Log action
    log_admin_action(
        current_admin,
        'approve_event',
        'event',
        event_id,
        f"Approved event: {event.title}"
    )
    
    db.session.commit()
    
    # Send approval email
    send_event_approval_email(event, approved=True)
    
    # Create notification for partner
    notify_event_approved(event)
    
    return jsonify({
        'message': 'Event approved successfully',
        'event': event.to_dict()
    }), 200


@bp.route('/events/<int:event_id>/reject', methods=['POST'])
@admin_required
def reject_event(current_admin, event_id):
    """Reject event"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    reason = data.get('reason', 'Event does not meet guidelines')
    
    event.status = 'rejected'
    event.rejection_reason = reason
    event.is_published = False
    
    # Log action
    log_admin_action(
        current_admin,
        'reject_event',
        'event',
        event_id,
        f"Rejected event: {event.title}. Reason: {reason}"
    )
    
    db.session.commit()
    
    # Send rejection email
    send_event_approval_email(event, approved=False)
    
    # Notify partner (includes SMS)
    notify_event_rejected(event, reason)
    
    return jsonify({
        'message': 'Event rejected',
        'event': event.to_dict()
    }), 200


@bp.route('/events/<int:event_id>/feature', methods=['POST'])
@admin_required
def feature_event(current_admin, event_id):
    """Feature event on homepage"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    event.is_featured = True
    
    # Log action
    log_admin_action(
        current_admin,
        'feature_event',
        'event',
        event_id,
        f"Featured event: {event.title}"
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Event featured successfully'
    }), 200


@bp.route('/events/<int:event_id>/promote', methods=['POST'])
@admin_required
def promote_event(current_admin, event_id):
    """Promote event (admin can promote for free)"""
    from app.models.event import EventPromotion
    from datetime import datetime, timedelta
    
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if event.status != 'approved':
        return jsonify({'error': 'Event must be approved before promotion'}), 400
    
    if not event.is_published:
        return jsonify({'error': 'Event must be published before promotion'}), 400
    
    data = request.get_json()
    days_count = data.get('days_count', 7)
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    is_free = data.get('is_free', True)  # Admin promotions are free by default
    
    # Parse dates
    if start_date_str and end_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_count)
    
    # Check for existing active promotion
    now = datetime.utcnow()
    existing_promo = EventPromotion.query.filter(
        EventPromotion.event_id == event_id,
        EventPromotion.is_active == True,
        EventPromotion.end_date >= now
    ).first()
    
    if existing_promo:
        return jsonify({
            'error': 'Event already has an active promotion',
            'promotion': existing_promo.to_dict()
        }), 400
    
    # Calculate cost (KES 400/day, but free for admin)
    cost_per_day = 400
    total_cost = days_count * cost_per_day
    
    # Create promotion
    promotion = EventPromotion(
        event_id=event_id,
        start_date=start_date,
        end_date=end_date,
        days_count=days_count,
        total_cost=total_cost,
        is_active=True,
        is_paid=not is_free
    )
    
    db.session.add(promotion)
    
    # Log action
    log_admin_action(
        current_admin,
        'promote_event',
        'event',
        event_id,
        f"Promoted event: {event.title} for {days_count} days"
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Event promoted successfully',
        'promotion': promotion.to_dict()
    }), 200


@bp.route('/events/<int:event_id>/unpromote', methods=['POST'])
@admin_required
def unpromote_event(current_admin, event_id):
    """Remove promotion from event"""
    from app.models.event import EventPromotion
    from datetime import datetime
    
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Find active promotion
    now = datetime.utcnow()
    promotion = EventPromotion.query.filter(
        EventPromotion.event_id == event_id,
        EventPromotion.is_active == True,
        EventPromotion.end_date >= now
    ).first()
    
    if not promotion:
        return jsonify({'error': 'No active promotion found for this event'}), 404
    
    # Deactivate promotion
    promotion.is_active = False
    
    # Log action
    log_admin_action(
        current_admin,
        'unpromote_event',
        'event',
        event_id,
        f"Removed promotion from event: {event.title}"
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Promotion removed successfully'
    }), 200


@bp.route('/promoted-events', methods=['GET', 'OPTIONS'])
@admin_required
def get_promoted_events(current_admin):
    """Get all promoted events for admin dashboard"""
    from app.models.event import EventPromotion
    
    # Get all promotions (active and inactive)
    promotions = EventPromotion.query.order_by(EventPromotion.created_at.desc()).all()
    
    now = datetime.utcnow()
    promotions_data = []
    
    for promo in promotions:
        event = promo.event
        if not event:
            continue
            
        # Calculate promotion status
        is_active_now = (
            promo.is_active and 
            promo.start_date <= now <= promo.end_date
        )
        
        event_dict = event.to_dict(include_stats=True) if event else {}
        
        promotion_dict = {
            'id': promo.id,
            'event_id': promo.event_id,
            'event': event_dict,
            'start_date': promo.start_date.isoformat(),
            'end_date': promo.end_date.isoformat(),
            'days_count': promo.days_count,
            'total_cost': float(promo.total_cost),
            'is_active': promo.is_active,
            'is_paid': promo.is_paid,
            'is_active_now': is_active_now,
            'created_at': promo.created_at.isoformat() if promo.created_at else None
        }
        
        promotions_data.append(promotion_dict)
    
    return jsonify({
        'promotions': promotions_data,
        'count': len(promotions_data)
    }), 200


# ============ USER MANAGEMENT ============

@bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_admin):
    """Get all users"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'page': users.page,
        'pages': users.pages
    }), 200


@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(current_admin, user_id):
    """Get user details with bookings and tickets"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's bookings
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    
    # Get all tickets for this user
    tickets = []
    events_booked = []
    
    for booking in bookings:
        # Get event details
        event = Event.query.get(booking.event_id)
        if event:
            events_booked.append({
                'id': event.id,
                'title': event.title,
                'date': event.start_date.isoformat() if event.start_date else None,
                'location': event.venue_name or event.venue_address or 'Location TBA',
                'booking_id': booking.id,
                'booking_number': booking.booking_number,
                'quantity': booking.quantity,
                'status': booking.status,
                'payment_status': booking.payment_status,
                'total_amount': float(booking.total_amount) if booking.total_amount else 0
            })
        
        # Get tickets for this booking
        booking_tickets = booking.tickets.all()
        for ticket in booking_tickets:
            ticket_type = ticket.ticket_type
            tickets.append({
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'event_id': event.id if event else None,
                'event_title': event.title if event else 'Unknown Event',
                'ticket_type': ticket_type.name if ticket_type else 'N/A',
                'price': float(ticket_type.price) if ticket_type and ticket_type.price else 0,
                'booking_id': booking.id,
                'booking_number': booking.booking_number,
                'status': booking.payment_status,
                'is_valid': ticket.is_valid,
                'is_scanned': ticket.is_scanned,  # Ticket has is_scanned, not is_checked_in
                'is_checked_in': booking.is_checked_in,  # Check-in status is on booking
                'scanned_at': ticket.scanned_at.isoformat() if ticket.scanned_at else None,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None
            })
    
    return jsonify({
        'user': user.to_dict(include_sensitive=True),
        'bookings': events_booked,
        'tickets': tickets,
        'total_bookings': len(bookings),
        'total_tickets': len(tickets),
        'confirmed_bookings': len([b for b in bookings if b.status == 'confirmed']),
        'total_spent': float(sum([b.total_amount for b in bookings if b.payment_status == 'paid' and b.total_amount])) or 0
    }), 200


# ============ CATEGORY & LOCATION MANAGEMENT ============

@bp.route('/categories', methods=['GET'])
@admin_required
def get_categories(current_admin):
    """Get all categories"""
    categories = Category.query.order_by(Category.display_order).all()
    return jsonify({
        'categories': [cat.to_dict() for cat in categories]
    }), 200


@bp.route('/categories', methods=['POST'])
@admin_required
def create_category(current_admin):
    """Create new category"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    
    # Generate slug
    from slugify import slugify
    slug = data.get('slug') or slugify(data['name'])
    
    # Check if slug exists
    if Category.query.filter_by(slug=slug).first():
        return jsonify({'error': 'Category slug already exists'}), 409
    
    category = Category(
        name=data['name'],
        slug=slug,
        description=data.get('description'),
        icon=data.get('icon'),
        display_order=data.get('display_order', 0)
    )
    
    db.session.add(category)
    
    # Log action
    log_admin_action(
        current_admin,
        'create_category',
        'category',
        None,
        f"Created category: {category.name}"
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Category created successfully',
        'category': category.to_dict()
    }), 201


@bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(current_admin, category_id):
    """Update category"""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    data = request.get_json()
    
    if data.get('name'):
        category.name = data['name']
    
    if data.get('description'):
        category.description = data['description']
    
    if data.get('icon'):
        category.icon = data['icon']
    
    if 'display_order' in data:
        category.display_order = data['display_order']
    
    if 'is_active' in data:
        category.is_active = data['is_active']
    
    category.updated_at = datetime.utcnow()
    
    # Log action
    log_admin_action(
        current_admin,
        'update_category',
        'category',
        category_id,
        f"Updated category: {category.name}"
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Category updated successfully',
        'category': category.to_dict()
    }), 200


@bp.route('/locations', methods=['GET'])
@admin_required
def get_locations(current_admin):
    """Get all locations"""
    locations = Location.query.order_by(Location.display_order).all()
    return jsonify({
        'locations': [loc.to_dict() for loc in locations]
    }), 200


@bp.route('/locations', methods=['POST'])
@admin_required
def create_location(current_admin):
    """Create new location"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    
    # Generate slug
    from slugify import slugify
    slug = data.get('slug') or slugify(data['name'])
    
    # Check if slug exists
    if Location.query.filter_by(slug=slug).first():
        return jsonify({'error': 'Location slug already exists'}), 409
    
    location = Location(
        name=data['name'],
        slug=slug,
        country=data.get('country', 'Kenya'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        display_order=data.get('display_order', 0)
    )
    
    db.session.add(location)
    
    # Log action
    log_admin_action(
        current_admin,
        'create_location',
        'location',
        None,
        f"Created location: {location.name}"
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Location created successfully',
        'location': location.to_dict()
    }), 201


# ============ ANALYTICS ============

@bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics(current_admin):
    """Get platform analytics"""
    # Date range
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # User growth
    new_users = User.query.filter(User.created_at >= start_date).count()
    
    # Partner growth
    new_partners = Partner.query.filter(Partner.created_at >= start_date).count()
    
    # Events
    new_events = Event.query.filter(Event.created_at >= start_date).count()
    
    # Bookings
    new_bookings = Booking.query.filter(Booking.created_at >= start_date).count()
    total_bookings = Booking.query.count()
    
    # Revenue
    revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.created_at >= start_date,
        Payment.status == 'completed'
    ).scalar() or 0
    
    platform_fees = db.session.query(func.sum(Payment.platform_fee)).filter(
        Payment.created_at >= start_date,
        Payment.status == 'completed'
    ).scalar() or 0
    
    # Top categories - be explicit about join conditions to avoid ambiguity
    top_categories = db.session.query(
        Category.name,
        func.count(Event.id).label('event_count')
    ).select_from(Category).join(
        Event, Event.category_id == Category.id
    ).group_by(Category.id, Category.name).order_by(desc('event_count')).limit(10).all()
    
    # Top partners - explicit joins: Partner -> Event -> Booking
    top_partners = db.session.query(
        Partner.business_name,
        func.count(Booking.id).label('booking_count'),
        func.sum(Booking.partner_amount).label('earnings')
    ).select_from(Partner).join(
        Event, Event.partner_id == Partner.id
    ).join(
        Booking, Booking.event_id == Event.id
    ).filter(
        Booking.status == 'confirmed'
    ).group_by(Partner.id, Partner.business_name).order_by(desc('booking_count')).limit(10).all()
    
    return jsonify({
        'period_days': days,
        'new_users': new_users,
        'new_partners': new_partners,
        'new_events': new_events,
        'new_bookings': new_bookings,
        'total_bookings': total_bookings,
        'revenue': float(revenue),
        'platform_fees': float(platform_fees),
        'top_categories': [{'name': cat[0], 'event_count': cat[1]} for cat in top_categories],
        'top_partners': [{
            'name': p[0],
            'booking_count': p[1],
            'earnings': float(p[2]) if p[2] else 0
        } for p in top_partners]
    }), 200


@bp.route('/analytics/charts', methods=['GET'])
@admin_required
def get_chart_data(current_admin):
    """Get chart data for reports with time filters"""
    period = request.args.get('period', 'all_time')  # today, 7_days, 30_days, all_time
    now = datetime.utcnow()
    
    # Calculate date ranges
    if period == 'today':
        start_date = datetime(now.year, now.month, now.day)
        group_by = 'hour'
    elif period == '7_days':
        start_date = now - timedelta(days=7)
        group_by = 'day'
    elif period == '30_days':
        start_date = now - timedelta(days=30)
        group_by = 'day'
    else:  # all_time
        start_date = None
        group_by = 'month'
    
    # Helper function to format date for grouping
    def format_date_for_group(date_obj, group_type):
        if group_type == 'hour':
            return date_obj.strftime('%Y-%m-%d %H:00')
        elif group_type == 'day':
            return date_obj.strftime('%Y-%m-%d')
        elif group_type == 'month':
            return date_obj.strftime('%Y-%m')
        return date_obj.strftime('%Y-%m-%d')
    
    # Events data
    events_query = Event.query
    if start_date:
        events_query = events_query.filter(Event.created_at >= start_date)
    events = events_query.all()
    
    events_data = {}
    for event in events:
        key = format_date_for_group(event.created_at, group_by)
        events_data[key] = events_data.get(key, 0) + 1
    
    # Partners data
    partners_query = Partner.query
    if start_date:
        partners_query = partners_query.filter(Partner.created_at >= start_date)
    partners = partners_query.all()
    
    partners_data = {}
    for partner in partners:
        key = format_date_for_group(partner.created_at, group_by)
        partners_data[key] = partners_data.get(key, 0) + 1
    
    # Users data
    users_query = User.query
    if start_date:
        users_query = users_query.filter(User.created_at >= start_date)
    users = users_query.all()
    
    users_data = {}
    for user in users:
        key = format_date_for_group(user.created_at, group_by)
        users_data[key] = users_data.get(key, 0) + 1
    
    # Revenue data
    revenue_query = Payment.query.filter(Payment.status == 'completed')
    if start_date:
        revenue_query = revenue_query.filter(Payment.created_at >= start_date)
    payments = revenue_query.all()
    
    revenue_data = {}
    for payment in payments:
        key = format_date_for_group(payment.created_at, group_by)
        revenue_data[key] = revenue_data.get(key, 0) + float(payment.amount)
    
    # Convert to sorted arrays with filled dates
    def create_chart_data(data_dict, group_type, start_dt=None, end_dt=None):
        items = []
        
        # If we have a date range, fill in missing dates
        if start_dt and end_dt:
            current = start_dt
            while current <= end_dt:
                if group_type == 'hour':
                    key = current.strftime('%Y-%m-%d %H:00')
                    label = current.strftime('%H:00')
                    # Move to next hour
                    current += timedelta(hours=1)
                    if current > end_dt:
                        break
                elif group_type == 'day':
                    key = current.strftime('%Y-%m-%d')
                    label = current.strftime('%b %d')
                    # Move to next day
                    current += timedelta(days=1)
                elif group_type == 'month':
                    key = current.strftime('%Y-%m')
                    label = current.strftime('%b %Y')
                    value = data_dict.get(key, 0)
                    items.append({
                        'date': key,
                        'label': label,
                        'value': value
                    })
                    # Move to next month
                    if current.month == 12:
                        next_month = datetime(current.year + 1, 1, 1)
                    else:
                        next_month = datetime(current.year, current.month + 1, 1)
                    # Check if next month would exceed end date
                    if next_month > end_dt:
                        break
                    current = next_month
                    continue
                else:
                    break
                
                value = data_dict.get(key, 0)
                items.append({
                    'date': key,
                    'label': label,
                    'value': value
                })
        else:
            # No date range, just use existing data
            for key, value in data_dict.items():
                if group_type == 'hour':
                    label = key.split(' ')[1] if ' ' in key else key  # Just the hour
                elif group_type == 'day':
                    date_obj = datetime.strptime(key, '%Y-%m-%d')
                    label = date_obj.strftime('%b %d')
                elif group_type == 'month':
                    date_obj = datetime.strptime(key, '%Y-%m')
                    label = date_obj.strftime('%b %Y')
                else:
                    label = key
                
                items.append({
                    'date': key,
                    'label': label,
                    'value': value
                })
            
            # Sort by date
            items.sort(key=lambda x: x['date'])
        
        return items
    
    # Calculate date ranges for filling
    end_date_for_fill = now
    start_date_for_fill = None
    
    if period == 'today':
        start_date_for_fill = datetime(now.year, now.month, now.day)
        end_date_for_fill = now
    elif period == '7_days':
        start_date_for_fill = now - timedelta(days=7)
    elif period == '30_days':
        start_date_for_fill = now - timedelta(days=30)
    else:  # all_time
        # For all_time, get the earliest event/partner/user date
        earliest_event = db.session.query(func.min(Event.created_at)).scalar()
        earliest_partner = db.session.query(func.min(Partner.created_at)).scalar()
        earliest_user = db.session.query(func.min(User.created_at)).scalar()
        
        earliest_dates = [d for d in [earliest_event, earliest_partner, earliest_user] if d is not None]
        if earliest_dates:
            start_date_for_fill = min(earliest_dates)
            # Round down to first of month
            start_date_for_fill = datetime(start_date_for_fill.year, start_date_for_fill.month, 1)
        else:
            # Default to 1 year ago if no data
            start_date_for_fill = datetime(now.year - 1, now.month, 1)
        
        # For all_time with month grouping, end_date should be current month
        end_date_for_fill = datetime(now.year, now.month, 1)
    
    return jsonify({
        'period': period,
        'events': create_chart_data(events_data, group_by, start_date_for_fill, end_date_for_fill),
        'partners': create_chart_data(partners_data, group_by, start_date_for_fill, end_date_for_fill),
        'users': create_chart_data(users_data, group_by, start_date_for_fill, end_date_for_fill),
        'revenue': create_chart_data(revenue_data, group_by, start_date_for_fill, end_date_for_fill)
    }), 200


# ============ PAYOUT MANAGEMENT ============

@bp.route('/payouts', methods=['GET'])
@admin_required
def get_payouts(current_admin):
    """Get all payout requests"""
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = PartnerPayout.query
    
    if status:
        query = query.filter_by(status=status)
    
    payouts = query.order_by(PartnerPayout.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'payouts': [payout.to_dict() for payout in payouts.items],
        'total': payouts.total,
        'page': payouts.page,
        'pages': payouts.pages
    }), 200


@bp.route('/payouts/<int:payout_id>/approve', methods=['POST'])
@admin_required
def approve_payout(current_admin, payout_id):
    """Approve payout request"""
    payout = PartnerPayout.query.get(payout_id)
    
    if not payout:
        return jsonify({'error': 'Payout not found'}), 404
    
    if payout.status != 'pending':
        return jsonify({'error': 'Payout is not pending'}), 400
    
    payout.status = 'processing'
    payout.processed_by = current_admin.id
    payout.processed_at = datetime.utcnow()
    
    # Log action
    log_admin_action(
        current_admin,
        'approve_payout',
        'payout',
        payout_id,
        f"Approved payout: {payout.reference_number} for KES {payout.amount}"
    )
    
    db.session.commit()
    
    # Send payout approval SMS and email to partner
    partner = payout.partner
    if partner:
        try:
            send_payout_approval_sms(partner, payout)
        except Exception as sms_error:
            current_app.logger.warning(f'Failed to send payout approval SMS: {str(sms_error)}')
        
        try:
            send_payout_approval_email(partner, payout)
        except Exception as email_error:
            current_app.logger.warning(f'Failed to send payout approval email: {str(email_error)}')
    
    # TODO: Initiate actual payout via MPesa B2C
    
    return jsonify({
        'message': 'Payout approved and processing'
    }), 200


@bp.route('/logs', methods=['GET'])
@admin_required
def get_admin_logs(current_admin):
    """Get admin activity logs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    logs = AdminLog.query.order_by(AdminLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'page': logs.page,
        'pages': logs.pages
    }), 200


@bp.route('/support', methods=['GET'])
@admin_required
def get_support_requests(current_admin):
    """Get all partner support requests"""
    status = request.args.get('status')  # open, in_progress, resolved, all
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = PartnerSupportRequest.query
    
    if status and status != 'all':
        query = query.filter_by(status=status)
    
    support_requests = query.order_by(PartnerSupportRequest.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Include partner information for each request
    requests_data = []
    for req in support_requests.items:
        partner = Partner.query.get(req.partner_id)
        req_dict = req.to_dict()
        req_dict['partner'] = partner.to_dict() if partner else None
        requests_data.append(req_dict)
    
    return jsonify({
        'support_requests': requests_data,
        'total': support_requests.total,
        'page': support_requests.page,
        'pages': support_requests.pages
    }), 200


@bp.route('/support/<int:request_id>/status', methods=['PUT'])
@admin_required
def update_support_status(current_admin, request_id):
    """Update support request status"""
    data = request.get_json() or {}
    new_status = data.get('status')
    
    if not new_status or new_status not in ['open', 'in_progress', 'resolved']:
        return jsonify({'error': 'Invalid status. Must be: open, in_progress, or resolved'}), 400
    
    support_request = PartnerSupportRequest.query.get(request_id)
    if not support_request:
        return jsonify({'error': 'Support request not found'}), 404
    
    support_request.status = new_status
    support_request.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_admin_action(
        current_admin,
        'update_support_status',
        'support_request',
        request_id,
        f'Updated support request status to {new_status}'
    )
    
    return jsonify({
        'message': 'Support request status updated',
        'support_request': support_request.to_dict()
    }), 200


@bp.route('/test-email', methods=['POST'])
@admin_required
def test_email_endpoint(current_admin):
    """Test email sending"""
    recipient = request.json.get('email', current_admin.email)
    
    try:
        send_email(
            subject="Email Test from Niko Free",
            recipient=recipient,
            html_body="<h1>Test Email</h1><p>If you see this, email is working!</p>"
        )
        return jsonify({
            'message': 'Test email sent',
            'recipient': recipient,
            'note': 'Check your inbox and spam folder'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

