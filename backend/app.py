# app.py
from webhook_handler import app
import schedule
import time
import threading
from datetime import datetime
from data_fetcher import DataFetcher
from webhook_handler import WebhookHandler

def safe_format(value, format_str="{}"):
    if value is None:
        return "N/A"
    try:
        return format_str.format(value)
    except:
        return str(value)

def scheduled_data_push():
    print(f"⏰ Scheduled run at {datetime.now()}")
    
    fetcher = DataFetcher()
    data = fetcher.fetch_all_data()
    
    handler = WebhookHandler()
    handler.send_to_tradingview(data)
    
    btc = data.get('btc_price')
    btc_str = safe_format(btc, "${:,.2f}") if btc else "N/A"
    
    funding = data.get('funding_rate', {})
    funding_str = safe_format(funding.get('rate') if funding else None)
    
    oi = data.get('open_interest', {})
    oi_value = oi.get('value') if oi else None
    oi_str = safe_format(oi_value, "{:,.0f}") if oi_value else "N/A"
    
    fng = data.get('fear_greed', {})
    fng_str = safe_format(fng.get('value') if fng else None)
    
    high = data.get('high_24h')
    low = data.get('low_24h')
    high_str = safe_format(high, "${:,.2f}") if high else "N/A"
    low_str = safe_format(low, "${:,.2f}") if low else "N/A"
    
    message = f"""
🔄 <b>Scheduled Update</b>
📊 BTC: {btc_str}
📈 Funding: {funding_str}
💰 OI: {oi_str}
😱 F&G: {fng_str}
📈 24h High: {high_str}
📉 24h Low: {low_str}
⏰ {datetime.now().strftime('%H:%M:%S')}
    """
    handler.send_telegram_alert(message)

def start_scheduler():
    print("🚀 Scheduler started - Data push every 5 minutes")
    schedule.every(5).minutes.do(scheduled_data_push)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("=" * 50)
    print("🚀 CRYPTO DATA AGGREGATOR - REAL FUTURES DATA")
    print("=" * 50)
    print("📡 Flask API: http://localhost:5000")
    print("📊 Data: http://localhost:5000/data/latest")
    print("⏰ Scheduler: Every 5 minutes")
    print("✅ Funding Rate: REAL")
    print("✅ Open Interest: REAL")
    print("✅ Price: REAL")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)