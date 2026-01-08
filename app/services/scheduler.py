"""Scheduler service - handles scheduled email reports"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.portfolio import PortfolioService
from app.services.email import send_report
from app.services.token_manager import load_token

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def send_scheduled_report(app):
    """Send scheduled portfolio report"""
    with app.app_context():
        try:
            logger.info("Running scheduled portfolio report...")

            # Load token from file
            token_data = load_token()
            if not token_data:
                logger.error("No valid token found for scheduled report")
                return

            access_token = token_data['access_token']
            api_key = app.config.get('KITE_API_KEY')
            resend_api_key = app.config.get('RESEND_API_KEY')
            recipient_email = app.config.get('RECIPIENT_EMAIL')

            if not all([api_key, resend_api_key, recipient_email]):
                logger.error("Missing configuration for scheduled report")
                return

            # Fetch and analyze portfolio
            portfolio_service = PortfolioService(api_key, access_token)
            holdings = portfolio_service.get_holdings()

            if not holdings:
                logger.warning("No holdings found for scheduled report")
                return

            analysis = portfolio_service.analyze(holdings)

            # Send report
            success = send_report(analysis, None, resend_api_key, recipient_email)

            if success:
                logger.info("Scheduled report sent successfully!")
            else:
                logger.error("Failed to send scheduled report")

        except Exception as e:
            logger.error(f"Error in scheduled report: {e}")


def init_scheduler(app):
    """Initialize the scheduler with daily report job"""
    # Get schedule time from config (default: 9:00 AM IST)
    schedule_hour = int(app.config.get('REPORT_HOUR', 9))
    schedule_minute = int(app.config.get('REPORT_MINUTE', 0))

    # Add job - runs daily at specified time
    scheduler.add_job(
        func=send_scheduled_report,
        args=[app],
        trigger=CronTrigger(hour=schedule_hour, minute=schedule_minute),
        id='daily_report',
        name='Daily Portfolio Report',
        replace_existing=True
    )

    # Start scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info(f"Scheduler started - Daily report at {schedule_hour:02d}:{schedule_minute:02d}")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")
