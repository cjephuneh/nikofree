from datetime import datetime
from app import db


class AdminLog(db.Model):
    """Admin activity logs"""
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Admin User
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    admin_email = db.Column(db.String(120), nullable=False)
    
    # Action
    action = db.Column(db.String(100), nullable=False)  # approve_partner, reject_event, suspend_partner, etc
    resource_type = db.Column(db.String(50), nullable=False)  # partner, event, user, etc
    resource_id = db.Column(db.Integer, nullable=True)
    
    # Details
    description = db.Column(db.Text, nullable=True)
    changes = db.Column(db.JSON, nullable=True)  # Store what changed
    
    # Metadata
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_email': self.admin_email,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

