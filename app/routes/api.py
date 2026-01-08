"""API routes - email and data refresh endpoints"""
from flask import Blueprint, jsonify, session, current_app
from app.services.portfolio import PortfolioService
from app.services.email import send_report
from app.services.token_manager import login_required

api_bp = Blueprint('api', __name__)


@api_bp.route('/send-email', methods=['POST'])
@login_required
def send_email():
    """Send portfolio report via email"""
    try:
        access_token = session.get('access_token')
        api_key = current_app.config['KITE_API_KEY']

        portfolio_service = PortfolioService(api_key, access_token)
        holdings = portfolio_service.get_holdings()

        if not holdings:
            return jsonify({
                'status': 'error',
                'message': 'No holdings found'
            }), 400

        analysis = portfolio_service.analyze(holdings)

        success = send_report(
            analysis,
            current_app.config['SENDER_EMAIL'],
            current_app.config['EMAIL_PASSWORD'],
            current_app.config['RECIPIENT_EMAIL']
        )

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Email sent successfully!'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send email'
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@api_bp.route('/portfolio', methods=['GET'])
@login_required
def get_portfolio():
    """Get portfolio data as JSON"""
    try:
        access_token = session.get('access_token')
        api_key = current_app.config['KITE_API_KEY']

        portfolio_service = PortfolioService(api_key, access_token)
        holdings = portfolio_service.get_holdings()
        analysis = portfolio_service.analyze(holdings)

        return jsonify({
            'status': 'success',
            'data': analysis
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
