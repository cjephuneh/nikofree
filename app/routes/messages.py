from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app import db, limiter
from app.models.message import Feedback, ContactMessage
from app.utils.validators import validate_email

bp = Blueprint('messages', __name__)


@bp.route('/feedback', methods=['POST'])
@limiter.limit("10 per minute")
def submit_feedback():
    """Submit feedback"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('description'):
            return jsonify({'error': 'Title and description are required'}), 400
        
        # Validate feedback type
        feedback_type = data.get('feedbackType', 'suggestion')
        if feedback_type not in ['suggestion', 'bug', 'compliment', 'other']:
            feedback_type = 'other'
        
        # Validate email if provided
        email = data.get('email', '').strip()
        if email and not validate_email(email):
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Validate rating if provided
        rating = data.get('rating')
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    rating = None
            except (ValueError, TypeError):
                rating = None
        
        # Create feedback
        feedback = Feedback(
            name=data.get('name', '').strip() or None,
            email=email or None,
            feedback_type=feedback_type,
            title=data.get('title', '').strip(),
            description=data.get('description', '').strip(),
            rating=rating
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'message': 'Thank you for your feedback! We appreciate your input.',
            'id': feedback.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'error': 'Failed to submit feedback. Please try again.'}), 500


@bp.route('/contact', methods=['POST'])
@limiter.limit("10 per minute")
def submit_contact():
    """Submit contact message"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('email') or not data.get('subject') or not data.get('message'):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validate email
        email = data.get('email', '').strip()
        if not validate_email(email):
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Create contact message
        contact = ContactMessage(
            name=data.get('name', '').strip(),
            email=email,
            subject=data.get('subject', '').strip(),
            message=data.get('message', '').strip()
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully! We\'ll get back to you soon.',
            'id': contact.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting contact message: {str(e)}")
        return jsonify({'error': 'Failed to send message. Please try again.'}), 500

