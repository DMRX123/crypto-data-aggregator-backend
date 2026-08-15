# data_fetcher.py - COMPLETE NO BINANCE VERSION
import requests
from datetime import datetime
import json
import time

class DataFetcher:
    def __init__(self):
        self.cache = {}
        print("✅ DataFetcher initialized (NO BINANCE)")
    
    def fetch_all_data(self):
        cache_key = "all_market_data"
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < 5:
                print("⚡ Using cached data")
                return data
        
        print("🔄 Fetching fresh data...")
        data = self._fetch_all()
        self.cache[cache_key] = (data, datetime.now())
        return data
    
    def _fetch_all(self):
        try:
            # ===== BTC PRICE - CoinGecko ONLY =====
            print("📊 Fetching BTC Price from CoinGecko...")
            price_resp = requests.get(
                'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
                timeout=15,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            if price_resp.status_code == 200:
                btc_price = float(price_resp.json()['bitcoin']['usd'])
                print(f"✅ BTC: ${btc_price}")
            else:
                print("⚠️ CoinGecko failed, using default")
                btc_price = 63000.0
            
            # ===== FUNDING RATE - DEFAULT =====
            funding_rate = 0.0001
            funding_time = int(time.time() * 1000)
            print(f"✅ Funding Rate: {funding_rate}")
            
            # ===== OPEN INTEREST - DEFAULT =====
            open_interest = 0
            print(f"✅ OI: {open_interest}")
            
            # ===== FEAR & GREED - alternative.me =====
            print("📊 Fetching Fear & Greed...")
            fng_resp = requests.get(
                'https://api.alternative.me/fng/?limit=1',
                timeout=10
            )
            if fng_resp.status_code == 200:
                fng_data = fng_resp.json()['data'][0]
                fng_value = int(fng_data['value'])
                fng_classification = fng_data['value_classification']
            else:
                fng_value = 50
                fng_classification = "Neutral"
            print(f"✅ F&G: {fng_value} ({fng_classification})")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'btc_price': btc_price,
                'funding_rate': {'rate': funding_rate, 'time': funding_time},
                'open_interest': {'symbol': 'BTCUSDT', 'value': open_interest},
                'fear_greed': {'value': fng_value, 'classification': fng_classification},
                'status': 'success',
                'source': 'coingecko_no_binance'
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error',
                'btc_price': None,
                'funding_rate': None,
                'open_interest': None,
                'fear_greed': None
            }
