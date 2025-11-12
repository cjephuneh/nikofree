from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from sqlalchemy import func
from app import db
from app.models.partner import Partner
from app.models.event import Event, EventHost, EventInterest, EventPromotion
from app.models.ticket import TicketType, PromoCode, Booking
from app.models.payment import PartnerPayout
from app.models.user import User
from app.utils.decorators import partner_required
from app.utils.file_upload import upload_file

bp = Blueprint('partners', __name__)


@bp.route('/dashboard', methods=['GET'])
@partner_required
def get_dashboard(current_partner):
    """Get partner dashboard overview"""
    # Count events
    total_events = Event.query.filter_by(partner_id=current_partner.id).count()
    upcoming_events = Event.query.filter(
        Event.partner_id == current_partner.id,
        Event.start_date > datetime.utcnow(),
        Event.status == 'approved'
    ).count()
    
    # Count attendees
    total_attendees = db.session.query(func.sum(Event.attendee_count)).filter(
        Event.partner_id == current_partner.id
    ).scalar() or 0
    
    # Get recent bookings
    recent_bookings = Booking.query.join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed'
    ).order_by(Booking.created_at.desc()).limit(10).all()
    
    return jsonify({
        'partner': current_partner.to_dict(include_sensitive=True),
        'stats': {
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'total_attendees': int(total_attendees),
            'total_earnings': float(current_partner.total_earnings),
            'pending_earnings': float(current_partner.pending_earnings),
            'withdrawn_earnings': float(current_partner.withdrawn_earnings)
        },
        'recent_bookings': [booking.to_dict() for booking in recent_bookings]
    }), 200


@bp.route('/profile', methods=['GET'])
@partner_required
def get_profile(current_partner):
    """Get partner profile"""
    return jsonify(current_partner.to_dict(include_sensitive=True)), 200


@bp.route('/profile', methods=['PUT'])
@partner_required
def update_profile(current_partner):
    """Update partner profile"""
    data = request.get_json()
    
    # Update allowed fields
    if data.get('business_name'):
        current_partner.business_name = data['business_name'].strip()
    
    if data.get('contact_person'):
        current_partner.contact_person = data['contact_person'].strip()
    
    if data.get('phone_number'):
        current_partner.phone_number = data['phone_number']
    
    if data.get('address'):
        current_partner.address = data['address']
    
    if data.get('website'):
        current_partner.website = data['website']
    
    if data.get('category_id'):
        current_partner.category_id = data['category_id']
    
    # Bank information
    if data.get('bank_name'):
        current_partner.bank_name = data['bank_name']
    
    if data.get('bank_account_number'):
        current_partner.bank_account_number = data['bank_account_number']
    
    if data.get('bank_account_name'):
        current_partner.bank_account_name = data['bank_account_name']
    
    if data.get('mpesa_number'):
        current_partner.mpesa_number = data['mpesa_number']
    
    current_partner.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'partner': current_partner.to_dict(include_sensitive=True)
    }), 200


@bp.route('/logo', methods=['POST'])
@partner_required
def upload_logo(current_partner):
    """Upload partner logo"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    try:
        file_path = upload_file(file, folder='logos')
        
        if not file_path:
            return jsonify({'error': 'Failed to upload file'}), 500
        
        current_partner.logo = file_path
        db.session.commit()
        
        return jsonify({
            'message': 'Logo uploaded successfully',
            'logo': file_path
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ============ EVENT MANAGEMENT ============

@bp.route('/events', methods=['GET'])
@partner_required
def get_partner_events(current_partner):
    """Get all events for this partner"""
    status = request.args.get('status')  # pending, approved, rejected, all
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Event.query.filter_by(partner_id=current_partner.id)
    
    if status and status != 'all':
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


@bp.route('/events', methods=['POST'])
@partner_required
def create_event(current_partner):
    """Create new event"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'description', 'category_id', 'start_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Parse dates
    try:
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
    except:
        return jsonify({'error': 'Invalid start_date format'}), 400
    
    end_date = None
    if data.get('end_date'):
        try:
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Create event
    event = Event(
        title=data['title'].strip(),
        description=data['description'].strip(),
        partner_id=current_partner.id,
        category_id=data['category_id'],
        start_date=start_date,
        end_date=end_date,
        is_online=data.get('is_online', False),
        venue_name=data.get('venue_name'),
        venue_address=data.get('venue_address'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        online_link=data.get('online_link'),
        location_id=data.get('location_id'),
        is_free=data.get('is_free', True),
        status='pending'
    )
    
    db.session.add(event)
    db.session.flush()  # Get event ID
    
    # Add interests (max 5)
    if data.get('interests'):
        interests = data['interests'][:current_app.config.get('MAX_INTERESTS_PER_EVENT', 5)]
        for interest_name in interests:
            interest = EventInterest(event_id=event.id, name=interest_name.strip())
            db.session.add(interest)
    
    # Add hosts (max 2)
    if data.get('host_ids'):
        host_ids = data['host_ids'][:current_app.config.get('MAX_HOSTS_PER_EVENT', 2)]
        for host_id in host_ids:
            user = User.query.get(host_id)
            if user:
                host = EventHost(event_id=event.id, user_id=host_id)
                db.session.add(host)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Event created successfully. Awaiting admin approval.',
        'event': event.to_dict()
    }), 201


