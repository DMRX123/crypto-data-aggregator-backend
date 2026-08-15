# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Binance API (Futures Enabled)
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8526613698:AAG1g7Hc-ZiukV20e6XHW6LPEG1vAor_a_4')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '5223741844')
    
    # Webhook
    TRADINGVIEW_WEBHOOK = os.getenv('TRADINGVIEW_WEBHOOK', 'https://crypto-data-api.onrender.com/webhook')
    
    # Cache TTL
    CACHE_TTL = 5
    
    # Futures Base URL
    FUTURES_BASE_URL = "https://fapi.binance.com"