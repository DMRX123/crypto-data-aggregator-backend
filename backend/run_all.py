# run_all.py - Updated Version
import schedule
import time
from datetime import datetime
from data_fetcher import DataFetcher
import requests
from config import Config

def send_telegram_alert(message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': Config.TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def send_to_tradingview(data):
    """Send data to TradingView webhook"""
    try:
        if Config.TRADINGVIEW_WEBHOOK:
            response = requests.post(
                Config.TRADINGVIEW_WEBHOOK,
                json=data,
                timeout=5
            )
            return response.status_code == 200
        return False
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False

def scheduled_data_push():
    """Run every 5 minutes"""
    print(f"⏰ Scheduled run at {datetime.now()}")
    
    fetcher = DataFetcher()
    data = fetcher.fetch_all_data()
    
    # Send to TradingView
    if send_to_tradingview(data):
        print("✅ Data sent to TradingView")
    
    # Send Telegram summary
    message = f"""
🔄 <b>Scheduled Update</b>
📊 BTC: ${data.get('btc_price', 'N/A'):,.2f}
📈 Funding: {data.get('funding_rate', {}).get('rate', 'N/A')}
💰 OI: {data.get('open_interest', {}).get('value', 'N/A'):,.0f}
😱 F&G: {data.get('fear_greed', {}).get('value', 'N/A')}
⏰ {datetime.now().strftime('%H:%M:%S')}
    """
    send_telegram_alert(message)

def start_scheduler():
    """Start the scheduler"""
    print("🚀 Starting scheduler...")
    schedule.every(5).minutes.do(scheduled_data_push)
    
    # Run once immediately
    scheduled_data_push()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    try:
        print("=" * 50)
        print("🚀 CRYPTO DATA AGGREGATOR - SCHEDULER")
        print("=" * 50)
        print(f"📡 Data will be pushed every 5 minutes")
        print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        start_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")