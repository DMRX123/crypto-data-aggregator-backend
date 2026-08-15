# webhook_handler.py
from flask import Flask, request, jsonify
from datetime import datetime
import requests
from data_fetcher import DataFetcher
from config import Config

app = Flask(__name__)

class WebhookHandler:
    def __init__(self):
        self.webhook_url = Config.TRADINGVIEW_WEBHOOK
        print("✅ WebhookHandler initialized")
    
    def send_to_tradingview(self, data):
        try:
            if not self.webhook_url:
                print("⚠️ No webhook URL")
                return False
            response = requests.post(self.webhook_url, json=data, timeout=5)
            if response.status_code == 200:
                print(f"✅ Webhook sent at {datetime.now()}")
                return True
            print(f"❌ Webhook failed: {response.status_code}")
            return False
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return False
    
    def send_telegram_alert(self, message):
        try:
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {'chat_id': Config.TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'active', 'service': 'Crypto Data Aggregator', 'timestamp': datetime.now().isoformat()})

@app.route('/data/latest', methods=['GET'])
def get_latest_data():
    try:
        fetcher = DataFetcher()
        data = fetcher.fetch_all_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data/send', methods=['POST'])
def send_data():
    try:
        fetcher = DataFetcher()
        data = fetcher.fetch_all_data()
        handler = WebhookHandler()
        success = handler.send_to_tradingview(data)
        return jsonify({'status': 'success', 'data_sent': success, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    try:
        data = request.json
        print(f"📥 Webhook received: {data}")
        return jsonify({'status': 'received', 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)