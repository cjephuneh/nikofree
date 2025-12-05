from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import or_, and_
from app import db, limiter
from app.models.event import Event, EventHost, EventInterest, EventPromotion
from app.models.category import Category, Location
from app.models.user import User
from sqlalchemy import func
from app.utils.decorators import optional_user, user_required
from app.utils.file_upload import upload_file

bp = Blueprint('events', __name__)


@bp.route('/', methods=['GET'])
@bp.route('', methods=['GET'])  # Also handle without trailing slash
@optional_user
@limiter.exempt
def get_events(current_user):
    """Get all events with filters"""
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    location = request.args.get('location')
    search = request.args.get('search', '').strip()
    is_free = request.args.get('is_free')
    featured = request.args.get('featured', 'false').lower() == 'true'
    this_weekend = request.args.get('this_weekend', 'false').lower() == 'true'
    
    # Base query - only published and approved events
    query = Event.query.filter(
        Event.is_published == True,
        Event.status == 'approved',
        Event.start_date > datetime.utcnow()
    )
    
    # Filter by category
    if category:
        cat = Category.query.filter_by(slug=category).first()
        if cat:
            query = query.filter(Event.category_id == cat.id)
    
    # Filter by location
    if location:
        loc = Location.query.filter_by(slug=location).first()
        if loc:
            query = query.filter(Event.location_id == loc.id)
    
    # Filter by free/paid
    if is_free is not None:
        is_free_bool = is_free.lower() == 'true'
        query = query.filter(Event.is_free == is_free_bool)
    
    # Filter featured
    if featured:
        query = query.filter(Event.is_featured == True)
    
    # Filter this weekend
    if this_weekend:
        from datetime import timedelta
        today = datetime.utcnow()
        # Find next Saturday and Sunday
        days_until_saturday = (5 - today.weekday()) % 7
        saturday = (today + timedelta(days=days_until_saturday)).replace(hour=0, minute=0, second=0)
        sunday = saturday + timedelta(days=1)
        monday = sunday + timedelta(days=1)
        
        query = query.filter(
            Event.start_date >= saturday,
            Event.start_date < monday
        )
    
    # Search by keyword
    if search:
        query = query.filter(
            or_(
                Event.title.ilike(f'%{search}%'),
                Event.description.ilike(f'%{search}%')
            )
        )
    
    # Order by date
    query = query.order_by(Event.start_date.asc())
    
    # Paginate
    events = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Build events list with bucketlist status
    events_list = []
    for event in events.items:
        event_dict = event.to_dict()
        # Check if event is in user's bucketlist
        if current_user:
            event_dict['in_bucketlist'] = event in current_user.bucketlist
        else:
            event_dict['in_bucketlist'] = False
        events_list.append(event_dict)
    
    return jsonify({
        'events': events_list,
        'total': events.total,
        'page': events.page,
        'pages': events.pages,
        'per_page': events.per_page
    }), 200


