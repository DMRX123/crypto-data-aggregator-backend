from binance.client import Client
import os

API_KEY = "VItC70BDJ0ov2nttu4Uk6WklixtXu7jeBrgdiHWzW5YAMhMfzKBLboHhL5CIW5vC"
API_SECRET = "kX1lupPncWhCkzqHvA5bpnmwwtu1sW2B4pduS79HgC5HSdHscYHHfgTojWgK710W"

client = Client(API_KEY, API_SECRET)

try:
    # Test account info
    account = client.get_account()
    print("✅ API Key WORKING!")
    print(f"✅ Account ID: {account.get('uid', 'N/A')}")
    
    # Test price
    price = client.get_symbol_ticker(symbol="BTCUSDT")
    print(f"✅ BTC Price: ${price['price']}")
    
except Exception as e:
    print(f"❌ Error: {e}")