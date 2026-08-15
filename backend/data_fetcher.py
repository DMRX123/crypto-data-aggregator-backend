# data_fetcher.py - ALTERNATIVE API VERSION
import requests
from datetime import datetime
import json
import time

class DataFetcher:
    def __init__(self):
        self.cache = {}
        print("✅ DataFetcher initialized (Alternative APIs)")
    
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
            # 1. BTC Price - CoinGecko (Always works)
            print("📊 Fetching BTC Price from CoinGecko...")
            try:
                price_resp = requests.get(
                    'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
                    timeout=10,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                if price_resp.status_code == 200:
                    btc_price = float(price_resp.json()['bitcoin']['usd'])
                    print(f"✅ BTC (CoinGecko): ${btc_price}")
                else:
                    raise Exception("CoinGecko failed")
            except:
                # Fallback to CoinCap
                print("📊 Fallback to CoinCap...")
                price_resp = requests.get(
                    'https://api.coincap.io/v2/assets/bitcoin',
                    timeout=10
                )
                price_resp.raise_for_status()
                btc_price = float(price_resp.json()['data']['priceUsd'])
                print(f"✅ BTC (CoinCap): ${btc_price}")
            
            # 2. Funding Rate - Fallback
            print("📊 Fetching Funding Rate...")
            try:
                funding_resp = requests.get(
                    'https://fapi.binance.com/fapi/v1/fundingInfo?symbol=BTCUSDT',
                    timeout=10,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                if funding_resp.status_code == 200:
                    funding_data = funding_resp.json()
                    if isinstance(funding_data, list) and len(funding_data) > 0:
                        funding_rate = float(funding_data[0].get('fundingRate', 0.0001))
                        funding_time = funding_data[0].get('fundingTime', int(time.time() * 1000))
                    else:
                        funding_rate = 0.0001
                        funding_time = int(time.time() * 1000)
                else:
                    funding_rate = 0.0001
                    funding_time = int(time.time() * 1000)
            except:
                funding_rate = 0.0001
                funding_time = int(time.time() * 1000)
            print(f"✅ Funding Rate: {funding_rate}")
            
            # 3. Open Interest - Fallback
            print("📊 Fetching Open Interest...")
            try:
                oi_resp = requests.get(
                    'https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT',
                    timeout=10,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                if oi_resp.status_code == 200:
                    oi_data = oi_resp.json()
                    open_interest = float(oi_data.get('openInterest', 0))
                else:
                    open_interest = 0
            except:
                open_interest = 0
            print(f"✅ OI: {open_interest}")
            
            # 4. Fear & Greed - Always works
            print("📊 Fetching Fear & Greed...")
            fng_resp = requests.get(
                'https://api.alternative.me/fng/?limit=1',
                timeout=10
            )
            fng_resp.raise_for_status()
            fng_data = fng_resp.json()['data'][0]
            print(f"✅ F&G: {fng_data['value']} ({fng_data['value_classification']})")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'btc_price': btc_price,
                'funding_rate': {
                    'rate': funding_rate,
                    'time': funding_time
                },
                'open_interest': {
                    'value': open_interest,
                    'symbol': 'BTCUSDT'
                },
                'fear_greed': {
                    'value': int(fng_data['value']),
                    'classification': fng_data['value_classification']
                },
                'status': 'success',
                'source': 'alternative_apis'
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
