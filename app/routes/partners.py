from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from sqlalchemy import func
import json
from app import db, limiter
from app.models.partner import Partner, PartnerSupportRequest, PartnerTeamMember
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


@bp.route('/analytics', methods=['GET'])
@partner_required
def get_partner_analytics(current_partner):
    """More detailed analytics for partner (used by Analytics page)"""
    from datetime import timedelta
    days = request.args.get('days', 30, type=int)
    now = datetime.utcnow()
    start_period = now - timedelta(days=days)
    start_7d = now - timedelta(days=7)
    start_1d = now - timedelta(days=1)
    
    # Base confirmed bookings query for this partner
    base_bookings = Booking.query.join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed'
    )
    
    # All-time stats
    total_bookings = base_bookings.count()
    total_revenue = db.session.query(func.sum(Booking.partner_amount)).join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed'
    ).scalar() or 0
    
    # Period stats (last N days)
    period_bookings = base_bookings.filter(Booking.created_at >= start_period).count()
    period_revenue = db.session.query(func.sum(Booking.partner_amount)).join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed',
        Booking.created_at >= start_period
    ).scalar() or 0
    
    # Last 7 days
    last_7d_bookings = base_bookings.filter(Booking.created_at >= start_7d).count()
    last_7d_revenue = db.session.query(func.sum(Booking.partner_amount)).join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed',
        Booking.created_at >= start_7d
    ).scalar() or 0
    
    # Last 24 hours
    last_1d_bookings = base_bookings.filter(Booking.created_at >= start_1d).count()
    last_1d_revenue = db.session.query(func.sum(Booking.partner_amount)).join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed',
        Booking.created_at >= start_1d
    ).scalar() or 0
    
    # Event stats
    total_events = Event.query.filter_by(partner_id=current_partner.id).count()
    active_events = Event.query.filter(
        Event.partner_id == current_partner.id,
        Event.start_date > now,
        Event.status == 'approved'
    ).count()
    
    return jsonify({
        'summary': {
            'total_bookings': total_bookings,
            'total_events': total_events,
            'active_events': active_events,
            'total_revenue': float(total_revenue),
        },
        'period': {
            'days': days,
            'bookings': period_bookings,
            'revenue': float(period_revenue),
        },
        'last_7_days': {
            'bookings': last_7d_bookings,
            'revenue': float(last_7d_revenue),
        },
        'last_24_hours': {
            'bookings': last_1d_bookings,
            'revenue': float(last_1d_revenue),
        },
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
    
    if data.get('description'):
        current_partner.description = data['description'].strip()
    
    if data.get('location'):
        current_partner.location = data['location'].strip()
    
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


@bp.route('/change-password', methods=['POST'])
@partner_required
def change_password(current_partner):
    """Change partner password"""
    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    # Verify current password
    if not current_partner.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password
    from app.utils.validators import validate_password
    is_valid, error_msg = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Check if new password is same as current
    if current_partner.check_password(data['new_password']):
        return jsonify({'error': 'New password must be different from current password'}), 400
    
    # Update password
    current_partner.set_password(data['new_password'])
    current_partner.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Password changed successfully'
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
            'partner': current_partner.to_dict(include_sensitive=True),
            'logo': file_path
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ============ EVENT MANAGEMENT ============

@bp.route('/events', methods=['GET'])
@limiter.exempt
@partner_required
def get_partner_events(current_partner):
    """Get all events for this partner"""
    status = request.args.get('status')  # pending, approved, rejected, upcoming, ongoing, past, all
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    now = datetime.utcnow()
    query = Event.query.filter_by(partner_id=current_partner.id)
    
    if status and status != 'all':
        if status == 'upcoming':
            # Future events that are approved
            query = query.filter(
                Event.start_date > now,
                Event.status == 'approved'
            )
        elif status == 'ongoing':
            # Events happening now (started but not ended)
            from sqlalchemy import or_
            query = query.filter(
                Event.start_date <= now,
                or_(Event.end_date.is_(None), Event.end_date >= now),
                Event.status == 'approved'
            )
        elif status == 'past':
            # Events that have ended
            query = query.filter(
                Event.end_date.isnot(None),
                Event.end_date < now,
                Event.status == 'approved'
            )
        else:
            # pending, approved, rejected
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
    """Create new event with poster, ticket types, and promo codes"""
    from app.models.ticket import TicketType, PromoCode
    from app.models.event import EventInterest
    
    # Handle both JSON and form-data
    if request.is_json:
        data = request.get_json()
        poster_file = None
    else:
        # Form data
        data = {}
        for key in request.form:
            try:
                # Try to parse JSON fields
                if key in ['ticket_types', 'promo_codes', 'interests', 'coordinates']:
                    data[key] = json.loads(request.form[key])
                else:
                    data[key] = request.form[key]
            except:
                data[key] = request.form[key]
        
        poster_file = request.files.get('poster_image')
    
    # Validate required fields
    required_fields = ['title', 'description', 'category_id', 'start_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Parse dates
    try:
        start_date_str = data['start_date']
        if 'T' in start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        else:
            # Handle date + time separately
            start_time = data.get('start_time', '00:00')
            start_date = datetime.strptime(f"{start_date_str} {start_time}", "%Y-%m-%d %H:%M")
    except Exception as e:
        return jsonify({'error': f'Invalid start_date format: {str(e)}'}), 400
    
    end_date = None
    if data.get('end_date'):
        try:
            end_date_str = data['end_date']
            if 'T' in end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            else:
                end_time = data.get('end_time', '23:59')
                end_date = datetime.strptime(f"{end_date_str} {end_time}", "%Y-%m-%d %H:%M")
        except Exception as e:
            return jsonify({'error': f'Invalid end_date format: {str(e)}'}), 400
    
    # Determine if online/hybrid
    location_type = data.get('location_type', 'physical')
    is_online = location_type == 'online'
    is_hybrid = location_type == 'hybrid'
    
    # Upload poster if provided
    poster_path = None
    if poster_file:
        try:
            poster_path = upload_file(poster_file, folder='events')
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    # Create event
    event = Event(
        title=data['title'].strip(),
        description=data['description'].strip(),
        partner_id=current_partner.id,
        category_id=int(data['category_id']),
        start_date=start_date,
        end_date=end_date,
        is_online=is_online or is_hybrid,
        venue_name=data.get('venue_name') or data.get('location_name'),
        venue_address=data.get('venue_address'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        online_link=data.get('online_link'),
        location_id=data.get('location_id'),
        is_free=data.get('is_free', 'true').lower() == 'true' if isinstance(data.get('is_free'), str) else data.get('is_free', True),
        status='pending',
        poster_image=poster_path
    )
    
    db.session.add(event)
    db.session.flush()  # Get event ID
    
    # Add interests (max 5)
    if data.get('interests'):
        interests = data['interests']
        if isinstance(interests, str):
            interests = json.loads(interests) if interests.startswith('[') else [interests]
        interests = interests[:current_app.config.get('MAX_INTERESTS_PER_EVENT', 5)]
        for interest_name in interests:
            if interest_name.strip():
                interest = EventInterest(event_id=event.id, name=interest_name.strip())
                db.session.add(interest)
    
    # Add ticket types if paid event
    if not event.is_free and data.get('ticket_types'):
        ticket_types_data = data['ticket_types']
        if isinstance(ticket_types_data, str):
            ticket_types_data = json.loads(ticket_types_data)
        
        for tt_data in ticket_types_data:
            ticket_type = TicketType(
                event_id=event.id,
                name=tt_data.get('name', '').strip(),
                description=tt_data.get('description', ''),
                price=float(tt_data.get('price', 0)),
                quantity_total=int(tt_data.get('quantity', 0)) if tt_data.get('quantity') else None,
                quantity_available=int(tt_data.get('quantity', 0)) if tt_data.get('quantity') else None,
                is_active=True
            )
            db.session.add(ticket_type)
    
    # Add promo codes
    if data.get('promo_codes'):
        promo_codes_data = data['promo_codes']
        if isinstance(promo_codes_data, str):
            promo_codes_data = json.loads(promo_codes_data)
        
        for promo_data in promo_codes_data:
            if promo_data.get('code'):
                promo_code = PromoCode(
                    code=promo_data['code'].upper().strip(),
                    event_id=event.id,
                    discount_type=promo_data.get('discount_type', 'percentage'),
                    discount_value=float(promo_data.get('discount', 0)),
                    max_uses=int(promo_data.get('max_uses', 0)) if promo_data.get('max_uses') else None,
                    created_by=current_partner.id
                )
                
                if promo_data.get('expiry_date'):
                    try:
                        promo_code.valid_until = datetime.strptime(promo_data['expiry_date'], "%Y-%m-%d")
                    except:
                        pass
                
                db.session.add(promo_code)
    
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
    """Update event with all fields including ticket types, promo codes, interests, and poster"""
    from app.models.ticket import TicketType, PromoCode
    from app.models.event import EventInterest
    
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Allow editing any event (can restrict later if needed)
    # if event.status not in ['pending', 'rejected']:
    #     return jsonify({'error': 'Cannot edit approved events'}), 403
    
    # Handle both JSON and form-data
    if request.is_json:
        data = request.get_json()
        poster_file = None
    else:
        # Form data
        data = {}
        for key in request.form:
            try:
                # Try to parse JSON fields
                if key in ['ticket_types', 'promo_codes', 'interests', 'coordinates', 'existing_ticket_ids', 'existing_promo_ids']:
                    data[key] = json.loads(request.form[key])
                else:
                    data[key] = request.form[key]
            except:
                data[key] = request.form[key]
        
        poster_file = request.files.get('poster_image')
    
    # Update basic fields
    if data.get('title'):
        event.title = data['title'].strip()
    
    if data.get('description'):
        event.description = data['description'].strip()
    
    if data.get('category_id'):
        event.category_id = int(data['category_id'])
    
    # Parse dates
    if data.get('start_date'):
        try:
            start_date_str = data['start_date']
            if 'T' in start_date_str:
                event.start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                start_time = data.get('start_time', '00:00')
                event.start_date = datetime.strptime(f"{start_date_str} {start_time}", "%Y-%m-%d %H:%M")
        except Exception as e:
            return jsonify({'error': f'Invalid start_date format: {str(e)}'}), 400
    
    if data.get('end_date'):
        try:
            end_date_str = data['end_date']
            if 'T' in end_date_str:
                event.end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            else:
                end_time = data.get('end_time', '23:59')
                event.end_date = datetime.strptime(f"{end_date_str} {end_time}", "%Y-%m-%d %H:%M")
        except Exception as e:
            pass
    
    # Location
    location_type = data.get('location_type')
    if location_type:
        if location_type == 'online':
            event.is_online = True
        elif location_type == 'hybrid':
            event.is_online = True
        elif location_type == 'physical':
            event.is_online = False
    
    if 'venue_name' in data or 'location_name' in data:
        event.venue_name = data.get('venue_name') or data.get('location_name')
    
    if 'venue_address' in data:
        event.venue_address = data.get('venue_address')
    
    if 'latitude' in data and data['latitude']:
        event.latitude = float(data['latitude'])
    
    if 'longitude' in data and data['longitude']:
        event.longitude = float(data['longitude'])
    
    if 'online_link' in data:
        event.online_link = data.get('online_link')
    
    if 'location_id' in data:
        event.location_id = data.get('location_id')
    
    if 'is_free' in data:
        event.is_free = data.get('is_free', 'true').lower() == 'true' if isinstance(data.get('is_free'), str) else data.get('is_free', True)
    
    # Upload new poster if provided
    if poster_file:
        try:
            # Delete old poster if exists
            if event.poster_image:
                import os
                old_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), event.poster_image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            event.poster_image = upload_file(poster_file, folder='events')
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    # Update interests - remove old ones and add new
    if 'interests' in data:
        # Delete existing interests
        EventInterest.query.filter_by(event_id=event.id).delete()
        
        interests = data['interests']
        if isinstance(interests, str):
            interests = json.loads(interests) if interests.startswith('[') else [interests]
        interests = interests[:current_app.config.get('MAX_INTERESTS_PER_EVENT', 5)]
        for interest_name in interests:
            if interest_name.strip():
                interest = EventInterest(event_id=event.id, name=interest_name.strip())
                db.session.add(interest)
    
    # Update ticket types
    if 'ticket_types' in data:
        existing_ticket_ids = data.get('existing_ticket_ids', [])
        if isinstance(existing_ticket_ids, str):
            existing_ticket_ids = json.loads(existing_ticket_ids) if existing_ticket_ids else []
        
        ticket_types_data = data['ticket_types']
        if isinstance(ticket_types_data, str):
            ticket_types_data = json.loads(ticket_types_data)
        
        # Delete ticket types not in the update list
        if existing_ticket_ids:
            TicketType.query.filter(
                TicketType.event_id == event.id,
                ~TicketType.id.in_(existing_ticket_ids)
            ).delete(synchronize_session=False)
        
        # Update or create ticket types
        for tt_data in ticket_types_data:
            if tt_data.get('id') and tt_data['id'] in existing_ticket_ids:
                # Update existing
                ticket_type = TicketType.query.get(tt_data['id'])
                if ticket_type and ticket_type.event_id == event.id:
                    ticket_type.name = tt_data.get('name', '').strip()
                    ticket_type.price = float(tt_data.get('price', 0))
                    if tt_data.get('quantity') is not None:
                        new_quantity_total = int(tt_data['quantity'])
                        current_sold = ticket_type.quantity_sold or 0
                        ticket_type.quantity_total = new_quantity_total
                        ticket_type.quantity_available = max(0, new_quantity_total - current_sold)
            else:
                # Create new
                ticket_type = TicketType(
                    event_id=event.id,
                    name=tt_data.get('name', '').strip(),
                    description=tt_data.get('description', ''),
                    price=float(tt_data.get('price', 0)),
                    quantity_total=int(tt_data.get('quantity', 0)) if tt_data.get('quantity') else None,
                    quantity_available=int(tt_data.get('quantity', 0)) if tt_data.get('quantity') else None,
                    is_active=True
                )
                db.session.add(ticket_type)
    
    # Update promo codes
    if 'promo_codes' in data:
        existing_promo_ids = data.get('existing_promo_ids', [])
        if isinstance(existing_promo_ids, str):
            existing_promo_ids = json.loads(existing_promo_ids) if existing_promo_ids else []
        
        promo_codes_data = data['promo_codes']
        if isinstance(promo_codes_data, str):
            promo_codes_data = json.loads(promo_codes_data)
        
        # Delete promo codes not in the update list
        if existing_promo_ids:
            PromoCode.query.filter(
                PromoCode.event_id == event.id,
                ~PromoCode.id.in_(existing_promo_ids)
            ).delete(synchronize_session=False)
        
        # Update or create promo codes
        for promo_data in promo_codes_data:
            if promo_data.get('code'):
                if promo_data.get('id') and promo_data['id'] in existing_promo_ids:
                    # Update existing
                    promo_code = PromoCode.query.get(promo_data['id'])
                    if promo_code and promo_code.event_id == event.id:
                        promo_code.code = promo_data['code'].upper().strip()
                        promo_code.discount_type = promo_data.get('discount_type', 'percentage')
                        promo_code.discount_value = float(promo_data.get('discount', 0))
                        promo_code.max_uses = int(promo_data.get('max_uses', 0)) if promo_data.get('max_uses') else None
                        if promo_data.get('expiry_date'):
                            try:
                                promo_code.valid_until = datetime.strptime(promo_data['expiry_date'], "%Y-%m-%d")
                            except:
                                pass
                else:
                    # Create new
                    promo_code = PromoCode(
                        code=promo_data['code'].upper().strip(),
                        event_id=event.id,
                        discount_type=promo_data.get('discount_type', 'percentage'),
                        discount_value=float(promo_data.get('discount', 0)),
                        max_uses=int(promo_data.get('max_uses', 0)) if promo_data.get('max_uses') else None,
                        created_by=current_partner.id
                    )
                    
                    if promo_data.get('expiry_date'):
                        try:
                            promo_code.valid_until = datetime.strptime(promo_data['expiry_date'], "%Y-%m-%d")
                        except:
                            pass
                    
                    db.session.add(promo_code)
    
    # Reset status to pending if it was rejected
    if event.status == 'rejected':
        event.status = 'pending'
        event.rejection_reason = None
    
    event.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Event updated successfully',
        'event': event.to_dict(include_stats=True)
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


# ============ SUPPORT & TEAM MANAGEMENT ============


@bp.route('/support', methods=['POST'])
@partner_required
def create_support_request(current_partner):
    """Create a support request from partner"""
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    subject = (data.get('subject') or '').strip()
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    support_request = PartnerSupportRequest(
        partner_id=current_partner.id,
        subject=subject or None,
        message=message
    )
    
    db.session.add(support_request)
    db.session.commit()
    
    return jsonify({
        'message': 'Support request sent',
        'request': support_request.to_dict()
    }), 201


@bp.route('/team', methods=['GET'])
@partner_required
def get_team_members(current_partner):
    """Get active team members for this partner"""
    members = PartnerTeamMember.query.filter_by(
        partner_id=current_partner.id,
        is_active=True
    ).order_by(PartnerTeamMember.added_at.desc()).all()
    
    return jsonify({
        'members': [m.to_dict() for m in members]
    }), 200


@bp.route('/team', methods=['POST'])
@partner_required
def add_team_member(current_partner):
    """Add a team member / fellow manager"""
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    phone = (data.get('phone') or '').strip()
    role = (data.get('role') or 'Manager').strip()
    permissions = data.get('permissions') or []
    
    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400
    
    member = PartnerTeamMember(
        partner_id=current_partner.id,
        name=name,
        email=email,
        phone=phone or None,
        role=role,
        permissions=json.dumps(permissions) if permissions else None
    )
    
    db.session.add(member)
    db.session.commit()
    
    return jsonify({
        'message': 'Team member added',
        'member': member.to_dict()
    }), 201


@bp.route('/team/<int:member_id>', methods=['DELETE'])
@partner_required
def remove_team_member(current_partner, member_id):
    """Soft-delete a team member"""
    member = PartnerTeamMember.query.filter_by(
        id=member_id,
        partner_id=current_partner.id,
        is_active=True
    ).first()
    
    if not member:
        return jsonify({'error': 'Team member not found'}), 404
    
    member.is_active = False
    db.session.commit()
    
    return jsonify({
        'message': 'Team member removed'
    }), 200


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

@bp.route('/attendees', methods=['GET'])
@partner_required
def get_all_attendees(current_partner):
    """Get all attendees across all partner events"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    event_id = request.args.get('event_id', type=int)
    
    # Get all bookings for partner's events
    query = Booking.query.join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed'
    )
    
    if event_id:
        query = query.filter(Booking.event_id == event_id)
    
    bookings = query.order_by(Booking.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Format attendees data
    attendees = []
    for booking in bookings.items:
        user = booking.user
        event = booking.event
        
        # Calculate age from date_of_birth
        age = None
        if user.date_of_birth:
            today = datetime.utcnow().date()
            age = today.year - user.date_of_birth.year - ((today.month, today.day) < (user.date_of_birth.month, user.date_of_birth.day))
        
        # Determine gender (we don't have this field, so we'll use a placeholder or derive from name)
        gender = 'Other'  # Default since we don't have gender field
        
        # Get ticket type name
        ticket_type_name = 'Free'
        if booking.tickets.first():
            ticket = booking.tickets.first()
            if ticket.ticket_type:
                ticket_type_name = ticket.ticket_type.name
        
        # Determine if current event (upcoming or ongoing)
        now = datetime.utcnow()
        is_current = False
        if event.start_date > now:
            is_current = True  # Upcoming
        elif event.start_date <= now and (not event.end_date or event.end_date >= now):
            is_current = True  # Ongoing
        
        attendees.append({
            'id': booking.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'phone': user.phone_number or '',
            'age': age or 0,
            'gender': gender,
            'location': user.location or '',
            'ticketType': ticket_type_name,
            'event': event.title,
            'eventDate': event.start_date.isoformat(),
            'bookingDate': booking.created_at.isoformat(),
            'status': booking.status.capitalize(),
            'isCurrentEvent': is_current,
            'booking': booking.to_dict()
        })
    
    return jsonify({
        'attendees': attendees,
        'total': bookings.total,
        'page': bookings.page,
        'pages': bookings.pages
    }), 200


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


# ============ VERIFICATION ============

@bp.route('/verification', methods=['GET'])
@partner_required
def get_verification_status(current_partner):
    """Get partner verification status and progress"""
    now = datetime.utcnow()
    
    # Count completed events (past events that were approved)
    completed_events = Event.query.filter(
        Event.partner_id == current_partner.id,
        Event.status == 'approved',
        Event.end_date.isnot(None),
        Event.end_date < now
    ).count()
    
    # Count total bookings across all events
    total_bookings = db.session.query(func.count(Booking.id)).join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed'
    ).scalar() or 0
    
    # Verification requirements
    events_required = 10
    bookings_required = 500
    
    # Check if eligible
    is_eligible = completed_events >= events_required or total_bookings >= bookings_required
    
    # Get all events for display
    all_events = Event.query.filter_by(
        partner_id=current_partner.id,
        status='approved'
    ).order_by(Event.start_date.desc()).all()
    
    # Get recent bookings
    recent_bookings = Booking.query.join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed'
    ).order_by(Booking.created_at.desc()).limit(10).all()
    
    return jsonify({
        'partner': {
            'id': current_partner.id,
            'business_name': current_partner.business_name,
            'is_verified': current_partner.is_verified,
            'status': current_partner.status
        },
        'verification': {
            'is_eligible': is_eligible,
            'is_verified': current_partner.is_verified,
            'events_hosted': completed_events,
            'events_required': events_required,
            'total_bookings': total_bookings,
            'bookings_required': bookings_required,
            'events_progress': min((completed_events / events_required) * 100, 100),
            'bookings_progress': min((total_bookings / bookings_required) * 100, 100)
        },
        'events': [event.to_dict(include_stats=True) for event in all_events],
        'recent_bookings': [booking.to_dict() for booking in recent_bookings]
    }), 200


@bp.route('/verification/claim', methods=['POST'])
@partner_required
def claim_verification_badge(current_partner):
    """Claim NIKO VERIFIED badge if eligible"""
    now = datetime.utcnow()
    
    # Count completed events
    completed_events = Event.query.filter(
        Event.partner_id == current_partner.id,
        Event.status == 'approved',
        Event.end_date.isnot(None),
        Event.end_date < now
    ).count()
    
    # Count total bookings
    total_bookings = db.session.query(func.count(Booking.id)).join(Event).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed'
    ).scalar() or 0
    
    # Check eligibility
    events_required = 10
    bookings_required = 500
    
    if completed_events < events_required and total_bookings < bookings_required:
        return jsonify({
            'error': 'You do not meet the requirements for NIKO VERIFIED status'
        }), 400
    
    # Mark as verified
    current_partner.is_verified = True
    db.session.commit()
    
    return jsonify({
        'message': 'NIKO VERIFIED badge claimed successfully!',
        'partner': current_partner.to_dict(include_sensitive=True)
    }), 200


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

