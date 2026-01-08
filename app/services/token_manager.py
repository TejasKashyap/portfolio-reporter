"""Token manager - handles token storage and validation"""
import json
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for

TOKEN_FILE = 'token_store.json'


def save_token(access_token, user_id):
    """Save token to file for persistence"""
    # Kite tokens expire at 6 AM IST next day
    now = datetime.now()
    expires_at = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now.hour >= 6:
        expires_at += timedelta(days=1)

    data = {
        'access_token': access_token,
        'user_id': user_id,
        'created_at': now.isoformat(),
        'expires_at': expires_at.isoformat()
    }

    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_token():
    """Load token from file if valid"""
    if not os.path.exists(TOKEN_FILE):
        return None

    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)

        expires_at = datetime.fromisoformat(data['expires_at'])
        if datetime.now() > expires_at:
            clear_token()
            return None

        return data
    except Exception:
        return None


def clear_token():
    """Remove stored token"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            # Try loading from file
            token_data = load_token()
            if token_data:
                session['access_token'] = token_data['access_token']
                session['user_id'] = token_data['user_id']
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
