# signal_engine.py - UPDATED WITH 5m & 15m ANALYSIS
import time
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Signal:
    timestamp: int
    symbol: str
    signal_type: str
    strength: int
    confidence: str
    indicators: Dict
    summary: str
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float

class SignalEngine:
    """Institutional Grade Signal Engine with 5m & 15m support"""
    
    def __init__(self):
        self.signals_history = []
        self._min_klines = 50
        print("✅ Signal Engine initialized (5m & 15m SUPPORT)")
    
    def analyze(self, data: Dict) -> Signal:
        indicators = {}
        bullish_score = 0
        bearish_score = 0
        
        # ----- GET ALL TIMEFRAMES -----
        klines_all = data.get('klines', {})
        klines_1m = klines_all.get('1m', [])
        klines_5m = klines_all.get('5m', [])
        klines_15m = klines_all.get('15m', [])
        klines_1h = klines_all.get('1h', [])
        klines_4h = klines_all.get('4h', [])
        
        # ===== 1. FUNDING RATE (DYNAMIC) =====
        fr = data.get('funding_rate', 0)
        fr_avg = data.get('funding_avg', 0.0001)
        fr_std = data.get('funding_std', 0.0002)
        fr_z_score = (fr - fr_avg) / (fr_std + 0.0001)
        
        indicators['funding_rate'] = fr
        indicators['funding_rate_pct'] = fr * 100
        indicators['funding_z_score'] = fr_z_score
        
        if fr_z_score > 2.5:
            bearish_score += 4
            indicators['funding_signal'] = "🔴 EXTREME OVERHEATED"
        elif fr_z_score > 1.5:
            bearish_score += 2
            indicators['funding_signal'] = "🟡 OVERHEATED"
        elif fr_z_score < -2.5:
            bullish_score += 4
            indicators['funding_signal'] = "🟢 EXTREME OVERSOLD"
        elif fr_z_score < -1.5:
            bullish_score += 2
            indicators['funding_signal'] = "🟡 OVERSOLD"
        else:
            indicators['funding_signal'] = "⚪ NEUTRAL"
        
        # ===== 2. OPEN INTEREST =====
        oi = data.get('open_interest', 0)
        indicators['open_interest'] = oi
        if oi > 100000:
            bullish_score += 1
            indicators['oi_signal'] = "🔵 HIGH LIQUIDITY"
        
        # ===== 3. CVD (Cumulative Volume Delta) =====
        cvd = self._calculate_cvd(klines_1m)
        indicators['cvd'] = cvd
        indicators['cvd_signal'] = "🟢 BUYERS ACTIVE" if cvd > 0 else "🔴 SELLERS ACTIVE"
        bullish_score += 1 if cvd > 0 else 0
        bearish_score += 1 if cvd < 0 else 0
        
        # ===== 4. RSI - MULTI-TIMEFRAME (1m, 5m, 15m, 1h) =====
        rsi_1m = self._calculate_rsi(klines_1m, 14)
        rsi_5m = self._calculate_rsi(klines_5m, 14)
        rsi_15m = self._calculate_rsi(klines_15m, 14)
        rsi_1h = self._calculate_rsi(klines_1h, 14)
        rsi_4h = self._calculate_rsi(klines_4h, 14)
        
        indicators['rsi_1m'] = rsi_1m
        indicators['rsi_5m'] = rsi_5m
        indicators['rsi_15m'] = rsi_15m
        indicators['rsi_1h'] = rsi_1h
        indicators['rsi_4h'] = rsi_4h
        
        # RSI Bullish/Bearish count
        rsi_bullish = sum([1 for r in [rsi_1m, rsi_5m, rsi_15m, rsi_1h] if r < 40])
        rsi_bearish = sum([1 for r in [rsi_1m, rsi_5m, rsi_15m, rsi_1h] if r > 60])
        
        if rsi_bullish >= 3:
            bullish_score += 3
            indicators['rsi_signal'] = "🟢 OVERSOLD (MTF)"
        elif rsi_bearish >= 3:
            bearish_score += 3
            indicators['rsi_signal'] = "🔴 OVERBOUGHT (MTF)"
        elif rsi_bullish >= 2:
            bullish_score += 1
            indicators['rsi_signal'] = "🟡 SLIGHTLY OVERSOLD"
        elif rsi_bearish >= 2:
            bearish_score += 1
            indicators['rsi_signal'] = "🟡 SLIGHTLY OVERBOUGHT"
        else:
            indicators['rsi_signal'] = "⚪ NEUTRAL"
        
        # ===== 5. PRICE VS VWAP =====
        price = data.get('price', 0)
        vwap = data.get('vwap', price)
        pv_diff = ((price - vwap) / vwap * 100) if vwap > 0 else 0
        indicators['price_vs_vwap'] = pv_diff
        
        if pv_diff > 0.5:
            bullish_score += 1
            indicators['vwap_signal'] = "📈 ABOVE VWAP"
        elif pv_diff < -0.5:
            bearish_score += 1
            indicators['vwap_signal'] = "📉 BELOW VWAP"
        else:
            indicators['vwap_signal'] = "⚪ NEAR VWAP"
        
        # ===== 6. ORDER BOOK IMBALANCE =====
        depth = data.get('order_book', {})
        imb_avg = (depth.get('imbalance_5', 0) + depth.get('imbalance_10', 0)) / 2
        indicators['order_book_imbalance'] = imb_avg
        
        if imb_avg > 0.3:
            bullish_score += 2
            indicators['order_book_signal'] = "🟢 STRONG BUY PRESSURE"
        elif imb_avg > 0.1:
            bullish_score += 1
            indicators['order_book_signal'] = "🟡 BUY PRESSURE"
        elif imb_avg < -0.3:
            bearish_score += 2
            indicators['order_book_signal'] = "🔴 STRONG SELL PRESSURE"
        elif imb_avg < -0.1:
            bearish_score += 1
            indicators['order_book_signal'] = "🟡 SELL PRESSURE"
        else:
            indicators['order_book_signal'] = "⚪ BALANCED"
        
        # ===== 7. VOLUME (DYNAMIC) =====
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', 30000)
        v_ratio = volume / avg_volume if avg_volume > 0 else 1
        indicators['volume_ratio'] = v_ratio
        
        if v_ratio > 2:
            if price > vwap:
                bullish_score += 1
            else:
                bearish_score += 1
            indicators['volume_signal'] = "🔊 HIGH VOLUME SPIKE"
        elif v_ratio > 1.5:
            indicators['volume_signal'] = "🔉 ABOVE AVG"
        else:
            indicators['volume_signal'] = "⚪ NORMAL"
        
        # ===== 8. PRICE POSITION =====
        high = data.get('high_24h', price)
        low = data.get('low_24h', price)
        range_24h = high - low
        p_pos = (price - low) / (range_24h + 0.001) if range_24h > 0 else 0.5
        indicators['price_position'] = p_pos * 100
        
        if p_pos > 0.8:
            bearish_score += 1
            indicators['range_signal'] = "📈 NEAR HIGH"
        elif p_pos < 0.2:
            bullish_score += 1
            indicators['range_signal'] = "📉 NEAR LOW"
        else:
            indicators['range_signal'] = "⚪ MID RANGE"
        
        # ===== 9. MACD - MULTI-TIMEFRAME =====
        macd_1m = self._calculate_macd(klines_1m)
        macd_5m = self._calculate_macd(klines_5m)
        macd_15m = self._calculate_macd(klines_15m)
        macd_1h = self._calculate_macd(klines_1h)
        
        indicators['macd_1m'] = macd_1m
        indicators['macd_5m'] = macd_5m
        indicators['macd_15m'] = macd_15m
        indicators['macd_1h'] = macd_1h
        
        macd_bullish = sum([1 for m in [macd_1m, macd_5m, macd_15m, macd_1h] if m == "BULLISH"])
        macd_bearish = sum([1 for m in [macd_1m, macd_5m, macd_15m, macd_1h] if m == "BEARISH"])
        
        if macd_bullish >= 3:
            bullish_score += 3
            indicators['macd_signal'] = "🟢 STRONG BULLISH (MTF)"
        elif macd_bearish >= 3:
            bearish_score += 3
            indicators['macd_signal'] = "🔴 STRONG BEARISH (MTF)"
        elif macd_bullish >= 2:
            bullish_score += 1
            indicators['macd_signal'] = "🟡 BULLISH"
        elif macd_bearish >= 2:
            bearish_score += 1
            indicators['macd_signal'] = "🟡 BEARISH"
        else:
            indicators['macd_signal'] = "⚪ NEUTRAL"
        
        # ===== 10. VOLATILITY =====
        vol = data.get('volatility', 1.5)
        indicators['volatility'] = vol
        indicators['volatility_signal'] = "🔊 HIGH VOLATILITY" if vol > 2.5 else "🔉 MEDIUM" if vol > 1.5 else "⚪ LOW"
        
        # ===== FINAL SCORE =====
        net_score = bullish_score - bearish_score
        indicators['bullish_score'] = bullish_score
        indicators['bearish_score'] = bearish_score
        indicators['net_score'] = net_score
        
        # ===== SIGNAL TYPE =====
        if net_score >= 6:
            signal_type = "STRONG_BULLISH"
            strength = min(10, net_score + 2)
            confidence = "HIGH"
        elif net_score >= 3:
            signal_type = "BULLISH"
            strength = min(10, net_score + 1)
            confidence = "MEDIUM"
        elif net_score <= -6:
            signal_type = "STRONG_BEARISH"
            strength = min(10, abs(net_score) + 2)
            confidence = "HIGH"
        elif net_score <= -3:
            signal_type = "BEARISH"
            strength = min(10, abs(net_score) + 1)
            confidence = "MEDIUM"
        else:
            signal_type = "NEUTRAL"
            strength = abs(net_score)
            confidence = "LOW"
        
        indicators['confidence'] = confidence
        
        # ===== RISK MANAGEMENT =====
        atr = self._calculate_atr(klines_15m if klines_15m else klines_5m)
        if atr < 1:
            atr = price * 0.005
        
        if signal_type in ["STRONG_BULLISH", "BULLISH"]:
            entry = price
            stop_loss = price - atr * 2.0
            take_profit = price + atr * 3.0
        elif signal_type in ["STRONG_BEARISH", "BEARISH"]:
            entry = price
            stop_loss = price + atr * 2.0
            take_profit = price - atr * 3.0
        else:
            entry = price
            stop_loss = price - atr * 1.5
            take_profit = price + atr * 2.0
        
        risk_reward = abs(take_profit - entry) / abs(stop_loss - entry) if abs(stop_loss - entry) > 0 else 0
        
        summary = self._generate_summary(
            signal_type, strength, confidence,
            indicators, bullish_score, bearish_score
        )
        
        return Signal(
            timestamp=int(time.time() * 1000),
            symbol=data.get('symbol', 'BTCUSDT'),
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            indicators=indicators,
            summary=summary,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=risk_reward
        )
    
    def _calculate_rsi(self, klines: List, period: int = 14) -> float:
        if not klines or len(klines) < period * 2:
            return 50.0
        
        closes = [float(k[4]) for k in klines[-period*2:]]
        gains, losses = [], []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change >= 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            return 100.0
        if avg_gain == 0:
            return 0.0
        
        return round(100 - (100 / (1 + avg_gain / avg_loss)), 2)
    
    def _calculate_atr(self, klines: List, period: int = 14) -> float:
        if not klines or len(klines) < period + 1:
            return 100.0
        
        trs = []
        for k in klines[-period*2:]:
            high = float(k[2])
            low = float(k[3])
            close = float(k[4])
            tr = max(high - low, abs(high - close), abs(low - close))
            trs.append(tr)
        
        return sum(trs[-period:]) / period if trs else 100.0
    
    def _calculate_macd(self, klines: List) -> str:
        if not klines or len(klines) < 26:
            return "NEUTRAL"
        
        closes = [float(k[4]) for k in klines[-50:]]
        
        def ema(data, period):
            if len(data) < period:
                return data[-1] if data else 0
            alpha = 2 / (period + 1)
            result = data[0]
            for price in data[1:]:
                result = price * alpha + result * (1 - alpha)
            return result
        
        ema12 = ema(closes, 12)
        ema26 = ema(closes, 26)
        
        if ema12 > ema26 * 1.001:
            return "BULLISH"
        elif ema12 < ema26 * 0.999:
            return "BEARISH"
        return "NEUTRAL"
    
    def _calculate_cvd(self, klines: List) -> float:
        if not klines:
            return 0
        
        cvd = 0
        for k in klines[-30:]:
            taker_buy = float(k[9]) if len(k) > 9 else 0
            taker_sell = float(k[5]) - taker_buy if len(k) > 5 else 0
            cvd += taker_buy - taker_sell
        
        return cvd
    
    def _generate_summary(self, signal_type: str, strength: int, confidence: str,
                         indicators: Dict, bullish: int, bearish: int) -> str:
        parts = []
        parts.append(f"📊 {signal_type} ({strength}/10) [Confidence: {confidence}]")
        parts.append(f"Funding: {indicators.get('funding_signal', 'N/A')}")
        parts.append(f"RSI: {indicators.get('rsi_1m', 50):.1f}/{indicators.get('rsi_5m', 50):.1f}/{indicators.get('rsi_15m', 50):.1f}")
        parts.append(f"MACD: {indicators.get('macd_signal', 'N/A')}")
        parts.append(f"CVD: {indicators.get('cvd_signal', 'N/A')}")
        parts.append(f"Score: {bullish}🟢/{bearish}🔴")
        return " | ".join(parts)