# app.py - FINAL WITH 5m & 15m DISPLAY
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from webhook_handler import app
import schedule
import time
import threading
from datetime import datetime
from data_fetcher import DataFetcher
from signal_engine import SignalEngine
from webhook_handler import WebhookHandler

def generate_signal_update():
    print(f"⏰ Signal update at {datetime.now()}")
    try:
        fetcher = DataFetcher()
        data = fetcher.fetch_all_data()
        if data.get('status') == 'error':
            print("⚠️ Data fetch failed")
            return
        
        engine = SignalEngine()
        signal = engine.analyze(data)
        
        handler = WebhookHandler()
        handler.send_signal_alert(data, signal)
        
        # Display with 5m & 15m info
        ind = signal.indicators
        print(f"📊 {signal.signal_type} ({signal.strength}/10)")
        print(f"   RSI: 1m={ind.get('rsi_1m', 50):.1f} | 5m={ind.get('rsi_5m', 50):.1f} | 15m={ind.get('rsi_15m', 50):.1f}")
        print(f"   MACD: {ind.get('macd_signal', 'N/A')}")
        print(f"   CVD: {ind.get('cvd_signal', 'N/A')}")
        print(f"   RR: {signal.risk_reward:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def start_scheduler():
    print("🚀 Scheduler started")
    schedule.every(5).minutes.do(generate_signal_update)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=start_scheduler, daemon=True).start()
    
    print("=" * 60)
    print("🚀 INSTITUTIONAL GRADE SIGNAL ENGINE v4.0")
    print("=" * 60)
    print("📡 Dashboard: http://localhost:5000")
    print("📊 Data API: http://localhost:5000/data/latest")
    print("📈 Signal API: http://localhost:5000/signal")
    print("✅ TIMEFRAMES: 1m | 5m | 15m | 1h | 4h")
    print("✅ RSI: Multi-Timeframe Confirmation")
    print("✅ MACD: Multi-Timeframe Confirmation")
    print("✅ CVD: Added")
    print("✅ Dynamic Funding: Z-Score based")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
