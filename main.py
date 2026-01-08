#!/usr/bin/env python3
"""
Portfolio Reporter - Automated Portfolio Analysis and Email Reporting
Using Official Kite Connect Library
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import logging
from kiteconnect import KiteConnect

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortfolioReporter:
    def __init__(self):
        self.api_key = os.getenv('KITE_API_KEY')
        self.api_secret = os.getenv('KITE_API_SECRET')
        self.access_token = os.getenv('KITE_ACCESS_TOKEN')
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        # Initialize Kite Connect
        self.kite = KiteConnect(api_key=self.api_key)
        if self.access_token:
            self.kite.set_access_token(self.access_token)
        
        # Set style for plots
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def get_portfolio_holdings(self):
        """Fetch current portfolio holdings using Kite Connect"""
        try:
            holdings = self.kite.holdings()
            logger.info(f"Successfully fetched {len(holdings)} holdings")
            return holdings
            
        except Exception as e:
            logger.error(f"Error fetching portfolio holdings: {e}")
            return []
    
    def get_historical_data(self, instrument_token, days=30):
        """Fetch historical data for a given instrument"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            historical_data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=start_date.date(),
                to_date=end_date.date(),
                interval='day'
            )
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return []
    
    def analyze_portfolio(self, holdings):
        """Analyze portfolio performance and generate insights"""
        if not holdings:
            return None
        
        analysis = {
            'total_value': 0,
            'total_pnl': 0,
            'sectors': {},
            'top_gainers': [],
            'top_losers': [],
            'holdings_count': len(holdings)
        }
        
        for holding in holdings:
            quantity = holding.get('quantity', 0)
            avg_price = holding.get('average_price', 0)
            ltp = holding.get('last_price', 0)
            
            current_value = quantity * ltp
            invested_value = quantity * avg_price
            pnl = current_value - invested_value
            pnl_percentage = (pnl / invested_value * 100) if invested_value > 0 else 0
            
            analysis['total_value'] += current_value
            analysis['total_pnl'] += pnl
            
            # Sector analysis
            sector = holding.get('sector', 'Unknown')
            if sector not in analysis['sectors']:
                analysis['sectors'][sector] = {'value': 0, 'pnl': 0, 'count': 0}
            
            analysis['sectors'][sector]['value'] += current_value
            analysis['sectors'][sector]['pnl'] += pnl
            analysis['sectors'][sector]['count'] += 1
            
            # Track top gainers and losers
            holding_info = {
                'symbol': holding.get('tradingsymbol', 'Unknown'),
                'pnl': pnl,
                'pnl_percentage': pnl_percentage,
                'current_value': current_value
            }
            
            if pnl > 0:
                analysis['top_gainers'].append(holding_info)
            else:
                analysis['top_losers'].append(holding_info)
        
        # Sort top gainers and losers
        analysis['top_gainers'].sort(key=lambda x: x['pnl'], reverse=True)
        analysis['top_losers'].sort(key=lambda x: x['pnl'])
        
        # Calculate overall PnL percentage
        total_invested = analysis['total_value'] - analysis['total_pnl']
        analysis['total_pnl_percentage'] = (analysis['total_pnl'] / total_invested * 100) if total_invested > 0 else 0
        
        return analysis
    
    def create_portfolio_charts(self, analysis):
        """Create visualizations for portfolio analysis"""
        if not analysis:
            return None
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Portfolio Analysis Report', fontsize=16, fontweight='bold')
        
        # 1. Sector Allocation Pie Chart
        sectors = list(analysis['sectors'].keys())
        sector_values = [analysis['sectors'][s]['value'] for s in sectors]
        
        if sector_values:
            ax1.pie(sector_values, labels=sectors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Sector Allocation')
        
        # 2. Top 5 Gainers Bar Chart
        top_gainers = analysis['top_gainers'][:5]
        if top_gainers:
            gainer_symbols = [h['symbol'] for h in top_gainers]
            gainer_pnls = [h['pnl'] for h in top_gainers]
            
            bars = ax2.bar(gainer_symbols, gainer_pnls, color='green', alpha=0.7)
            ax2.set_title('Top 5 Gainers')
            ax2.set_ylabel('P&L (₹)')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, pnl in zip(bars, gainer_pnls):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'₹{pnl:,.0f}', ha='center', va='bottom')
        
        # 3. Top 5 Losers Bar Chart
        top_losers = analysis['top_losers'][:5]
        if top_losers:
            loser_symbols = [h['symbol'] for h in top_losers]
            loser_pnls = [abs(h['pnl']) for h in top_losers]
            
            bars = ax3.bar(loser_symbols, loser_pnls, color='red', alpha=0.7)
            ax3.set_title('Top 5 Losers')
            ax3.set_ylabel('Loss (₹)')
            ax3.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, pnl in zip(bars, loser_pnls):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'₹{pnl:,.0f}', ha='center', va='bottom')
        
        # 4. Overall Portfolio Summary
        summary_text = f"""
        Portfolio Summary
        
        Total Value: ₹{analysis['total_value']:,.2f}
        Total P&L: ₹{analysis['total_pnl']:,.2f}
        P&L %: {analysis['total_pnl_percentage']:.2f}%
        Holdings: {analysis['holdings_count']}
        Sectors: {len(analysis['sectors'])}
        """
        
        ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes, fontsize=12,
                verticalalignment='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        ax4.set_title('Portfolio Summary')
        ax4.axis('off')
        
        plt.tight_layout()
        
        # Save the chart
        chart_path = 'portfolio_analysis.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def generate_email_content(self, analysis):
        """Generate HTML email content with portfolio analysis"""
        if not analysis:
            return "Unable to generate portfolio analysis."
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 10px; }}
                .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .section {{ margin: 20px 0; }}
                .positive {{ color: green; font-weight: bold; }}
                .negative {{ color: red; font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Portfolio Analysis Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>Portfolio Summary</h2>
                <p><strong>Total Portfolio Value:</strong> ₹{analysis['total_value']:,.2f}</p>
                <p><strong>Total P&L:</strong> 
                    <span class="{'positive' if analysis['total_pnl'] >= 0 else 'negative'}">
                        ₹{analysis['total_pnl']:,.2f} ({analysis['total_pnl_percentage']:+.2f}%)
                    </span>
                </p>
                <p><strong>Number of Holdings:</strong> {analysis['holdings_count']}</p>
                <p><strong>Sectors Covered:</strong> {len(analysis['sectors'])}</p>
            </div>
            
            <div class="section">
                <h2>🏆 Top Gainers</h2>
                <table>
                    <tr><th>Symbol</th><th>P&L</th><th>P&L %</th><th>Current Value</th></tr>
        """
        
        for gainer in analysis['top_gainers'][:5]:
            html_content += f"""
                    <tr>
                        <td>{gainer['symbol']}</td>
                        <td class="positive">₹{gainer['pnl']:,.2f}</td>
                        <td class="positive">+{gainer['pnl_percentage']:.2f}%</td>
                        <td>₹{gainer['current_value']:,.2f}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>📉 Top Losers</h2>
                <table>
                    <tr><th>Symbol</th><th>P&L</th><th>P&L %</th><th>Current Value</th></tr>
        """
        
        for loser in analysis['top_losers'][:5]:
            html_content += f"""
                    <tr>
                        <td>{loser['symbol']}</td>
                        <td class="negative">₹{loser['pnl']:,.2f}</td>
                        <td class="negative">{loser['pnl_percentage']:.2f}%</td>
                        <td>₹{loser['current_value']:,.2f}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>🏭 Sector Analysis</h2>
                <table>
                    <tr><th>Sector</th><th>Value</th><th>P&L</th><th>Holdings</th></tr>
        """
        
        for sector, data in analysis['sectors'].items():
            pnl_class = 'positive' if data['pnl'] >= 0 else 'negative'
            html_content += f"""
                    <tr>
                        <td>{sector}</td>
                        <td>₹{data['value']:,.2f}</td>
                        <td class="{pnl_class}">₹{data['pnl']:,.2f}</td>
                        <td>{data['count']}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <p><em>This report was generated automatically by Portfolio Reporter using Kite Connect.</em></p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_email_report(self, html_content, chart_path=None):
        """Send portfolio report via email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Portfolio Analysis Report - {datetime.now().strftime("%Y-%m-%d")}'
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Attach chart if available
            if chart_path and os.path.exists(chart_path):
                with open(chart_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', '<portfolio_chart>')
                    img.add_header('Content-Disposition', 'inline', filename='portfolio_analysis.png')
                    msg.attach(img)
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email report sent successfully to {self.recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def run_report(self):
        """Main method to run the complete portfolio report"""
        logger.info("Starting portfolio analysis using Kite Connect...")
        
        # Fetch portfolio holdings
        holdings = self.get_portfolio_holdings()
        if not holdings:
            logger.error("No portfolio holdings found or error fetching data")
            return False
        
        # Analyze portfolio
        analysis = self.analyze_portfolio(holdings)
        if not analysis:
            logger.error("Error analyzing portfolio data")
            return False
        
        # Create charts
        chart_path = self.create_portfolio_charts(analysis)
        
        # Generate email content
        html_content = self.generate_email_content(analysis)
        
        # Send email report
        success = self.send_email_report(html_content, chart_path)
        
        # Clean up chart file
        if chart_path and os.path.exists(chart_path):
            os.remove(chart_path)
        
        if success:
            logger.info("Portfolio report completed successfully!")
        else:
            logger.error("Failed to send portfolio report")
        
        return success

def main():
    """Main function to run the portfolio reporter"""
    try:
        reporter = PortfolioReporter()
        success = reporter.run_report()
        
        if success:
            print("✅ Portfolio report generated and sent successfully!")
        else:
            print("❌ Failed to generate portfolio report. Check logs for details.")
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
