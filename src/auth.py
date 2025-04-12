from functools import wraps
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Session as DbSession, User, Subscription
import stripe
import os
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        db = DbSession()
        user = db.query(User).get(session['user_id'])
        if not user.has_active_subscription:
            return redirect(url_for('auth.subscription'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = DbSession()
        user = db.query(User).filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        
        flash('Invalid email or password')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        db = DbSession()
        if db.query(User).filter_by(email=email).first():
            flash('Email already registered')
            return render_template('auth/register.html')
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            name=name
        )
        db.add(user)
        db.commit()
        
        session['user_id'] = user.id
        return redirect(url_for('auth.subscription'))
    
    return render_template('auth/register.html')

@auth_bp.route('/subscription', methods=['GET', 'POST'])
@login_required
def subscription():
    db = DbSession()
    user = db.query(User).get(session['user_id'])
    
    if request.method == 'POST':
        plan_type = request.form.get('plan')
        token = request.form.get('stripeToken')
        api_key = request.form.get('api_key')
        
        try:
            if plan_type == 'monthly':
                amount = 3000  # $30.00
                # Create Stripe subscription
                customer = stripe.Customer.create(
                    email=user.email,
                    source=token
                )
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{'price': 'price_monthly_plan_id'}]  # Replace with actual price ID
                )
                
                # Create local subscription record
                sub = Subscription(
                    user_id=user.id,
                    plan_type='monthly',
                    status='active',
                    amount_paid=30.00,
                    end_date=datetime.utcnow() + timedelta(days=30)
                )
            else:  # lifetime
                amount = 10000  # $100.00
                # Process one-time payment
                stripe.Charge.create(
                    amount=amount,
                    currency='usd',
                    description='Lifetime Subscription',
                    source=token
                )
                
                # Create local subscription record
                sub = Subscription(
                    user_id=user.id,
                    plan_type='lifetime',
                    status='active',
                    amount_paid=100.00,
                    api_key=api_key
                )
            
            db.add(sub)
            db.commit()
            return redirect(url_for('index'))
            
        except stripe.error.StripeError as e:
            flash('Payment failed: ' + str(e))
    
    return render_template('auth/subscription.html', 
                         user=user,
                         stripe_public_key=os.getenv('STRIPE_PUBLIC_KEY'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    db = DbSession()
    user = db.query(User).get(session['user_id'])
    
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        if user.subscription and user.subscription.plan_type == 'lifetime':
            user.subscription.api_key = api_key
            db.commit()
            flash('API key updated successfully')
    
    return render_template('auth/settings.html', user=user)
