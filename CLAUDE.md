# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Portfolio Reporter is a Python application that fetches portfolio holdings from Zerodha's Kite API, analyzes performance (P&L, sector allocation, top gainers/losers), generates visualization charts, and sends HTML email reports.

## Commands

```bash
# Install dependencies (use virtual environment)
pip install -r requirements.txt

# Run the main portfolio report
python main.py

# Generate Kite access token (interactive - opens browser)
python generate_token.py
```

## Architecture

The application is built around a single `PortfolioReporter` class in `main.py` with this flow:

1. **Data Fetching** - `get_portfolio_holdings()` uses KiteConnect to fetch holdings
2. **Analysis** - `analyze_portfolio()` calculates P&L, groups by sector, identifies top gainers/losers
3. **Visualization** - `create_portfolio_charts()` generates a 2x2 matplotlib figure (sector pie, gainers bar, losers bar, summary)
4. **Email** - `generate_email_content()` creates HTML report, `send_email_report()` sends via Gmail SMTP

Helper script `generate_token.py` handles the OAuth flow to obtain Kite access tokens.

## Configuration

All credentials are in `.env` (not committed):
- `KITE_API_KEY`, `KITE_API_SECRET`, `KITE_ACCESS_TOKEN` - Kite Connect API credentials
- `SENDER_EMAIL`, `EMAIL_PASSWORD`, `RECIPIENT_EMAIL` - Gmail credentials (requires app password)

## Dependencies

Key libraries: `kiteconnect` (Kite API), `pandas` (data), `matplotlib`/`seaborn` (charts), `python-dotenv` (env vars)
