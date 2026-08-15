# config.py - UPDATED WITH TIMEFRAMES
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ===== BINANCE FUTURES API =====
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    
    # ===== BINANCE ENDPOINTS =====
    FUTURES_BASE_URL = "https://fapi.binance.com"
    FUTURES_WS_URL = "wss://fstream.binance.com/ws"
    SPOT_BASE_URL = "https://api.binance.com"
    
    # ===== TELEGRAM =====
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8526613698:AAG1g7Hc-ZiukV20e6XHW6LPEG1vAor_a_4')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '5223741844')
    
    # ===== WEBHOOK =====
    TRADINGVIEW_WEBHOOK = os.getenv('TRADINGVIEW_WEBHOOK', '')
    
    # ===== CACHE =====
    CACHE_TTL = 2
    
    # ===== TIMEFRAMES FOR ANALYSIS =====
    TIMEFRAMES = {
        '1m': {'limit': 100, 'weight': 1},
        '5m': {'limit': 100, 'weight': 2},
        '15m': {'limit': 80, 'weight': 3},
        '1h': {'limit': 50, 'weight': 4},
    }
    
    # ===== SIGNAL CONFIG =====
    SIGNAL_CONFIG = {
        'rsi_period': 14,
        'rsi_ob': 70,
        'rsi_os': 30,
        'atr_period': 14,
        'funding_lookback': 30,
        'volume_lookback': 30,
        'min_klines_rsi': 50,
        'min_klines_atr': 30,
    }
    
    # ===== RISK MANAGEMENT =====
    RISK = {
        'max_position_size': 0.02,
        'max_risk_per_trade': 0.01,
        'atr_multiplier_sl': 2.0,
        'atr_multiplier_tp': 3.0,
        'min_risk_reward': 1.5,
    }