from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from app.models.user import User
from app.models.partner import Partner
from app.models.event import Event
from app.models.ticket import Booking
from app.models.payment import Payment, PartnerPayout
from app.models.category import Category, Location
from app.models.admin import AdminLog
from app.utils.decorators import admin_required
from app.utils.email import send_partner_approval_email, send_event_approval_email
from app.routes.notifications import notify_event_approved, notify_event_rejected

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
@admin_required
def get_dashboard(current_admin):
    """Get admin dashboard overview"""
    # Get stats
    total_users = User.query.count()
    total_partners = Partner.query.count()
    total_events = Event.query.count()
    total_bookings = Booking.query.count()
    
    # Pending approvals
    pending_partners = Partner.query.filter_by(status='pending').count()
    pending_events = Event.query.filter_by(status='pending').count()
    
    # Revenue
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed'
    ).scalar() or 0
    
    platform_fees = db.session.query(func.sum(Payment.platform_fee)).filter(
        Payment.status == 'completed'
    ).scalar() or 0
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_partners = Partner.query.order_by(Partner.created_at.desc()).limit(5).all()
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_partners': total_partners,
            'total_events': total_events,
            'total_bookings': total_bookings,
            'pending_partners': pending_partners,
            'pending_events': pending_events,
            'total_revenue': float(total_revenue),
            'platform_fees': float(platform_fees)
        },
        'recent_users': [user.to_dict() for user in recent_users],
        'recent_partners': [partner.to_dict() for partner in recent_partners],
        'recent_events': [event.to_dict() for event in recent_events]
    }), 200


# ============ PARTNER MANAGEMENT ============

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
    
    return jsonify({
        'partners': [partner.to_dict() for partner in partners.items],
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
    
    # Extract temporary password if stored
    temp_password = None
    if partner.rejection_reason and partner.rejection_reason.startswith('TEMP_PASS:'):
        temp_password = partner.rejection_reason.replace('TEMP_PASS:', '')
    
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
    
    return jsonify({
        'message': 'Partner activated successfully'
    }), 200


# ============ EVENT MANAGEMENT ============

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
    
    return jsonify({
        'events': [event.to_dict(include_stats=True) for event in events.items],
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
    
    # Create notification for partner
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
    
    # Top categories
    top_categories = db.session.query(
        Category.name,
        func.count(Event.id).label('event_count')
    ).join(Event).group_by(Category.id).order_by(desc('event_count')).limit(10).all()
    
    # Top partners
    top_partners = db.session.query(
        Partner.business_name,
        func.count(Booking.id).label('booking_count'),
        func.sum(Booking.partner_amount).label('earnings')
    ).join(Event).join(Booking).filter(
        Booking.status == 'confirmed'
    ).group_by(Partner.id).order_by(desc('booking_count')).limit(10).all()
    
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

