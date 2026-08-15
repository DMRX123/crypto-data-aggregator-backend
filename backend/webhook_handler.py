# webhook_handler.py - COMPLETE
from flask import Flask, request, jsonify
from datetime import datetime
import requests
import os
from typing import Dict
from signal_engine import Signal

app = Flask(__name__)

class WebhookHandler:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '8526613698:AAG1g7Hc-ZiukV20e6XHW6LPEG1vAor_a_4')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '5223741844')
        print("✅ WebhookHandler initialized")
    
    def send_telegram_alert(self, message: str) -> bool:
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            resp = requests.post(url, json={
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }, timeout=30)
            return resp.status_code == 200
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def send_signal_alert(self, data: Dict, signal: Signal) -> bool:
        emoji = "🚀" if "BULLISH" in signal.signal_type else "🔻" if "BEARISH" in signal.signal_type else "⏸️"
        
        message = f"""
{emoji} <b>SIGNAL ALERT - {signal.signal_type}</b>
━━━━━━━━━━━━━━━━━━━━━━
🪙 <b>{data['symbol']}</b>
💰 Price: <b>${data['price']:,.2f}</b>
📈 Signal: <b>{signal.signal_type}</b> ({signal.strength}/10)
📊 Confidence: <b>{signal.confidence}</b>

📊 <b>Key Indicators</b>
• Funding: {signal.indicators.get('funding_signal', 'N/A')} ({signal.indicators.get('funding_rate_pct', 0):.4f}%)
• RSI: {signal.indicators.get('rsi', 50):.1f} ({signal.indicators.get('rsi_signal', 'N/A')})
• OI: {data.get('open_interest', 0):,.0f}
• CVD: {signal.indicators.get('cvd_signal', 'N/A')}
• Order Book: {signal.indicators.get('order_book_signal', 'N/A')}

🎯 <b>Levels</b>
• Entry: <b>${signal.entry_price:,.2f}</b>
• Stop Loss: <b>${signal.stop_loss:,.2f}</b> ({(abs(signal.stop_loss - signal.entry_price)/signal.entry_price*100):.2f}%)
• Take Profit: <b>${signal.take_profit:,.2f}</b> ({(abs(signal.take_profit - signal.entry_price)/signal.entry_price*100):.2f}%)
• Risk/Reward: <b>{signal.risk_reward:.2f}</b>

📝 {signal.summary}
⏰ {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━
"""
        return self.send_telegram_alert(message)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'active', 'service': 'Crypto Signal Engine', 'version': '3.0'})

@app.route('/data/latest', methods=['GET'])
def get_latest_data():
    from data_fetcher import DataFetcher
    fetcher = DataFetcher()
    symbol = request.args.get('symbol', 'BTCUSDT')
    return jsonify(fetcher.fetch_all_data(symbol))

@app.route('/signal', methods=['GET'])
def get_signal():
    from data_fetcher import DataFetcher
    from signal_engine import SignalEngine
    
    fetcher = DataFetcher()
    symbol = request.args.get('symbol', 'BTCUSDT')
    data = fetcher.fetch_all_data(symbol)
    
    engine = SignalEngine()
    signal = engine.analyze(data)
    
    return jsonify({
        'symbol': symbol,
        'price': data.get('price', 0),
        'signal': {
            'type': signal.signal_type,
            'strength': signal.strength,
            'confidence': signal.confidence,
            'summary': signal.summary,
            'entry': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'risk_reward': signal.risk_reward,
            'indicators': signal.indicators
        },
        'timestamp': data.get('timestamp')
    })

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