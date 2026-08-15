# data_fetcher.py - UPDATED WITH 5m & 15m
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import numpy as np

class DataFetcher:
    """Enhanced Real-Time Data Fetcher with 5m & 15m support"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 2
        self.executor = ThreadPoolExecutor(max_workers=12)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.historical_cache = {}
        print("✅ DataFetcher initialized (5m & 15m SUPPORT)")
    
    def fetch_all_data(self, symbol: str = "BTCUSDT") -> Dict:
        cache_key = f"all_data_{symbol}"
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if (time.time() - timestamp) < self.cache_ttl:
                return data
        
        data = self._fetch_parallel(symbol)
        self.cache[cache_key] = (data, time.time())
        return data
    
    def _fetch_parallel(self, symbol: str) -> Dict:
        results = {}
        
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = {
                'premium': executor.submit(self._get_premium_index, symbol),
                'oi': executor.submit(self._get_open_interest, symbol),
                'price': executor.submit(self._get_ticker_price, symbol),
                'ticker': executor.submit(self._get_ticker_24hr, symbol),
                'depth': executor.submit(self._get_order_book, symbol, 50),
                # ===== 5m & 15m KLINES ADDED =====
                'klines_1m': executor.submit(self._get_klines, symbol, '1m', 100),
                'klines_5m': executor.submit(self._get_klines, symbol, '5m', 100),
                'klines_15m': executor.submit(self._get_klines, symbol, '15m', 80),
                'klines_1h': executor.submit(self._get_klines, symbol, '1h', 100),
                'klines_4h': executor.submit(self._get_klines, symbol, '4h', 50),
            }
            
            for name, future in futures.items():
                try:
                    results[name] = future.result(timeout=10)
                except Exception as e:
                    print(f"⚠️ Error fetching {name}: {e}")
                    results[name] = None
        
        results['historical'] = self._get_historical_data(symbol)
        return self._build_response(symbol, results)
    
    def _get_premium_index(self, symbol: str) -> Dict:
        resp = self.session.get(
            f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}",
            timeout=5
        )
        return resp.json()
    
    def _get_open_interest(self, symbol: str) -> float:
        resp = self.session.get(
            f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}",
            timeout=5
        )
        return float(resp.json()['openInterest'])
    
    def _get_ticker_price(self, symbol: str) -> float:
        resp = self.session.get(
            f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}",
            timeout=5
        )
        return float(resp.json()['price'])
    
    def _get_ticker_24hr(self, symbol: str) -> Dict:
        resp = self.session.get(
            f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}",
            timeout=5
        )
        return resp.json()
    
    def _get_order_book(self, symbol: str, limit: int = 50) -> Dict:
        resp = self.session.get(
            f"https://fapi.binance.com/fapi/v1/depth?symbol={symbol}&limit={limit}",
            timeout=5
        )
        data = resp.json()
        bids = [(float(b[0]), float(b[1])) for b in data['bids']]
        asks = [(float(a[0]), float(a[1])) for a in data['asks']]
        
        bid_vol_5 = sum([b[1] for b in bids[:5]])
        ask_vol_5 = sum([a[1] for a in asks[:5]])
        bid_vol_10 = sum([b[1] for b in bids[:10]])
        ask_vol_10 = sum([a[1] for a in asks[:10]])
        
        return {
            'bids': bids[:20],
            'asks': asks[:20],
            'bid_volume_5': bid_vol_5,
            'ask_volume_5': ask_vol_5,
            'bid_volume_10': bid_vol_10,
            'ask_volume_10': ask_vol_10,
            'imbalance_5': (bid_vol_5 - ask_vol_5) / (bid_vol_5 + ask_vol_5 + 0.001),
            'imbalance_10': (bid_vol_10 - ask_vol_10) / (bid_vol_10 + ask_vol_10 + 0.001),
            'lastUpdateId': data['lastUpdateId']
        }
    
    def _get_klines(self, symbol: str, interval: str = "1m", limit: int = 100) -> List:
        resp = self.session.get(
            f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}",
            timeout=5
        )
        return resp.json()
    
    def _get_historical_data(self, symbol: str) -> Dict:
        cache_key = f"historical_{symbol}"
        if cache_key in self.historical_cache:
            data, timestamp = self.historical_cache[cache_key]
            if (time.time() - timestamp) < 3600:
                return data
        
        try:
            # Use 1d klines for accurate volume average
            klines = self._get_klines(symbol, '1d', 30)
            if not klines:
                return self._get_default_historical()
            
            import pandas as pd
            df = pd.DataFrame(klines, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_vol',
                'taker_buy_quote', 'ignore'
            ])
            
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            
            # Correct avg volume (24h average)
            avg_volume = df['volume'].mean()  # Daily average
            avg_range = (df['high'] - df['low']).mean()
            volatility = df['close'].pct_change().std() * 100
            
            funding_history = self._get_funding_history(symbol)
            
            result = {
                'avg_volume': avg_volume,
                'avg_range': avg_range,
                'volatility': volatility,
                'avg_funding_rate': funding_history.get('avg', 0.0001),
                'funding_std': funding_history.get('std', 0.0002),
                'max_funding': funding_history.get('max', 0.001),
                'min_funding': funding_history.get('min', -0.001),
            }
            
            self.historical_cache[cache_key] = (result, time.time())
            return result
            
        except Exception as e:
            print(f"⚠️ Historical data error: {e}")
            return self._get_default_historical()
    
    def _get_funding_history(self, symbol: str) -> Dict:
        try:
            resp = self.session.get(
                f"https://fapi.binance.com/fapi/v1/fundingInfo?symbol={symbol}",
                timeout=5
            )
            data = resp.json()
            if data and len(data) > 0:
                rates = []
                for item in data:
                    if 'fundingRate' in item:
                        rates.append(float(item['fundingRate']))
                
                if rates:
                    return {
                        'avg': sum(rates) / len(rates),
                        'std': np.std(rates) if len(rates) > 1 else 0.0002,
                        'max': max(rates),
                        'min': min(rates),
                    }
        except:
            pass
        return {'avg': 0.0001, 'std': 0.0002, 'max': 0.001, 'min': -0.001}
    
    def _get_default_historical(self) -> Dict:
        return {
            'avg_volume': 30000,
            'avg_range': 100,
            'volatility': 1.5,
            'avg_funding_rate': 0.0001,
            'funding_std': 0.0002,
            'max_funding': 0.001,
            'min_funding': -0.001,
        }
    
    def _build_response(self, symbol: str, results: Dict) -> Dict:
        premium = results.get('premium', {})
        ticker = results.get('ticker', {})
        depth = results.get('depth', {})
        historical = results.get('historical', {})
        
        # Get all klines
        klines_1m = results.get('klines_1m', [])
        klines_5m = results.get('klines_5m', [])
        klines_15m = results.get('klines_15m', [])
        klines_1h = results.get('klines_1h', [])
        klines_4h = results.get('klines_4h', [])
        
        # Calculate VWAP from 1m klines
        vwap = float(ticker.get('weightedAvgPrice', 0)) if ticker else 0
        if not vwap and klines_1m:
            total_value, total_volume = 0, 0
            for k in klines_1m[-20:]:
                close = float(k[4])
                volume = float(k[5])
                total_value += close * volume
                total_volume += volume
            vwap = total_value / total_volume if total_volume > 0 else 0
        
        return {
            'timestamp': int(time.time() * 1000),
            'datetime': datetime.now().isoformat(),
            'symbol': symbol,
            'price': results.get('price', 0),
            'mark_price': float(premium.get('markPrice', 0)),
            'funding_rate': float(premium.get('lastFundingRate', 0)),
            'funding_avg': historical.get('avg_funding_rate', 0.0001),
            'funding_std': historical.get('funding_std', 0.0002),
            'next_funding_time': premium.get('nextFundingTime', 0),
            'open_interest': results.get('oi', 0),
            'high_24h': float(ticker.get('highPrice', 0)) if ticker else 0,
            'low_24h': float(ticker.get('lowPrice', 0)) if ticker else 0,
            'volume': float(ticker.get('volume', 0)) if ticker else 0,
            'avg_volume': historical.get('avg_volume', 30000),
            'vwap': vwap,
            'price_change': float(ticker.get('priceChange', 0)) if ticker else 0,
            'price_change_percent': float(ticker.get('priceChangePercent', 0)) if ticker else 0,
            'volatility': historical.get('volatility', 1.5),
            'order_book': depth,
            'klines': {
                '1m': klines_1m[-50:],
                '5m': klines_5m[-50:],
                '15m': klines_15m[-40:],
                '1h': klines_1h[-30:],
                '4h': klines_4h[-20:],
            },
            'historical': historical,
            'status': 'success',
            'source': 'binance_futures'
        }