@bp.route('/<int:event_id>', methods=['GET'])
@optional_user
def get_event(current_user, event_id):
    """Get single event"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if user can view this event
    # Allow viewing unpublished events if user is logged in (for now)
    # In production, you might want to restrict this to organizers and admins only
    if not event.is_published or event.status != 'approved':
        if not current_user:
            return jsonify({'error': 'Event not found or not available'}), 404
        # For logged-in users, allow viewing unpublished events
        # This helps with testing and allows users to see events they're interested in
    
    # Increment view count
    event.view_count += 1
    db.session.commit()
    
    # Check if user has bookmarked this event
    in_bucketlist = False
    if current_user:
        in_bucketlist = event in current_user.bucketlist
    
    event_data = event.to_dict(include_stats=True)
    event_data['in_bucketlist'] = in_bucketlist
    
    # Show full attendee count only if user is logged in
    if not current_user:
        event_data['attendee_count_blurred'] = True
    
    return jsonify({'event': event_data}), 200


@bp.route('/promoted', methods=['GET'])
def get_promoted_events():
    """Get promoted events (Can't Miss banner)"""
    # Get active promotions (both free and paid)
    now = datetime.utcnow()
    
    # Only show promotions that are currently active (between start and end time)
    # This ensures events only show during their scheduled promotion window
    promotions = EventPromotion.query.filter(
        EventPromotion.is_active == True,
        EventPromotion.start_date <= now,
        EventPromotion.end_date >= now
    ).order_by(
        EventPromotion.is_paid.desc(),  # Paid promotions first
        EventPromotion.start_date.asc()  # Then by start date (earliest first)
    ).limit(10).all()
    
    events = []
    for promo in promotions:
        if promo.event and promo.event.is_published and promo.event.status == 'approved':
            # Check if event is past - use end_date if available, otherwise start_date
            event_end_date = promo.event.end_date if promo.event.end_date else promo.event.start_date
            if event_end_date < now:
                # Event is past, skip it
                continue
            
            event_dict = promo.event.to_dict()
            
            # Calculate promotion status
            time_until_start = None
            time_until_end = None
            is_active_now = promo.start_date <= now <= promo.end_date
            
            if now < promo.start_date:
                # Promotion hasn't started yet
                time_until_start = (promo.start_date - now).total_seconds()
            elif now > promo.end_date:
                # Promotion has ended
                time_until_end = 0
            else:
                # Promotion is active
                time_until_end = (promo.end_date - now).total_seconds()
            
            # Include promotion info with status
            event_dict['promotion'] = {
                'id': promo.id,
                'is_paid': promo.is_paid,
                'days_count': promo.days_count,
                'start_date': promo.start_date.isoformat(),
                'end_date': promo.end_date.isoformat(),
                'is_active_now': is_active_now,
                'time_until_start': time_until_start,  # seconds until start (None if already started)
                'time_until_end': time_until_end,  # seconds until end (None if not started or already ended)
                'total_cost': float(promo.total_cost)
            }
            events.append(event_dict)
    
    return jsonify({
        'events': events,
        'count': len(events)
    }), 200


@bp.route('/categories', methods=['GET', 'OPTIONS'])
@bp.route('/categories/', methods=['GET', 'OPTIONS'])
@limiter.exempt
def get_categories():
    """Get all event categories"""
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        from flask import make_response
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response, 200
    
    from sqlalchemy import func
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order).all()
    
    # Add event count for each category
    categories_data = []
    for cat in categories:
        cat_dict = cat.to_dict()
        # Count upcoming approved events in this category
        event_count = Event.query.filter(
            Event.category_id == cat.id,
            Event.is_published == True,
            Event.status == 'approved',
            Event.start_date > datetime.utcnow()
        ).count()
        cat_dict['event_count'] = event_count
        categories_data.append(cat_dict)
    
    response = jsonify({
        'categories': categories_data
    })
    # Ensure CORS headers are set
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept')
    return response, 200


@bp.route('/categories/<int:category_id>/events', methods=['GET'])
def get_category_events(category_id):
    """Get events by category with preview"""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Get upcoming events in this category
    events = Event.query.filter(
        Event.category_id == category_id,
        Event.is_published == True,
        Event.status == 'approved',
        Event.start_date > datetime.utcnow()
    ).order_by(Event.start_date.asc()).limit(10).all()
    
    return jsonify({
        'category': category.to_dict(),
        'events': [event.to_dict() for event in events],
        'count': len(events)
    }), 200


@bp.route('/locations', methods=['GET'])
@limiter.exempt
def get_locations():
    """Get all locations"""
    locations = Location.query.filter_by(is_active=True).order_by(Location.display_order).all()
    
    return jsonify({
        'locations': [loc.to_dict() for loc in locations]
    }), 200


@bp.route('/<int:event_id>/share', methods=['POST'])
def generate_share_link(event_id):
    """Generate shareable link for event"""
    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    from flask import current_app
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
    
    share_data = {
        'link': f"{frontend_url}/events/{event_id}",
        'whatsapp': f"https://wa.me/?text=Check out this event: {event.title} - {frontend_url}/events/{event_id}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={frontend_url}/events/{event_id}",
        'email': f"mailto:?subject={event.title}&body=Check out this event: {frontend_url}/events/{event_id}",
        'title': event.title,
        'description': event.description[:200]
    }
    
    return jsonify(share_data), 200


@bp.route('/calendar', methods=['GET'])
def get_calendar_events():
    """Get events for calendar view"""
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Event.query.filter(
        Event.is_published == True,
        Event.status == 'approved'
    )
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Event.start_date >= start)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Event.start_date <= end)
        except:
            pass
    
    events = query.order_by(Event.start_date).all()
    
    # Format for calendar
    calendar_events = []
    for event in events:
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat() if event.end_date else event.start_date.isoformat(),
            'url': f"/events/{event.id}",
            'category': event.category.name if event.category else None,
            'is_free': event.is_free
        })
    
    return jsonify({
        'events': calendar_events
    }), 200


