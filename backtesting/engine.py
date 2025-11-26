from src.trading.portfolio import Portfolio

class BacktestEngine:
    def __init__(self, initial_cash=10000.0):
        self.portfolio = Portfolio(initial_cash)
        self.trades = []
    
    def run(self, signals, candles):
        for sig in signals:
            self.portfolio.on_signal(sig)
            self.trades.append(sig)
        
        final_price = candles[-1]["c"] if candles else 0.0
        nav = self.portfolio.nav(final_price)
        
        return {
            "initial": self.portfolio.cash if self.portfolio.pos == 0 else 10000.0,
            "final": nav,
            "trades": len(self.trades),
            "return_pct": round((nav / 10000.0 - 1) * 100, 2)
        }
