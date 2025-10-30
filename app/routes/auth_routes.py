from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db, logger
from app.models import User
from functools import wraps

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning('Unauthorized access attempt to protected route')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            logger.warning(f'Unauthorized access attempt by {current_user.username if current_user.is_authenticated else "anonymous"} to admin route')
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logger.info(f'User {current_user.username} already logged in, redirecting to quiz list')
        return redirect(url_for('quiz.list_quizzes'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            logger.info(f'User {username} logged in successfully')
            next_page = request.args.get('next') or url_for('quiz.list_quizzes')
            return redirect(next_page)
        else:
            logger.warning(f'Failed login attempt for username: {username}')
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logger.info(f'User {current_user.username} logged out')
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))