@bp.route('/this-weekend', methods=['GET'])
def get_this_weekend_events():
    """Get events happening this weekend"""
    from datetime import timedelta
    
    today = datetime.utcnow()
    days_until_saturday = (5 - today.weekday()) % 7
    
    if days_until_saturday == 0:
        saturday = today.replace(hour=0, minute=0, second=0)
    else:
        saturday = (today + timedelta(days=days_until_saturday)).replace(hour=0, minute=0, second=0)
    
    sunday = saturday + timedelta(days=1)
    monday = sunday + timedelta(days=1)
    
    events = Event.query.filter(
        Event.is_published == True,
        Event.status == 'approved',
        Event.start_date >= saturday,
        Event.start_date < monday
    ).order_by(Event.start_date).all()
    
    return jsonify({
        'events': [event.to_dict() for event in events],
        'count': len(events),
        'weekend_start': saturday.isoformat(),
        'weekend_end': sunday.isoformat()
    }), 200


@bp.route('/search/autocomplete', methods=['GET'])
def autocomplete_search():
    """Autocomplete search suggestions"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'suggestions': []}), 200
    
    # Search events
    events = Event.query.filter(
        Event.is_published == True,
        Event.status == 'approved',
        Event.title.ilike(f'%{query}%')
    ).limit(5).all()
    
    suggestions = []
    for event in events:
        suggestions.append({
            'type': 'event',
            'id': event.id,
            'title': event.title,
            'subtitle': event.category.name if event.category else None
        })
    
    # Search categories
    categories = Category.query.filter(
        Category.is_active == True,
        Category.name.ilike(f'%{query}%')
    ).limit(3).all()
    
    for cat in categories:
        suggestions.append({
            'type': 'category',
            'id': cat.id,
            'title': cat.name,
            'subtitle': 'Category'
        })
    
    return jsonify({
        'suggestions': suggestions
    }), 200


# ============ REVIEWS ============

@bp.route('/<int:event_id>/reviews', methods=['GET'])
@optional_user
def get_event_reviews(current_user, event_id):
    """Get reviews for an event"""
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if user can view this event (same logic as get_event)
    # Allow viewing reviews for unpublished events if user is logged in
    if not event.is_published or event.status != 'approved':
        if not current_user:
            return jsonify({'error': 'Event not found or not available'}), 404
        # For logged-in users, allow viewing reviews for unpublished events
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    from app.models.review import Review
    reviews = Review.query.filter_by(event_id=event_id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate average rating
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(
        event_id=event_id
    ).scalar() or 0
    
    total_reviews = Review.query.filter_by(event_id=event_id).count()
    
    return jsonify({
        'reviews': [review.to_dict() for review in reviews.items],
        'average_rating': round(float(avg_rating), 1),
        'total_reviews': total_reviews,
        'page': reviews.page,
        'pages': reviews.pages
    }), 200


@bp.route('/<int:event_id>/reviews', methods=['POST'])
@user_required
def add_event_review(current_user, event_id):
    """Add review to event - only for past events that user has booked"""
    from app.models.review import Review
    from app.models.ticket import Booking
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Check if event is published and approved
    if not event.is_published or event.status != 'approved':
        return jsonify({'error': 'Event not available for review'}), 403
    
    # Check if user has booked this event
    booking = Booking.query.filter_by(
        user_id=current_user.id,
        event_id=event_id,
        status='confirmed'
    ).first()
    
    if not booking:
        return jsonify({
            'error': 'You can only review events you have booked and attended'
        }), 403
    
    # Check if event has ended (user can only review past events)
    now = datetime.utcnow()
    event_end_date = event.end_date if event.end_date else event.start_date
    
    if event_end_date > now:
        return jsonify({
            'error': 'You can only review events that have ended. Please wait until after the event.'
        }), 403
    
    data = request.get_json()
    
    if not data or not data.get('rating'):
        return jsonify({'error': 'Rating is required'}), 400
    
    rating = int(data['rating'])
    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if user already reviewed this event
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if existing_review:
        return jsonify({'error': 'You have already reviewed this event'}), 409
    
    # Create review
    review = Review(
        user_id=current_user.id,
        event_id=event_id,
        rating=rating,
        comment=data.get('comment', '').strip() if data.get('comment') else ''
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review added successfully',
        'review': review.to_dict()
    }), 201


@bp.route('/<int:event_id>/reviews/<int:review_id>', methods=['PUT'])
@user_required
def update_event_review(current_user, event_id, review_id):
    """Update review"""
    from app.models.review import Review
    
    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    data = request.get_json()
    
    if data.get('rating'):
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        review.rating = rating
    
    if data.get('comment') is not None:
        review.comment = data['comment'].strip()
    
    review.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': review.to_dict()
    }), 200


@bp.route('/<int:event_id>/reviews/<int:review_id>', methods=['DELETE'])
@user_required
def delete_event_review(current_user, event_id, review_id):
    """Delete review"""
    from app.models.review import Review
    
    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review deleted successfully'
    }), 200

