from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Partner(db.Model):
    """Partner model for event organizers"""
    __tablename__ = 'partners'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Account Information
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Business Information
    business_name = db.Column(db.String(200), nullable=False, index=True)
    logo = db.Column(db.String(500), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    # Contact Information
    contact_person = db.Column(db.String(200), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    
    # Legal
    contract_accepted = db.Column(db.Boolean, default=False)
    contract_accepted_at = db.Column(db.DateTime, nullable=True)
    
    # Approval Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, suspended
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Financial
    total_earnings = db.Column(db.Numeric(10, 2), default=0.00)
    pending_earnings = db.Column(db.Numeric(10, 2), default=0.00)
    withdrawn_earnings = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Bank Information (for payouts)
    bank_name = db.Column(db.String(100), nullable=True)
    bank_account_number = db.Column(db.String(50), nullable=True)
    bank_account_name = db.Column(db.String(200), nullable=True)
    mpesa_number = db.Column(db.String(20), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    events = db.relationship('Event', backref='organizer', lazy='dynamic', cascade='all, delete-orphan')
    payouts = db.relationship('PartnerPayout', backref='partner', lazy='dynamic', cascade='all, delete-orphan')
    category = db.relationship('Category', backref='partners')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert partner to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'phone_number': self.phone_number,
            'business_name': self.business_name,
            'logo': self.logo,
            'category': self.category.to_dict() if self.category else None,
            'contact_person': self.contact_person,
            'website': self.website,
            'status': self.status,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }
        
        if include_sensitive:
            data['total_earnings'] = float(self.total_earnings)
            data['pending_earnings'] = float(self.pending_earnings)
            data['withdrawn_earnings'] = float(self.withdrawn_earnings)
            data['bank_name'] = self.bank_name
            data['bank_account_number'] = self.bank_account_number
            data['mpesa_number'] = self.mpesa_number
            
        return data
    
    def __repr__(self):
        return f'<Partner {self.business_name}>'

