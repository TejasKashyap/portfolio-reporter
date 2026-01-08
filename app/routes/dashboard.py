"""Dashboard routes - main portfolio view"""
from flask import Blueprint, render_template, session, current_app, flash
from app.services.portfolio import PortfolioService
from app.services.charts import create_all_charts
from app.services.token_manager import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard - shows portfolio analysis"""
    access_token = session.get('access_token')
    api_key = current_app.config['KITE_API_KEY']

    try:
        portfolio_service = PortfolioService(api_key, access_token)
        holdings = portfolio_service.get_holdings()

        if not holdings:
            flash('No holdings found or error fetching data. You may need to re-authenticate.', 'warning')
            analysis = None
            charts = {}
        else:
            analysis = portfolio_service.analyze(holdings)
            charts = create_all_charts(analysis)

    except Exception as e:
        flash(f'Error loading portfolio: {str(e)}', 'error')
        analysis = None
        charts = {}

    return render_template('dashboard.html',
                          analysis=analysis,
                          charts=charts,
                          user_id=session.get('user_id'))
