"""Authentication routes - OAuth flow with Kite"""
from flask import Blueprint, redirect, url_for, session, flash, current_app, render_template, request
from kiteconnect import KiteConnect
from app.services.token_manager import save_token, clear_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    """Show login page"""
    # If already logged in, redirect to dashboard
    if 'access_token' in session:
        return redirect(url_for('dashboard.index'))

    # Generate Kite login URL
    kite = KiteConnect(api_key=current_app.config['KITE_API_KEY'])
    login_url = kite.login_url()

    return render_template('login.html', login_url=login_url)


@auth_bp.route('/callback')
def callback():
    """OAuth callback - receives request_token from Kite"""
    request_token = request.args.get('request_token')

    if not request_token:
        flash('Authentication failed: No request token received', 'error')
        return redirect(url_for('auth.login'))

    try:
        kite = KiteConnect(api_key=current_app.config['KITE_API_KEY'])
        data = kite.generate_session(
            request_token,
            api_secret=current_app.config['KITE_API_SECRET']
        )

        access_token = data['access_token']
        user_id = data.get('user_id', 'unknown')

        # Store in session
        session['access_token'] = access_token
        session['user_id'] = user_id

        # Store in file for persistence
        save_token(access_token, user_id)

        flash('Successfully connected to Kite!', 'success')
        return redirect(url_for('dashboard.index'))

    except Exception as e:
        flash(f'Authentication failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    """Clear session and stored token"""
    session.clear()
    clear_token()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
