"""Flask application factory"""
from flask import Flask
from dotenv import load_dotenv
import os


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-change-in-production')
    app.config['KITE_API_KEY'] = os.getenv('KITE_API_KEY')
    app.config['KITE_API_SECRET'] = os.getenv('KITE_API_SECRET')
    app.config['SENDER_EMAIL'] = os.getenv('SENDER_EMAIL')
    app.config['EMAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
    app.config['RECIPIENT_EMAIL'] = os.getenv('RECIPIENT_EMAIL')

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
