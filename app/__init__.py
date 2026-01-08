"""Flask application factory"""
from flask import Flask
from dotenv import load_dotenv
import os


def create_app():
    # Only load .env file if it exists (local development)
    # Don't override existing env vars (Railway sets these directly)
    load_dotenv(override=False)

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-in-production')
    app.config['KITE_API_KEY'] = os.environ.get('KITE_API_KEY')
    app.config['KITE_API_SECRET'] = os.environ.get('KITE_API_SECRET')
    app.config['RESEND_API_KEY'] = os.environ.get('RESEND_API_KEY')
    app.config['RECIPIENT_EMAIL'] = os.environ.get('RECIPIENT_EMAIL')

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
