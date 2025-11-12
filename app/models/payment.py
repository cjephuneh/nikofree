from datetime import datetime
from app import db


class Payment(db.Model):
    """Payment transactions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # References
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=True)
    
    # Payment Details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='KES')
    
    # Commission
    platform_fee = db.Column(db.Numeric(10, 2), default=0.00)
    partner_amount = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Payment Method
    payment_method = db.Column(db.String(50), nullable=False)  # mpesa, card, bank
    payment_provider = db.Column(db.String(50), nullable=True)  # daraja, stripe, etc
    
    # MPesa Details
    mpesa_receipt_number = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    
    # Metadata
    description = db.Column(db.String(500), nullable=True)
    payment_type = db.Column(db.String(50), nullable=True)  # ticket, promotion, etc
    metadata = db.Column(db.JSON, nullable=True)
    
    # Provider Response
    provider_response = db.Column(db.JSON, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    failed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'platform_fee': float(self.platform_fee),
            'partner_amount': float(self.partner_amount),
            'payment_method': self.payment_method,
            'mpesa_receipt_number': self.mpesa_receipt_number,
            'status': self.status,
            'description': self.description,
            'payment_type': self.payment_type,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class PartnerPayout(db.Model):
    """Partner withdrawal/payout requests"""
    __tablename__ = 'partner_payouts'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # References
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id', ondelete='CASCADE'), nullable=False)
    
    # Amount
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='KES')
    
    # Payout Method
    payout_method = db.Column(db.String(50), nullable=False)  # mpesa, bank_transfer
    account_number = db.Column(db.String(100), nullable=False)
    account_name = db.Column(db.String(200), nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed, cancelled
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Response
    transaction_reference = db.Column(db.String(100), nullable=True)
    provider_response = db.Column(db.JSON, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reference_number': self.reference_number,
            'amount': float(self.amount),
            'currency': self.currency,
            'payout_method': self.payout_method,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

