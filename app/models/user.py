from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User model for attendees"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    
    # Profile Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    
    # OAuth Information
    google_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    apple_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    oauth_provider = db.Column(db.String(50), nullable=True)  # 'google', 'apple', 'email'
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False, index=True)  # Admin access flag
    
    # Preferences
    keep_logged_in = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(200), nullable=True)
    
    # Password Reset
    reset_token = db.Column(db.String(255), nullable=True, unique=True, index=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    bucketlist = db.relationship('Event', secondary='bucketlist', backref='wishlist_users', lazy='dynamic')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    admin_notifications = db.relationship('Notification', foreign_keys='Notification.admin_id', backref='admin_user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'profile_picture': self.profile_picture,
            'oauth_provider': self.oauth_provider,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'location': self.location,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['email_verified'] = self.email_verified
            data['phone_verified'] = self.phone_verified
            
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'


# Bucketlist association table
bucketlist = db.Table('bucketlist',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)

