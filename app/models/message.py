from datetime import datetime
from app import db


class Feedback(db.Model):
    """Feedback model for user feedback submissions"""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User Information (optional)
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    
    # Feedback Content
    feedback_type = db.Column(db.String(50), nullable=False)  # suggestion, bug, compliment, other
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_starred = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': 'feedback',
            'name': self.name or 'Anonymous',
            'email': self.email,
            'title': self.title,
            'description': self.description,
            'feedbackType': self.feedback_type,
            'rating': self.rating,
            'date': self.created_at.isoformat(),
            'isRead': self.is_read,
            'isStarred': self.is_starred,
            'isArchived': self.is_archived,
            'readAt': self.read_at.isoformat() if self.read_at else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }


class ContactMessage(db.Model):
    """Contact message model for contact form submissions"""
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User Information
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # Message Content
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_starred = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': 'contact',
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'date': self.created_at.isoformat(),
            'isRead': self.is_read,
            'isStarred': self.is_starred,
            'isArchived': self.is_archived,
            'readAt': self.read_at.isoformat() if self.read_at else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }

