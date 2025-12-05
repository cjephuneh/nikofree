from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from sqlalchemy import func, or_
import json
from app import db, limiter
from app.models.partner import Partner, PartnerSupportRequest, PartnerTeamMember
from app.models.event import Event, EventHost, EventInterest, EventPromotion
from app.models.ticket import TicketType, PromoCode, Booking
from app.models.payment import PartnerPayout, Payment
from app.models.user import User
from app.utils.decorators import partner_required
from app.utils.file_upload import upload_file

bp = Blueprint('partners', __name__)


@bp.route('/dashboard', methods=['GET'])
@partner_required
def get_dashboard(current_partner):
    """Get partner dashboard overview"""
    # Count events
    now = datetime.utcnow()
    total_events = Event.query.filter_by(partner_id=current_partner.id).count()
    upcoming_events = Event.query.filter(
        Event.partner_id == current_partner.id,
        Event.start_date > now,
        Event.status == 'approved'
    ).count()
    
    # Count past events (using same logic as events endpoint)
    past_events = Event.query.filter(
        Event.partner_id == current_partner.id,
        or_(
            (Event.end_date.isnot(None)) & (Event.end_date < now),
            (Event.end_date.is_(None)) & (Event.start_date < now)
        ),
        Event.status == 'approved'
    ).count()
    
    # Count attendees
    total_attendees = db.session.query(func.sum(Event.attendee_count)).filter(
        Event.partner_id == current_partner.id
    ).scalar() or 0
    
    # Calculate actual earnings from database (only from completed payments)
    # Join with Payment to ensure we only count bookings with completed payments
    actual_total_earnings = db.session.query(func.sum(Booking.partner_amount)).join(Event).join(Payment).filter(
        Event.partner_id == current_partner.id,
        Booking.status == 'confirmed',
        Payment.status == 'completed',
        Booking.payment_id == Payment.id
    ).scalar() or 0
    
    # Get withdrawn earnings (from payouts)
    withdrawn_earnings = db.session.query(func.sum(PartnerPayout.amount)).filter(
        PartnerPayout.partner_id == current_partner.id,
        PartnerPayout.status == 'approved'
    ).scalar() or 0
    
    # Pending earnings = total - withdrawn
    pending_earnings = float(actual_total_earnings) - float(withdrawn_earnings)
    
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
            'past_events': past_events,
            'total_attendees': int(total_attendees),
            'total_earnings': float(actual_total_earnings),
            'pending_earnings': float(pending_earnings),
            'withdrawn_earnings': float(withdrawn_earnings)
        },
        'recent_bookings': [booking.to_dict() for booking in recent_bookings]
    }), 200


