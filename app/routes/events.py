from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import or_, and_
from app import db
from app.models.event import Event, EventHost, EventInterest, EventPromotion
from app.models.category import Category, Location
from app.models.user import User
from app.utils.decorators import optional_user, user_required
from app.utils.file_upload import upload_file

bp = Blueprint('events', __name__)


@bp.route('/', methods=['GET'])
@optional_user
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
    
    return jsonify({
        'events': [event.to_dict() for event in events.items],
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
    if not event.is_published or event.status != 'approved':
        # Only organizer and admin can view unpublished events
        if not current_user:
            return jsonify({'error': 'Event not found'}), 404
    
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
    
    return jsonify(event_data), 200


@bp.route('/promoted', methods=['GET'])
def get_promoted_events():
    """Get promoted events (Can't Miss banner)"""
    # Get active promotions
    now = datetime.utcnow()
    
    promotions = EventPromotion.query.filter(
        EventPromotion.is_active == True,
        EventPromotion.is_paid == True,
        EventPromotion.start_date <= now,
        EventPromotion.end_date >= now
    ).limit(10).all()
    
    events = []
    for promo in promotions:
        if promo.event and promo.event.is_published and promo.event.status == 'approved':
            events.append(promo.event.to_dict())
    
    return jsonify({
        'events': events,
        'count': len(events)
    }), 200


@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all event categories"""
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order).all()
    
    return jsonify({
        'categories': [cat.to_dict() for cat in categories]
    }), 200


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

