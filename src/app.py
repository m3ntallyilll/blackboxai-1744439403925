from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from .email_manager import EmailManager
from .groq_handler import GroqHandler
from .auth import auth_bp, login_required, subscription_required
from .models import init_db, Session as DbSession, User, EmailHistory
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_key_replace_in_production')

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

# Initialize services
email_manager = EmailManager()
groq_handler = GroqHandler()

@app.route('/')
@login_required
def index():
    db = DbSession()
    user = db.query(User).get(session['user_id'])
    
    # Get statistics
    stats = {
        'processed_emails': db.query(EmailHistory).filter_by(user_id=user.id).count(),
        'ai_analysis': db.query(EmailHistory).filter_by(user_id=user.id).count(),  # Same as processed for now
        'time_saved': f"{db.query(EmailHistory).filter_by(user_id=user.id).count() * 5}m"  # Estimate 5 minutes saved per email
    }
    
    return render_template('index.html', stats=stats)

@app.route('/settings')
@login_required
def settings():
    db = DbSession()
    user = db.query(User).get(session['user_id'])
    return render_template('settings.html', user=user)

@app.route('/history')
@login_required
def history():
    return render_template('history.html')

@app.route('/api/history')
@login_required
def get_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    importance = request.args.get('importance')
    sentiment = request.args.get('sentiment')
    date_range = request.args.get('date_range')
    
    db = DbSession()
    query = db.query(EmailHistory).filter_by(user_id=session['user_id'])
    
    # Apply filters
    if category:
        query = query.filter_by(category=category)
    if importance:
        query = query.filter_by(importance=importance)
    if sentiment:
        query = query.filter_by(sentiment=sentiment)
    if date_range:
        if date_range == 'today':
            query = query.filter(EmailHistory.processed_at >= datetime.today())
        elif date_range == 'week':
            query = query.filter(EmailHistory.processed_at >= datetime.today() - timedelta(days=7))
        elif date_range == 'month':
            query = query.filter(EmailHistory.processed_at >= datetime.today() - timedelta(days=30))
    
    # Paginate results
    total = query.count()
    history = query.order_by(EmailHistory.processed_at.desc())\
                  .offset((page - 1) * per_page)\
                  .limit(per_page)\
                  .all()
    
    return jsonify({
        'status': 'success',
        'history': [{
            'id': h.id,
            'sender': h.sender,
            'subject': h.subject,
            'processed_at': h.processed_at.isoformat(),
            'category': h.category,
            'importance': h.importance,
            'sentiment': h.sentiment,
            'ai_analysis': h.ai_analysis,
            'suggested_actions': h.suggested_actions
        } for h in history],
        'total': total
    })

@app.route('/api/refresh-emails', methods=['GET'])
@login_required
@subscription_required
def refresh_emails():
    try:
        emails = email_manager.fetch_recent_emails()
        db = DbSession()
        
        processed_emails = []
        for email in emails:
            analysis = groq_handler.analyze_email(
                email_content=email['body'],
                sender=email['from'],
                subject=email['subject']
            )
            
            # Save to history
            history = EmailHistory(
                user_id=session['user_id'],
                sender=email['from'],
                subject=email['subject'],
                category=analysis['category'],
                importance=analysis['importance'],
                sentiment=analysis['sentiment'],
                ai_analysis=analysis['summary'],
                suggested_actions=analysis.get('required_action')
            )
            db.add(history)
            
            email['analysis'] = analysis
            processed_emails.append(email)
        
        db.commit()
        return jsonify({"status": "success", "emails": processed_emails})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.context_processor
def utility_processor():
    def has_active_subscription():
        if 'user_id' not in session:
            return False
        db = DbSession()
        user = db.query(User).get(session['user_id'])
        return user and user.has_active_subscription
    return dict(has_active_subscription=has_active_subscription)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
