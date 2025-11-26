import pandas as pd
from datetime import datetime
from bots.base_bot import SignalType, TradingSignal

class WickMasterPro:
    def __init__(self, wick_threshold=2.0, pattern_min_score=60, volume_threshold=1.5):
        self.wick_threshold = wick_threshold
        self.pattern_min_score = pattern_min_score
        self.volume_threshold = volume_threshold
    
    def analyze(self, symbol: str, df: pd.DataFrame, market_data: dict) -> TradingSignal:
        if df.empty or len(df) < 25:
            return self._hold_signal(symbol, df)
        
        # Calculate technical indicators
        df = self._add_indicators(df)
        last = df.iloc[-1]
        
        # Wick analysis
        body_size = abs(last['close'] - last['open'])
        lower_wick = last['open'] - last['low'] if last['close'] > last['open'] else last['close'] - last['low']
        upper_wick = last['high'] - last['close'] if last['close'] > last['open'] else last['high'] - last['open']
        
        # Pattern scoring
        score = 0
        wick_ratio = 0
        
        if body_size > 0:
            wick_ratio = max(lower_wick, upper_wick) / body_size
            if wick_ratio >= self.wick_threshold:
                score += 40
        
        # RSI check
        if 'rsi' in df.columns:
            rsi = last['rsi']
            if rsi < 30:
                score += 20  # Oversold
            elif rsi > 70:
                score -= 20  # Overbought
        
        # Volume confirmation
        if 'volume' in df.columns and len(df) > 1:
            avg_vol = df['volume'].iloc[-20:-1].mean()
            if last['volume'] > avg_vol * self.volume_threshold:
                score += 20
        
        # Moving average trend
        if 'sma_20' in df.columns:
            if last['close'] > last['sma_20']:
                score += 10
            else:
                score -= 10
        
        # Generate signal
        if score >= self.pattern_min_score and lower_wick > upper_wick:
            # Bullish wick reversal
            entry = last['close']
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else (last['high'] - last['low'])
            stop_loss = entry - (2.5 * atr)
            take_profit = entry + (3.0 * (entry - stop_loss))
            
            return TradingSignal(
                signal_type=SignalType.BUY,
                symbol=symbol,
                confidence=min(score / 100.0, 0.95),
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                position_size=0.001,
                timestamp=datetime.now(),
                reason=f"Bullish wick reversal (ratio={wick_ratio:.2f}, score={score})",
                indicators={
                    'wick_ratio': wick_ratio,
                    'score': score,
                    'rsi': last.get('rsi', None),
                    'volume_ratio': last['volume'] / avg_vol if 'volume' in df.columns else None
                },
                metadata={'timeframe': '1h', 'pattern': 'hammer'}
            )
        
        return self._hold_signal(symbol, df)
    
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        # Simple Moving Average
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(window=14).mean()
        
        return df
    
    def _hold_signal(self, symbol: str, df: pd.DataFrame) -> TradingSignal:
        last_price = df.iloc[-1]['close'] if not df.empty else 0.0
        return TradingSignal(
            signal_type=SignalType.HOLD,
            symbol=symbol,
            confidence=0.0,
            entry_price=last_price,
            stop_loss=last_price,
            take_profit=last_price,
            position_size=0.0,
            timestamp=datetime.now(),
            reason="No valid pattern detected",
            indicators={},
            metadata={}
        )
    
    def generate_signals(self, candles, symbol, timeframe, **kwargs):
        """Adapter for strategy loader - converts candles to signals"""
        if not candles or len(candles) < 25:
            return []
        
        # Convert candles to DataFrame
        df = pd.DataFrame(candles)
        df.columns = ['t', 'o', 'h', 'l', 'c', 'v']
        df.rename(columns={'o':'open','h':'high','l':'low','c':'close','v':'volume'}, inplace=True)
        
        # Analyze using our main method
        signal = self.analyze(symbol, df, kwargs.get('market_data', {}))
        
        # Convert TradingSignal to dict format expected by the system
        if signal.signal_type == SignalType.HOLD:
            return []
        
        return [{
            'side': 'buy' if signal.signal_type == SignalType.BUY else 'sell',
            'symbol': signal.symbol,
            'price': signal.entry_price,
            'confidence': signal.confidence,
            'reason': signal.reason,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'timestamp': signal.timestamp.isoformat(),
            'metadata': signal.metadata
        }]
