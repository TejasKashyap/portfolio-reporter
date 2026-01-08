# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Portfolio Reporter is a Python application that fetches portfolio holdings from Zerodha's Kite API, analyzes performance (P&L, sector allocation, top gainers/losers), generates visualization charts, and sends HTML email reports. Available as both CLI and Flask web app.

## Commands

```bash
# Install dependencies (use virtual environment)
pip install -r requirements.txt

# Run Flask web app (development)
python run.py

# Run Flask web app (production)
gunicorn wsgi:app

# Run CLI version (for cron jobs)
python main.py

# Generate Kite access token (CLI - interactive)
python generate_token.py
```

## Architecture

### Web App (Flask)
```
app/
├── __init__.py          # Flask app factory
├── config.py            # Configuration
├── routes/
│   ├── auth.py          # OAuth: /auth/login, /auth/callback, /auth/logout
│   ├── dashboard.py     # Main view: /
│   └── api.py           # API: /api/send-email, /api/portfolio
├── services/
│   ├── portfolio.py     # PortfolioService - fetch & analyze holdings
│   ├── charts.py        # Chart generation (base64 output)
│   ├── email.py         # Email sending
│   └── token_manager.py # Token storage & login_required decorator
└── templates/           # Jinja2 templates (Bootstrap 5)
```

### OAuth Flow
1. User visits `/` → redirected to `/auth/login`
2. Click "Connect to Kite" → redirect to Kite login
3. Kite redirects to `/auth/callback?request_token=xxx`
4. Flask exchanges token, stores in session + `token_store.json`

### CLI Version
`main.py` contains standalone `PortfolioReporter` class for cron-based scheduled reports.

## Configuration

`.env` file (not committed):
```
KITE_API_KEY=xxx
KITE_API_SECRET=xxx
KITE_ACCESS_TOKEN=xxx        # Only needed for CLI
SENDER_EMAIL=xxx
EMAIL_PASSWORD=xxx           # Gmail app password
RECIPIENT_EMAIL=xxx
FLASK_SECRET_KEY=xxx         # For web app sessions
```

## Key Files

- `run.py` - Development server entry point
- `wsgi.py` - Production entry point (gunicorn)
- `main.py` - CLI version (standalone)
- `token_store.json` - Persisted access token (auto-generated)

## Dependencies

Core: `Flask`, `kiteconnect`, `pandas`, `matplotlib`, `seaborn`, `gunicorn`
