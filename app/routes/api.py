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
        # Check email config first
        resend_api_key = current_app.config.get('RESEND_API_KEY')
        recipient_email = current_app.config.get('RECIPIENT_EMAIL')

        if not resend_api_key or not recipient_email:
            return jsonify({
                'status': 'error',
                'message': 'Email not configured. Add RESEND_API_KEY and RECIPIENT_EMAIL in Railway variables.'
            }), 500

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

        success = send_report(analysis, None, resend_api_key, recipient_email)

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

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
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