@bp.route('/events/<int:event_id>', methods=['GET'])
@partner_required
def get_event(current_partner, event_id):
    """Get single event"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    return jsonify(event.to_dict(include_stats=True)), 200


@bp.route('/events/<int:event_id>', methods=['PUT'])
@partner_required
def update_event(current_partner, event_id):
    """Update event"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Can only edit pending or rejected events
    if event.status not in ['pending', 'rejected']:
        return jsonify({'error': 'Cannot edit approved events'}), 403
    
    data = request.get_json()
    
    # Update fields
    if data.get('title'):
        event.title = data['title'].strip()
    
    if data.get('description'):
        event.description = data['description'].strip()
    
    if data.get('category_id'):
        event.category_id = data['category_id']
    
    if data.get('start_date'):
        try:
            event.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if data.get('end_date'):
        try:
            event.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except:
            pass
    
    if 'is_online' in data:
        event.is_online = data['is_online']
    
    if 'venue_name' in data:
        event.venue_name = data['venue_name']
    
    if 'venue_address' in data:
        event.venue_address = data['venue_address']
    
    if 'latitude' in data:
        event.latitude = data['latitude']
    
    if 'longitude' in data:
        event.longitude = data['longitude']
    
    if 'online_link' in data:
        event.online_link = data['online_link']
    
    if 'location_id' in data:
        event.location_id = data['location_id']
    
    if 'is_free' in data:
        event.is_free = data['is_free']
    
    # Reset status to pending if it was rejected
    if event.status == 'rejected':
        event.status = 'pending'
        event.rejection_reason = None
    
    event.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Event updated successfully',
        'event': event.to_dict()
    }), 200


