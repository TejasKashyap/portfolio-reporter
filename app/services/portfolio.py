"""Portfolio service - fetches and analyzes portfolio data"""
import logging
from kiteconnect import KiteConnect

logger = logging.getLogger(__name__)


class PortfolioService:
    def __init__(self, api_key, access_token):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def get_holdings(self):
        """Fetch current portfolio holdings from Kite"""
        try:
            holdings = self.kite.holdings()
            logger.info(f"Successfully fetched {len(holdings)} holdings")
            return holdings
        except Exception as e:
            logger.error(f"Error fetching portfolio holdings: {e}")
            return []

    def analyze(self, holdings):
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
        analysis['total_pnl_percentage'] = (
            (analysis['total_pnl'] / total_invested * 100) if total_invested > 0 else 0
        )

        return analysis
