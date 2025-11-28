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
    description = db.Column(db.Text, nullable=True)  # Business description
    
    # Application Information
    location = db.Column(db.String(200), nullable=True)  # City/Location for application
    interests = db.Column(db.Text, nullable=True)  # JSON string of additional interests
    signature_name = db.Column(db.String(200), nullable=True)  # Name as signature
    terms_accepted = db.Column(db.Boolean, default=False)
    terms_accepted_at = db.Column(db.DateTime, nullable=True)
    
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
    # New relationships
    support_requests = db.relationship('PartnerSupportRequest', backref='partner', lazy='dynamic', cascade='all, delete-orphan')
    team_members = db.relationship('PartnerTeamMember', backref='partner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert partner to dictionary"""
        # Filter out base64 data URIs from logo (they shouldn't be in DB, but handle if they are)
        logo = self.logo
        if logo and logo.startswith('data:image'):
            # If somehow a base64 string got stored, return None so frontend can handle it
            logo = None
        
        data = {
            'id': self.id,
            'email': self.email,
            'phone_number': self.phone_number,
            'business_name': self.business_name,
            'logo': logo,
            'category': self.category.to_dict() if self.category else None,
            'contact_person': self.contact_person,
            'address': self.address,
            'website': self.website,
            'location': self.location,
            'description': self.description,
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


class PartnerSupportRequest(db.Model):
    """Support requests created by partners"""
    __tablename__ = 'partner_support_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id', ondelete='CASCADE'), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class PartnerTeamMember(db.Model):
    """Team members / managers that help manage partner events"""
    __tablename__ = 'partner_team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(50), default='Manager')
    permissions = db.Column(db.Text, nullable=True)  # JSON-encoded list of permissions
    is_active = db.Column(db.Boolean, default=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        import json as _json
        perms: list[str] = []
        if self.permissions:
            try:
                perms = _json.loads(self.permissions)
            except Exception:
                # Fallback if stored as comma-separated string
                perms = [p.strip() for p in self.permissions.split(',') if p.strip()]
        
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'permissions': perms,
            'is_active': self.is_active,
            'added_at': self.added_at.isoformat() if self.added_at else None,
        }