@bp.route('/events/<int:event_id>', methods=['DELETE'])
@partner_required
def delete_event(current_partner, event_id):
    """Delete event"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if event has bookings
    if event.bookings.count() > 0:
        return jsonify({'error': 'Cannot delete event with existing bookings'}), 403
    
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'message': 'Event deleted successfully'}), 200


@bp.route('/events/<int:event_id>/poster', methods=['POST'])
@partner_required
def upload_event_poster(current_partner, event_id):
    """Upload event poster"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    try:
        file_path = upload_file(file, folder='events')
        
        if not file_path:
            return jsonify({'error': 'Failed to upload file'}), 500
        
        event.poster_image = file_path
        db.session.commit()
        
        return jsonify({
            'message': 'Poster uploaded successfully',
            'poster_image': file_path
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ============ TICKET MANAGEMENT ============

@bp.route('/events/<int:event_id>/tickets', methods=['POST'])
@partner_required
def create_ticket_type(current_partner, event_id):
    """Create ticket type for event"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or data.get('price') is None:
        return jsonify({'error': 'name and price are required'}), 400
    
    ticket_type = TicketType(
        event_id=event_id,
        name=data['name'].strip(),
        description=data.get('description'),
        price=data['price'],
        quantity_total=data.get('quantity_total'),
        quantity_available=data.get('quantity_total'),
        min_per_order=data.get('min_per_order', 1),
        max_per_order=data.get('max_per_order', 10)
    )
    
    if data.get('sales_start'):
        try:
            ticket_type.sales_start = datetime.fromisoformat(data['sales_start'].replace('Z', '+00:00'))
        except:
            pass
    
    if data.get('sales_end'):
        try:
            ticket_type.sales_end = datetime.fromisoformat(data['sales_end'].replace('Z', '+00:00'))
        except:
            pass
    
    db.session.add(ticket_type)
    db.session.commit()
    
    return jsonify({
        'message': 'Ticket type created successfully',
        'ticket_type': ticket_type.to_dict()
    }), 201


@bp.route('/events/<int:event_id>/promo-codes', methods=['POST'])
@partner_required
def create_promo_code(current_partner, event_id):
    """Create promo code for event"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required = ['code', 'discount_type', 'discount_value']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if code already exists
    existing = PromoCode.query.filter_by(code=data['code'].upper()).first()
    if existing:
        return jsonify({'error': 'Promo code already exists'}), 409
    
    promo_code = PromoCode(
        code=data['code'].upper().strip(),
        event_id=event_id,
        discount_type=data['discount_type'],
        discount_value=data['discount_value'],
        max_uses=data.get('max_uses'),
        max_uses_per_user=data.get('max_uses_per_user', 1),
        created_by=current_partner.id
    )
    
    if data.get('valid_from'):
        try:
            promo_code.valid_from = datetime.fromisoformat(data['valid_from'].replace('Z', '+00:00'))
        except:
            pass
    
    if data.get('valid_until'):
        try:
            promo_code.valid_until = datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00'))
        except:
            pass
    
    db.session.add(promo_code)
    db.session.commit()
    
    return jsonify({
        'message': 'Promo code created successfully',
        'promo_code': promo_code.to_dict()
    }), 201


# ============ ATTENDEE MANAGEMENT ============

@bp.route('/events/<int:event_id>/attendees', methods=['GET'])
@partner_required
def get_event_attendees(current_partner, event_id):
    """Get list of attendees for event"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    bookings = Booking.query.filter_by(
        event_id=event_id,
        status='confirmed'
    ).order_by(Booking.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'attendees': [booking.to_dict() for booking in bookings.items],
        'total': bookings.total,
        'page': bookings.page,
        'pages': bookings.pages
    }), 200


@bp.route('/events/<int:event_id>/attendees/export', methods=['GET'])
@partner_required
def export_attendees(current_partner, event_id):
    """Export attendee list as CSV"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    import csv
    from io import StringIO
    
    # Get all bookings
    bookings = Booking.query.filter_by(
        event_id=event_id,
        status='confirmed'
    ).all()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Header
    writer.writerow(['Booking Number', 'Name', 'Email', 'Phone', 'Quantity', 'Total Amount', 'Checked In', 'Booking Date'])
    
    # Data
    for booking in bookings:
        user = booking.user
        writer.writerow([
            booking.booking_number,
            f"{user.first_name} {user.last_name}",
            user.email,
            user.phone_number or '',
            booking.quantity,
            f"KES {booking.total_amount}",
            'Yes' if booking.is_checked_in else 'No',
            booking.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    output = si.getvalue()
    
    from flask import make_response
    response = make_response(output)
    response.headers["Content-Disposition"] = f"attachment; filename=attendees_{event_id}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response


# ============ FINANCIALS ============

@bp.route('/earnings', methods=['GET'])
@partner_required
def get_earnings(current_partner):
    """Get earnings breakdown"""
    # Get all completed bookings
    bookings = db.session.query(
        func.sum(Booking.partner_amount).label('total'),
        func.count(Booking.id).label('count')
    ).join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed',
        Booking.payment_status == 'paid'
    ).first()
    
    return jsonify({
        'total_earnings': float(current_partner.total_earnings),
        'pending_earnings': float(current_partner.pending_earnings),
        'withdrawn_earnings': float(current_partner.withdrawn_earnings),
        'available_for_withdrawal': float(current_partner.pending_earnings),
        'total_bookings': bookings.count if bookings else 0
    }), 200


@bp.route('/payouts', methods=['GET'])
@partner_required
def get_payouts(current_partner):
    """Get payout history"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    payouts = PartnerPayout.query.filter_by(
        partner_id=current_partner.id
    ).order_by(PartnerPayout.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'payouts': [payout.to_dict() for payout in payouts.items],
        'total': payouts.total,
        'page': payouts.page,
        'pages': payouts.pages
    }), 200


@bp.route('/payouts', methods=['POST'])
@partner_required
def request_payout(current_partner):
    """Request payout/withdrawal"""
    data = request.get_json()
    
    # Validate amount
    if not data.get('amount'):
        return jsonify({'error': 'amount is required'}), 400
    
    amount = float(data['amount'])
    
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    if amount > float(current_partner.pending_earnings):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Validate payout method
    payout_method = data.get('payout_method', 'mpesa')
    
    if payout_method == 'mpesa':
        if not current_partner.mpesa_number:
            return jsonify({'error': 'Please add MPesa number in your profile'}), 400
        account_number = current_partner.mpesa_number
    elif payout_method == 'bank_transfer':
        if not current_partner.bank_account_number:
            return jsonify({'error': 'Please add bank details in your profile'}), 400
        account_number = current_partner.bank_account_number
    else:
        return jsonify({'error': 'Invalid payout method'}), 400
    
    # Create payout request
    import uuid
    payout = PartnerPayout(
        reference_number=f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
        partner_id=current_partner.id,
        amount=amount,
        payout_method=payout_method,
        account_number=account_number,
        account_name=current_partner.bank_account_name or current_partner.business_name,
        status='pending'
    )
    
    db.session.add(payout)
    
    # Update partner balance
    current_partner.pending_earnings -= amount
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payout request submitted successfully',
        'payout': payout.to_dict()
    }), 201

