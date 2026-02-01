from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorator to check if user is logged in before accessing a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this feature.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function 