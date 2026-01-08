# Portfolio Reporter

An automated Python application that fetches portfolio data from Kite API using the official Kite Connect library, analyzes performance, and sends detailed email reports with visualizations.

## Features

- 📊 **Portfolio Analysis**: Fetches current holdings and calculates P&L using Kite Connect
- 📈 **Visual Reports**: Generates charts showing sector allocation, top gainers/losers
- 📧 **Email Reports**: Sends comprehensive HTML reports via email
- 🔄 **Automated**: Can be scheduled to run daily/weekly
- 🔐 **Secure**: Uses official Kite Connect library for reliable API access

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Edit the `.env` file with your credentials:
   ```
   KITE_API_KEY=your_actual_api_key
   KITE_API_SECRET=your_actual_api_secret
   KITE_ACCESS_TOKEN=your_actual_access_token
   SENDER_EMAIL=your_email@gmail.com
   EMAIL_PASSWORD=your_gmail_app_password
   RECIPIENT_EMAIL=your_email@gmail.com
   ```

3. **Get Kite API Credentials**:
   - Login to [kite.trade](https://kite.trade)
   - Go to API section and generate API key
   - Set appropriate permissions (Portfolio, Market Data)
   - Generate access token using the API

4. **Gmail App Password**:
   - Enable 2-factor authentication on your Gmail account
   - Generate an app password for this application
   - Use the app password in EMAIL_PASSWORD

## Usage

Run the application:
```bash
python main.py
```

## Output

The application will:
1. Fetch your current portfolio holdings from Kite using Kite Connect
2. Analyze performance and generate insights
3. Create visual charts (sector allocation, top gainers/losers)
4. Send an HTML email report with analysis and charts

## Requirements

- Python 3.7+
- Kite trading account with API access
- Gmail account with app password
- Internet connection for API calls

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys and passwords secure
- Use app passwords instead of your main Gmail password
- The `.env` file is already in `.gitignore` to protect your credentials

## Dependencies

- `kiteconnect` - Official Kite Connect library
- `requests` - HTTP library
- `python-dotenv` - Environment variable management
- `pandas` - Data manipulation
- `matplotlib` & `seaborn` - Data visualization
- `email-validator` - Email validation
