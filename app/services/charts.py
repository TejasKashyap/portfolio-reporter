"""Chart generation service - creates charts as base64 images"""
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for web
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def create_sector_chart(analysis):
    """Create sector allocation pie chart"""
    if not analysis or not analysis.get('sectors'):
        return None

    sectors = list(analysis['sectors'].keys())
    sector_values = [analysis['sectors'][s]['value'] for s in sectors]

    if not sector_values or sum(sector_values) == 0:
        return None

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sector_values, labels=sectors, autopct='%1.1f%%', startangle=90)
    ax.set_title('Sector Allocation')

    result = fig_to_base64(fig)
    plt.close(fig)
    return result


def create_gainers_chart(analysis):
    """Create top gainers bar chart"""
    if not analysis:
        return None

    top_gainers = analysis.get('top_gainers', [])[:5]
    if not top_gainers:
        return None

    fig, ax = plt.subplots(figsize=(8, 6))

    symbols = [h['symbol'] for h in top_gainers]
    pnls = [h['pnl'] for h in top_gainers]

    bars = ax.bar(symbols, pnls, color='green', alpha=0.7)
    ax.set_title('Top 5 Gainers')
    ax.set_ylabel('P&L')
    ax.tick_params(axis='x', rotation=45)

    # Add value labels on bars
    for bar, pnl in zip(bars, pnls):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{pnl:,.0f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    result = fig_to_base64(fig)
    plt.close(fig)
    return result


def create_losers_chart(analysis):
    """Create top losers bar chart"""
    if not analysis:
        return None

    top_losers = analysis.get('top_losers', [])[:5]
    if not top_losers:
        return None

    fig, ax = plt.subplots(figsize=(8, 6))

    symbols = [h['symbol'] for h in top_losers]
    pnls = [abs(h['pnl']) for h in top_losers]

    bars = ax.bar(symbols, pnls, color='red', alpha=0.7)
    ax.set_title('Top 5 Losers')
    ax.set_ylabel('Loss')
    ax.tick_params(axis='x', rotation=45)

    # Add value labels on bars
    for bar, pnl in zip(bars, pnls):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{pnl:,.0f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    result = fig_to_base64(fig)
    plt.close(fig)
    return result


def create_all_charts(analysis):
    """Create all charts and return as dict of base64 strings"""
    return {
        'sector_pie': create_sector_chart(analysis),
        'gainers': create_gainers_chart(analysis),
        'losers': create_losers_chart(analysis)
    }
