"""
Authentication Blueprint for Gruha Alankara.
Handles user registration, login, and logout with session management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration Route.
    GET: Display registration form.
    POST: Validate input, create user, redirect to login.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # ---- Input Validation ----
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check for duplicate username or email
        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')
        
        if User.query.filter_by(username=username).first():
            errors.append('This username is already taken.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', username=username, email=email)
        
        # ---- Create new user ----
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User Login Route.
    GET: Display login form.
    POST: Authenticate user, create session, redirect to dashboard.
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Set session data
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('designs.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('login.html', email=email)
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """
    User Logout Route.
    Clears session data and redirects to the homepage.
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))
