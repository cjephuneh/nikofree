from datetime import datetime
from app import db


class Event(db.Model):
    """Event model"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    poster_image = db.Column(db.String(500), nullable=True)
    
    # Organizer
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id', ondelete='CASCADE'), nullable=False)
    
    # Category and Interests
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Date and Time
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=True)
    attendee_capacity = db.Column(db.Integer, nullable=True)  # Maximum number of attendees
    
    # Location
    is_online = db.Column(db.Boolean, default=False)
    venue_name = db.Column(db.String(200), nullable=True)
    venue_address = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    online_link = db.Column(db.String(500), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    
    # Ticket Information
    is_free = db.Column(db.Boolean, default=True)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, published, cancelled, completed
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Visibility
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    attendee_count = db.Column(db.Integer, default=0)
    total_tickets_sold = db.Column(db.Integer, default=0)
    revenue = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    category = db.relationship('Category', backref='events')
    location = db.relationship('Location', backref='events')
    hosts = db.relationship('EventHost', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    interests = db.relationship('EventInterest', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    ticket_types = db.relationship('TicketType', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    promotions = db.relationship('EventPromotion', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    promo_codes = db.relationship('PromoCode', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_stats=False):
        """Convert event to dictionary"""
        # Filter out base64 data URIs from poster_image (they shouldn't be in DB, but handle if they are)
        poster_image = self.poster_image
        if poster_image and poster_image.startswith('data:image'):
            # If somehow a base64 string got stored, return None so frontend can handle it
            poster_image = None
        
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'poster_image': poster_image,
            'partner': self.organizer.to_dict() if self.organizer else None,
            'category': self.category.to_dict() if self.category else None,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'attendee_capacity': self.attendee_capacity,
            'is_online': self.is_online,
            'venue_name': self.venue_name,
            'venue_address': self.venue_address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'online_link': self.online_link,
            'location': self.location.to_dict() if self.location else None,
            'is_free': self.is_free,
            'status': self.status,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'hosts': [host.to_dict() for host in self.hosts],
            'interests': [interest.name for interest in self.interests],
            'ticket_types': [tt.to_dict() for tt in self.ticket_types],
            'promo_codes': [pc.to_dict() for pc in self.promo_codes]
        }
        
        if include_stats:
            data['view_count'] = self.view_count
            data['attendee_count'] = self.attendee_count
            data['total_tickets_sold'] = self.total_tickets_sold
            data['revenue'] = float(self.revenue)
            # Add bucketlist count (likes) - query the bucketlist table directly
            from app.models.user import bucketlist
            from sqlalchemy import func
            bucketlist_count = db.session.query(func.count(bucketlist.c.user_id)).filter(
                bucketlist.c.event_id == self.id
            ).scalar() or 0
            data['bucketlist_count'] = bucketlist_count
            # Add actual bookings count (people going)
            bookings_count = self.bookings.filter_by(status='confirmed').count()
            data['bookings_count'] = bookings_count
            
        return data
    
    def __repr__(self):
        return f'<Event {self.title}>'


class EventHost(db.Model):
    """Event host association"""
    __tablename__ = 'event_hosts'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(100), default='Host')
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='hosted_events')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'role': self.role
        }


class EventInterest(db.Model):
    """Event interests/tags"""
    __tablename__ = 'event_interests'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<EventInterest {self.name}>'


class EventPromotion(db.Model):
    """Event promotion (Can't Miss banner)"""
    __tablename__ = 'event_promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    days_count = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.Numeric(10, 2), nullable=False)  # KES 400/day
    
    is_active = db.Column(db.Boolean, default=True)
    is_paid = db.Column(db.Boolean, default=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, include_status=False):
        """Convert promotion to dictionary"""
        data = {
            'id': self.id,
            'event_id': self.event_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'days_count': self.days_count,
            'total_cost': float(self.total_cost),
            'is_active': self.is_active,
            'is_paid': self.is_paid
        }
        
        if include_status:
            from datetime import datetime
            now = datetime.utcnow()
            data['is_active_now'] = self.start_date <= now <= self.end_date
            if now < self.start_date:
                data['time_until_start'] = (self.start_date - now).total_seconds()
            elif now > self.end_date:
                data['time_until_end'] = 0
            else:
                data['time_until_end'] = (self.end_date - now).total_seconds()
        
        return data