@bp.route('/analytics', methods=['GET'])
@partner_required
def get_partner_analytics(current_partner):
    """More detailed analytics for partner (used by Analytics page)"""
    try:
        from datetime import timedelta
        days = request.args.get('days', 30, type=int)
        now = datetime.utcnow()
        start_period = now - timedelta(days=days)
        start_7d = now - timedelta(days=7)
        start_1d = now - timedelta(days=1)
        
        # Base confirmed bookings query for this partner (only bookings with COMPLETED payments count for revenue)
        # Join with Payment to ensure we only count bookings with completed payments
        base_bookings = Booking.query.join(Event).join(Payment).filter(
            Event.partner_id == current_partner.id,
            Booking.status == 'confirmed',
            Payment.status == 'completed',
            Booking.payment_id == Payment.id
        )
        
        # All-time stats
        total_bookings = base_bookings.count()
        total_revenue = db.session.query(func.sum(Booking.partner_amount)).join(Event).join(Payment).filter(
            Event.partner_id == current_partner.id,
            Booking.status == 'confirmed',
            Payment.status == 'completed',
            Booking.payment_id == Payment.id
        ).scalar() or 0
        
        # Period stats (last N days)
        period_bookings = base_bookings.filter(Booking.created_at >= start_period).count()
        period_revenue = db.session.query(func.sum(Booking.partner_amount)).join(Event).join(Payment).filter(
            Event.partner_id == current_partner.id,
            Booking.status == 'confirmed',
            Payment.status == 'completed',
            Booking.payment_id == Payment.id,
            Booking.created_at >= start_period
        ).scalar() or 0
        
        # Last 7 days
        last_7d_bookings = base_bookings.filter(Booking.created_at >= start_7d).count()
        last_7d_revenue = db.session.query(func.sum(Booking.partner_amount)).join(Event).join(Payment).filter(
            Event.partner_id == current_partner.id,
            Booking.status == 'confirmed',
            Payment.status == 'completed',
            Booking.payment_id == Payment.id,
            Booking.created_at >= start_7d
        ).scalar() or 0
        
        # Last 24 hours
        last_1d_bookings = base_bookings.filter(Booking.created_at >= start_1d).count()
        last_1d_revenue = db.session.query(func.sum(Booking.partner_amount)).join(Event).join(Payment).filter(
            Event.partner_id == current_partner.id,
            Booking.status == 'confirmed',
            Payment.status == 'completed',
            Booking.payment_id == Payment.id,
            Booking.created_at >= start_1d
        ).scalar() or 0
        
        # Event stats
        total_events = Event.query.filter_by(partner_id=current_partner.id).count()
        active_events = Event.query.filter(
            Event.partner_id == current_partner.id,
            Event.start_date > now,
            Event.status == 'approved'
        ).count()
        
        # Generate daily time-series data for line chart
        # Pre-fetch all events and bookings to avoid N+1 queries
        all_events = Event.query.filter_by(partner_id=current_partner.id).all()
        all_bookings = base_bookings.all()
        
        chart_data = []
        cumulative_bookings_count = 0
        cumulative_revenue_total = 0.0
        
        for i in range(days):
            day_start = start_period + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            # Active events on this day (events that were active/upcoming on this date)
            active_on_day = sum(1 for event in all_events 
                               if event.start_date > day_start and event.status == 'approved')
            
            # Total events created up to this day
            total_events_by_day = sum(1 for event in all_events 
                                     if event.created_at <= day_end)
            
            # Bookings created on this day
            bookings_on_day = sum(1 for booking in all_bookings 
                                if day_start <= booking.created_at < day_end)
            
            # Revenue from bookings created on this day
            revenue_on_day = sum(float(booking.partner_amount) for booking in all_bookings 
                               if day_start <= booking.created_at < day_end)
            
            # Update cumulative values
            cumulative_bookings_count = sum(1 for booking in all_bookings 
                                           if booking.created_at <= day_end)
            cumulative_revenue_total = sum(float(booking.partner_amount) for booking in all_bookings 
                                          if booking.created_at <= day_end)
            
            chart_data.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'active_events': active_on_day,
                'total_events': total_events_by_day,
                'bookings': bookings_on_day,
                'cumulative_bookings': cumulative_bookings_count,
                'revenue': float(revenue_on_day),
                'cumulative_revenue': float(cumulative_revenue_total)
            })
        
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
            'chart_data': chart_data,
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching partner analytics: {str(e)}', exc_info=True)
        return jsonify({'error': f'Failed to fetch analytics: {str(e)}'}), 500


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
    
    # Validate logo if provided - prevent base64 data URIs
    if data.get('logo'):
        logo_value = data['logo']
        if isinstance(logo_value, str) and logo_value.startswith('data:image'):
            return jsonify({'error': 'Base64 data URIs are not allowed. Please use the /logo endpoint to upload an actual image file.'}), 400
        # Only update if it's a valid file path
        if logo_value and not logo_value.startswith('data:image'):
            current_partner.logo = logo_value
    
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
    
    # Check if file is actually a base64 data URI (shouldn't happen, but prevent it)
    if file.filename and file.filename.startswith('data:image'):
        return jsonify({'error': 'Base64 data URIs are not allowed. Please upload an actual image file.'}), 400
    
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
            query = query.filter(
                Event.start_date <= now,
                or_(Event.end_date.is_(None), Event.end_date >= now),
                Event.status == 'approved'
            )
        elif status == 'past':
            # Events that have ended
            # Past = (end_date < now) OR (end_date is None AND start_date < now)
            query = query.filter(
                or_(
                    (Event.end_date.isnot(None)) & (Event.end_date < now),
                    (Event.end_date.is_(None)) & (Event.start_date < now)
                ),
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
        # Check if poster_image is a base64 string in JSON (should not be allowed)
        if data.get('poster_image') and data['poster_image'].startswith('data:image'):
            return jsonify({'error': 'Please upload image as a file, not as base64 data URI'}), 400
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
        # Check if poster_image was sent as form field with base64 (should not be allowed)
        if 'poster_image' in request.form and request.form['poster_image'].startswith('data:image'):
            return jsonify({'error': 'Please upload image as a file, not as base64 data URI'}), 400
    
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
                # Handle ISO format with time: "2025-12-02T14:30:00" or "2025-12-02T14:30:00Z"
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            else:
                # Handle separate date and time
                end_time = data.get('end_time', '23:59')
                if ':' not in end_time:
                    end_time = '23:59'  # Default if invalid
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
    
    # Handle attendee capacity
    attendee_capacity = None
    if data.get('attendee_capacity') or data.get('attendeeLimit'):
        try:
            capacity_value = data.get('attendee_capacity') or data.get('attendeeLimit')
            if capacity_value and str(capacity_value).strip() and str(capacity_value) != '0':
                attendee_capacity = int(capacity_value)
        except (ValueError, TypeError):
            attendee_capacity = None
    
    # Create event
    event = Event(
        title=data['title'].strip(),
        description=data['description'].strip(),
        partner_id=current_partner.id,
        category_id=int(data['category_id']),
        start_date=start_date,
        end_date=end_date,
        attendee_capacity=attendee_capacity,
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
        
        # Remove duplicates by name to prevent multiple tickets with same name
        seen_names = set()
        unique_ticket_types = []
        for tt_data in ticket_types_data:
            name = tt_data.get('name', '').strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_ticket_types.append(tt_data)
        
        for tt_data in unique_ticket_types:
            # Skip if name is empty
            if not tt_data.get('name', '').strip():
                continue
                
            # Handle quantity - if empty string or 0, set to None (unlimited)
            quantity_value = tt_data.get('quantity')
            if quantity_value is None or quantity_value == '' or quantity_value == 0:
                quantity_total = None
                quantity_available = None
            else:
                quantity_total = int(quantity_value)
                quantity_available = quantity_total  # New ticket type, all available
            
            ticket_type = TicketType(
                event_id=event.id,
                name=tt_data.get('name', '').strip(),
                description=tt_data.get('description', ''),
                price=float(tt_data.get('price', 0)),
                quantity_total=quantity_total,
                quantity_available=quantity_available,
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
        # Check if poster_image is a base64 string in JSON (should not be allowed)
        if data.get('poster_image') and isinstance(data.get('poster_image'), str) and data['poster_image'].startswith('data:image'):
            return jsonify({'error': 'Please upload image as a file, not as base64 data URI'}), 400
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
        # Check if poster_image was sent as form field with base64 (should not be allowed)
        if 'poster_image' in request.form and isinstance(request.form['poster_image'], str) and request.form['poster_image'].startswith('data:image'):
            return jsonify({'error': 'Please upload image as a file, not as base64 data URI'}), 400
    
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
                # Handle ISO format with time: "2025-12-02T14:30:00" or "2025-12-02T14:30:00Z"
                event.end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            else:
                # Handle separate date and time
                end_time = data.get('end_time', '23:59')
                if ':' not in end_time:
                    end_time = '23:59'  # Default if invalid
                event.end_date = datetime.strptime(f"{end_date_str} {end_time}", "%Y-%m-%d %H:%M")
        except Exception as e:
            current_app.logger.warning(f'Error parsing end_date: {str(e)}')
    
    # Update attendee capacity
    if 'attendee_capacity' in data or 'attendeeLimit' in data:
        try:
            capacity_value = data.get('attendee_capacity') or data.get('attendeeLimit')
            if capacity_value and str(capacity_value).strip() and str(capacity_value) != '0':
                event.attendee_capacity = int(capacity_value)
            elif capacity_value == '' or capacity_value is None:
                event.attendee_capacity = None
        except (ValueError, TypeError):
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
            ticket_type_id = tt_data.get('id')
            
            # Try to find existing ticket type by ID first
            ticket_type = None
            if ticket_type_id and ticket_type_id in existing_ticket_ids:
                ticket_type = TicketType.query.get(ticket_type_id)
                if ticket_type and ticket_type.event_id != event.id:
                    ticket_type = None  # Wrong event, don't use it
            
            # If not found by ID, try to find by name (to avoid duplicates)
            if not ticket_type:
                ticket_name = tt_data.get('name', '').strip()
                if ticket_name:
                    ticket_type = TicketType.query.filter_by(
                        event_id=event.id,
                        name=ticket_name
                    ).first()
            
            if ticket_type:
                # Update existing ticket type
                ticket_type.name = tt_data.get('name', '').strip()
                ticket_type.price = float(tt_data.get('price', 0))
                ticket_type.description = tt_data.get('description', '')
                
                # Only update quantity if it's explicitly provided and different
                quantity_value = tt_data.get('quantity')
                
                # Check if quantity is being changed
                if quantity_value is not None and quantity_value != '':
                    # Convert to appropriate type for comparison
                    try:
                        quantity_value_int = int(quantity_value) if quantity_value != '' else None
                    except (ValueError, TypeError):
                        quantity_value_int = None
                    
                    # Only update if the value is actually different
                    if quantity_value_int != ticket_type.quantity_total:
                        if quantity_value_int is None or quantity_value_int == 0:
                            # Unlimited tickets
                            ticket_type.quantity_total = None
                            ticket_type.quantity_available = None
                        else:
                            # Limited tickets - recalculate available based on current sold count
                            current_sold = ticket_type.quantity_sold or 0
                            ticket_type.quantity_total = quantity_value_int
                            # Don't increase available - calculate from total minus sold
                            ticket_type.quantity_available = max(0, quantity_value_int - current_sold)
                # If quantity is not provided, keep existing values (don't change)
            else:
                # Create new ticket type only if it doesn't exist
                ticket_name = tt_data.get('name', '').strip()
                if ticket_name:
                    # Double-check it doesn't exist
                    existing = TicketType.query.filter_by(
                        event_id=event.id,
                        name=ticket_name
                    ).first()
                    
                    if not existing:
                        # Handle quantity - if empty string or 0, set to None (unlimited)
                        quantity_value = tt_data.get('quantity')
                        if quantity_value is None or quantity_value == '' or quantity_value == 0:
                            quantity_total = None
                            quantity_available = None
                        else:
                            quantity_total = int(quantity_value)
                            quantity_available = quantity_total  # New ticket type, all available
                        
                        ticket_type = TicketType(
                            event_id=event.id,
                            name=ticket_name,
                            description=tt_data.get('description', ''),
                            price=float(tt_data.get('price', 0)),
                            quantity_total=quantity_total,
                            quantity_available=quantity_available,
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
        
        # Get all existing promo codes for this event
        existing_promo_codes = PromoCode.query.filter_by(event_id=event.id).all()
        existing_promo_codes_by_id = {pc.id: pc for pc in existing_promo_codes}
        existing_promo_codes_by_code = {pc.code.upper(): pc for pc in existing_promo_codes}
        
        # Extract IDs from promo_data (handle both 'id' and 'existingId' fields from frontend)
        promo_ids_to_keep = []
        for promo_data in promo_codes_data:
            if promo_data.get('code'):
                # Check for existing ID in various formats
                promo_id = None
                if promo_data.get('id'):
                    # Handle string IDs like "existing-123" or numeric IDs
                    promo_id_str = str(promo_data['id'])
                    if promo_id_str.startswith('existing-'):
                        promo_id = int(promo_id_str.replace('existing-', ''))
                    else:
                        try:
                            promo_id = int(promo_data['id'])
                        except (ValueError, TypeError):
                            pass
                elif promo_data.get('existingId'):
                    promo_id = int(promo_data['existingId'])
                
                if promo_id and promo_id in existing_promo_codes_by_id:
                    promo_ids_to_keep.append(promo_id)
        
        # Delete promo codes not in the update list
        if promo_ids_to_keep:
            PromoCode.query.filter(
                PromoCode.event_id == event.id,
                ~PromoCode.id.in_(promo_ids_to_keep)
            ).delete(synchronize_session=False)
        else:
            # If no IDs to keep, delete all existing promo codes for this event
            PromoCode.query.filter_by(event_id=event.id).delete()
        
        # Update or create promo codes
        for promo_data in promo_codes_data:
            if not promo_data.get('code'):
                continue
                
            code = promo_data['code'].upper().strip()
            if not code:
                continue
            
            # Check for existing ID in various formats
            promo_id = None
            if promo_data.get('id'):
                promo_id_str = str(promo_data['id'])
                if promo_id_str.startswith('existing-'):
                    try:
                        promo_id = int(promo_id_str.replace('existing-', ''))
                    except (ValueError, TypeError):
                        pass
                else:
                    try:
                        promo_id = int(promo_data['id'])
                    except (ValueError, TypeError):
                        pass
            elif promo_data.get('existingId'):
                try:
                    promo_id = int(promo_data['existingId'])
                except (ValueError, TypeError):
                    pass
            
            # Check if this is an existing promo code to update
            if promo_id and promo_id in existing_promo_codes_by_id:
                # Update existing promo code
                promo_code = existing_promo_codes_by_id[promo_id]
                # Only update code if it's different and doesn't conflict
                new_code = code.upper().strip()  # Ensure code is always uppercase
                if promo_code.code.upper() != new_code:
                    # Check if new code already exists (for a different promo code)
                    existing_with_code = PromoCode.query.filter_by(code=new_code).first()
                    if existing_with_code and existing_with_code.id != promo_id:
                        # Code already exists for another promo code, skip updating this one
                        current_app.logger.warning(f'Promo code {new_code} already exists, skipping update for promo {promo_id}')
                        continue
                    promo_code.code = new_code
                
                promo_code.discount_type = promo_data.get('discount_type', 'percentage')
                promo_code.discount_value = float(promo_data.get('discount', 0))
                promo_code.max_uses = int(promo_data.get('max_uses', 0)) if promo_data.get('max_uses') else None
                if promo_data.get('expiry_date'):
                    try:
                        promo_code.valid_until = datetime.strptime(promo_data['expiry_date'], "%Y-%m-%d")
                    except:
                        pass
            else:
                # Create new - but check if code already exists (normalize to uppercase for comparison)
                existing_with_code = PromoCode.query.filter_by(code=code.upper().strip()).first()
                if existing_with_code:
                    # Code already exists, skip creating duplicate
                    current_app.logger.warning(f'Promo code {code} already exists, skipping creation')
                    continue
                
                promo_code = PromoCode(
                    code=code.upper().strip(),  # Ensure code is always uppercase
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
    
    # Handle quantity - if empty string or 0, set to None (unlimited)
    quantity_total = data.get('quantity_total')
    if quantity_total is None or quantity_total == '' or quantity_total == 0:
        quantity_total = None
        quantity_available = None
    else:
        quantity_total = int(quantity_total)
        quantity_available = quantity_total  # New ticket type, all available
    
    ticket_type = TicketType(
        event_id=event_id,
        name=data['name'].strip(),
        description=data.get('description'),
        price=data['price'],
        quantity_total=quantity_total,
        quantity_available=quantity_available,
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


@bp.route('/events/<int:event_id>/promo-codes/<int:promo_code_id>', methods=['PUT'])
@partner_required
def update_promo_code(current_partner, event_id, promo_code_id):
    """Update promo code for event"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    promo_code = PromoCode.query.filter_by(
        id=promo_code_id,
        event_id=event_id
    ).first()
    
    if not promo_code:
        return jsonify({'error': 'Promo code not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    if 'code' in data:
        new_code = data['code'].upper().strip()
        # Check if new code already exists (for a different promo code)
        existing = PromoCode.query.filter_by(code=new_code).first()
        if existing and existing.id != promo_code_id:
            return jsonify({'error': 'Promo code already exists'}), 409
        promo_code.code = new_code
    
    if 'discount_type' in data:
        promo_code.discount_type = data['discount_type']
    
    if 'discount_value' in data:
        promo_code.discount_value = float(data['discount_value'])
    
    if 'max_uses' in data:
        promo_code.max_uses = int(data['max_uses']) if data['max_uses'] else None
    
    if 'max_uses_per_user' in data:
        promo_code.max_uses_per_user = int(data.get('max_uses_per_user', 1))
    
    if 'valid_from' in data:
        if data['valid_from']:
            try:
                promo_code.valid_from = datetime.fromisoformat(data['valid_from'].replace('Z', '+00:00'))
            except:
                pass
        else:
            promo_code.valid_from = None
    
    if 'valid_until' in data:
        if data['valid_until']:
            try:
                promo_code.valid_until = datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00'))
            except:
                pass
        else:
            promo_code.valid_until = None
    
    if 'is_active' in data:
        promo_code.is_active = bool(data['is_active'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Promo code updated successfully',
        'promo_code': promo_code.to_dict()
    }), 200


@bp.route('/events/<int:event_id>/promo-codes/<int:promo_code_id>', methods=['DELETE'])
@partner_required
def delete_promo_code(current_partner, event_id, promo_code_id):
    """Delete promo code for event"""
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    promo_code = PromoCode.query.filter_by(
        id=promo_code_id,
        event_id=event_id
    ).first()
    
    if not promo_code:
        return jsonify({'error': 'Promo code not found'}), 404
    
    db.session.delete(promo_code)
    db.session.commit()
    
    return jsonify({
        'message': 'Promo code deleted successfully'
    }), 200


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
        # Past = (end_date < now) OR (end_date is None AND start_date < now)
        now = datetime.utcnow()
        is_current = False
        
        # Check if event is past
        is_past = False
        if event.end_date and event.end_date < now:
            is_past = True  # Past event (has ended)
        elif not event.end_date and event.start_date < now:
            is_past = True  # Past event (no end_date but start_date is past)
        
        # If not past, it's current (upcoming or ongoing)
        if not is_past:
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
    
    # Count past and current events from attendees
    past_events_count = sum(1 for a in attendees if not a['isCurrentEvent'])
    current_events_count = sum(1 for a in attendees if a['isCurrentEvent'])
    
    return jsonify({
        'attendees': attendees,
        'total': bookings.total,
        'page': bookings.page,
        'pages': bookings.pages,
        'past_events_count': past_events_count,
        'current_events_count': current_events_count
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
        # Use phone number from request if provided, otherwise use profile
        account_number = data.get('phone_number') or current_partner.mpesa_number
        if not account_number:
            return jsonify({'error': 'Please provide MPesa number'}), 400
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
        status='processing'  # Start as processing since we'll attempt B2C immediately
    )
    
    db.session.add(payout)
    db.session.flush()  # Get payout ID
    
    # For MPesa, automatically process B2C payment
    if payout_method == 'mpesa':
        try:
            from app.utils.mpesa import MPesaClient
            from app.utils.sms import format_phone_for_sms
            
            # Format phone number for MPesa
            formatted_phone = format_phone_for_sms(account_number)
            if not formatted_phone:
                payout.status = 'failed'
                payout.rejection_reason = 'Invalid phone number format'
                db.session.commit()
                return jsonify({'error': 'Invalid phone number format'}), 400
            
            # Initiate B2C payment
            mpesa = MPesaClient()
            b2c_response = mpesa.b2c_payment(
                phone_number=formatted_phone,
                amount=amount,
                occasion=f'Payout {payout.reference_number}'
            )
            
            # Store response
            payout.provider_response = b2c_response
            
            # Check if B2C was successful
            if b2c_response.get('ResponseCode') == '0' or b2c_response.get('error') is None:
                # B2C initiated successfully
                payout.status = 'processing'
                payout.transaction_reference = b2c_response.get('ConversationID') or b2c_response.get('OriginatorConversationID')
                current_app.logger.info(f'B2C payment initiated for payout {payout.id}: {b2c_response}')
            else:
                # B2C failed
                payout.status = 'failed'
                payout.rejection_reason = b2c_response.get('ResponseDescription') or b2c_response.get('error') or 'B2C payment failed'
                current_app.logger.error(f'B2C payment failed for payout {payout.id}: {b2c_response}')
                # Don't update balance if payment failed
                db.session.commit()
                return jsonify({
                    'error': payout.rejection_reason or 'Failed to process payment. Please try again.'
                }), 400
        except Exception as e:
            current_app.logger.error(f'Error processing B2C payment for payout {payout.id}: {str(e)}', exc_info=True)
            payout.status = 'failed'
            payout.rejection_reason = f'Payment processing error: {str(e)}'
            db.session.commit()
            return jsonify({
                'error': 'Failed to process payment. Please try again later.'
            }), 500
    else:
        # Bank transfer - keep as pending for admin approval
        payout.status = 'pending'
    
    # Update partner balance only if payment is processing/completed
    if payout.status in ['processing', 'completed']:
        current_partner.pending_earnings -= amount
        current_partner.withdrawn_earnings += amount
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payout request submitted successfully' if payout_method == 'bank_transfer' else 'Payment processing. You will receive funds shortly.',
        'payout': payout.to_dict()
    }), 201


# ============ EVENT PROMOTION ============

@bp.route('/events/<int:event_id>/promote', methods=['POST'])
@partner_required
def promote_event(current_partner, event_id):
    """Promote event to Can't Miss section"""
    data = request.get_json()
    
    # Get event
    event = Event.query.filter_by(
        id=event_id,
        partner_id=current_partner.id
    ).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Validate event status
    if event.status != 'approved':
        return jsonify({'error': 'Event must be approved before promotion'}), 400
    
    if not event.is_published:
        return jsonify({'error': 'Event must be published before promotion'}), 400
    
    # Get promotion details
    days_count = data.get('days_count', 7)  # Default 7 days
    is_free = data.get('is_free', False)  # Free promotion for testing
    
    # Allow custom start and end dates for scheduled promotions
    custom_start_date = data.get('start_date')  # ISO format datetime string
    custom_end_date = data.get('end_date')  # ISO format datetime string
    
    if custom_start_date and custom_end_date:
        # Parse custom dates
        try:
            from dateutil import parser
            start_date = parser.parse(custom_start_date)
            end_date = parser.parse(custom_end_date)
            
            # Validate dates
            if start_date >= end_date:
                return jsonify({'error': 'Start date must be before end date'}), 400
            
            if start_date < datetime.utcnow():
                return jsonify({'error': 'Start date cannot be in the past'}), 400
            
            # Calculate days_count from custom dates
            days_count = (end_date - start_date).days + 1  # Include both start and end days
            if days_count < 1 or days_count > 30:
                return jsonify({'error': 'Promotion period must be between 1 and 30 days'}), 400
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    else:
        # Use default behavior: start now, end after days_count
        if days_count < 1 or days_count > 30:
            return jsonify({'error': 'Promotion period must be between 1 and 30 days'}), 400
        
        start_date = datetime.utcnow()
        from datetime import timedelta
        end_date = start_date + timedelta(days=days_count)
    
    # Calculate cost (KES 400 per day for paid, 0 for free)
    cost_per_day = 400
    total_cost = 0 if is_free else days_count * cost_per_day
    
    # Check if there's an existing active promotion
    existing_promo = EventPromotion.query.filter_by(
        event_id=event_id,
        is_active=True
    ).first()
    
    if existing_promo:
        # Check if existing promotion is still valid
        if existing_promo.end_date > datetime.utcnow():
            return jsonify({
                'error': 'Event already has an active promotion',
                'promotion': existing_promo.to_dict()
            }), 400
    
    # Create promotion record
    promotion = EventPromotion(
        event_id=event_id,
        start_date=start_date,
        end_date=end_date,
        days_count=days_count,
        total_cost=total_cost,
        is_active=True,
        is_paid=not is_free  # Free promotions are not paid
    )
    
    db.session.add(promotion)
    db.session.flush()
    
    # Handle payment for paid promotions
    payment = None
    if not is_free:
        phone_number = data.get('phone_number')
        if not phone_number:
            db.session.rollback()
            return jsonify({'error': 'Phone number is required for paid promotion'}), 400
        
        # Format phone number
        from app.utils.mpesa import format_phone_number, MPesaClient
        phone = format_phone_number(phone_number)
        
        # Generate transaction ID
        import uuid
        transaction_id = f"PROMO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create payment record
        payment = Payment(
            transaction_id=transaction_id,
            partner_id=current_partner.id,
            event_id=event_id,
            amount=total_cost,
            platform_fee=0.00,
            partner_amount=0.00,  # Platform keeps all promotion fees
            payment_method='mpesa',
            payment_provider='daraja',
            phone_number=phone,
            description=f"Event promotion for {event.title} ({days_count} days)",
            payment_type='promotion',
            status='pending'
        )
        
        db.session.add(payment)
        db.session.flush()
        
        # Link payment to promotion
        promotion.payment_id = payment.id
        
        # Initiate MPesa STK Push
        mpesa = MPesaClient()
        response = mpesa.stk_push(
            phone_number=phone,
            amount=float(total_cost),
            account_reference=f"PROMO-{event.id}",
            transaction_desc=f"Promotion for {event.title}"
        )
        
        # Save response
        payment.provider_response = response
        
        if response.get('ResponseCode') == '0':
            # Success - STK push sent
            payment.payment_metadata = {
                'CheckoutRequestID': response.get('CheckoutRequestID'),
                'MerchantRequestID': response.get('MerchantRequestID')
            }
            db.session.commit()
            
            return jsonify({
                'message': 'Payment initiated. Please check your phone to complete payment.',
                'promotion': promotion.to_dict(),
                'payment_id': payment.id,
                'transaction_id': transaction_id,
                'checkout_request_id': response.get('CheckoutRequestID')
            }), 200
        else:
            # Failed
            payment.status = 'failed'
            payment.error_message = response.get('errorMessage') or response.get('ResponseDescription')
            promotion.is_paid = False
            promotion.is_active = False
            db.session.commit()
            
            return jsonify({
                'error': 'Failed to initiate payment',
                'message': payment.error_message
            }), 400
    else:
        # Free promotion - activate immediately
        promotion.is_paid = False
        promotion.is_active = True
        db.session.commit()
        
        return jsonify({
            'message': 'Event promoted successfully (free promotion)',
            'promotion': promotion.to_dict()
        }), 200

