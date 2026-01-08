#!/usr/bin/env python3
"""
Generate Kite Access Token using Kite Connect Library
"""

from kiteconnect import KiteConnect
import webbrowser
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_access_token():
    # Get API credentials from .env
    api_key = os.getenv('KITE_API_KEY')
    api_secret = os.getenv('KITE_API_SECRET')
    
    if api_key == 'your_actual_api_key' or api_secret == 'your_actual_api_secret':
        print("❌ Please update your API credentials in .env file first!")
        print("Update these values:")
        print("KITE_API_KEY=your_real_api_key")
        print("KITE_API_SECRET=your_real_api_secret")
        return
    
    # Initialize Kite Connect
    kite = KiteConnect(api_key=api_key)
    
    # Generate login URL
    login_url = kite.login_url()
    print(f"🔗 Login URL: {login_url}")
    
    # Open browser for login
    print("🌐 Opening browser for login...")
    webbrowser.open(login_url)
    
    # Get request token from user
    print("\n📝 After logging in, you'll be redirected to a URL.")
    print("Copy the 'request_token' parameter from that URL.")
    request_token = input("Enter the request token: ").strip()
    
    try:
        # Generate session
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        
        print(f"\n✅ Access Token Generated Successfully!")
        print(f"🔑 Access Token: {access_token}")
        
        # Update .env file
        with open('.env', 'r') as f:
            env_content = f.read()
        
        env_content = env_content.replace('KITE_ACCESS_TOKEN=your_actual_access_token', f'KITE_ACCESS_TOKEN={access_token}')
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Access token saved to .env file!")
        print("\n🎉 You can now run: python main.py")
        
    except Exception as e:
        print(f"❌ Error generating access token: {e}")

if __name__ == "__main__":
    generate_access_token()
