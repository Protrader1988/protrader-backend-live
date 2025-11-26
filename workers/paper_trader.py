import os, time, yaml
from data.providers.alpaca_data import get_bars as stocks_bars
from data.providers.gemini_data import get_bars as crypto_bars
from strategies.loader import load_strategy
from src.trading.execution_router import ExecutionRouter

def fetch_bars(symbol, timeframe):
    return crypto_bars(symbol, timeframe) if "/" in symbol else stocks_bars(symbol, timeframe)

def run_paper_loop():
    with open("config/strategies.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    
    universe = cfg.get("universe", [])
    strats = [s for s in cfg.get("strategies", []) if s.get("enabled", True)]
    router = ExecutionRouter()
    demo = os.getenv("DEMO_ORDER", "false").lower() == "true"
    
    print(f"[PAPER] Starting loop. Demo={demo}, Universe={len(universe)} symbols, Strategies={len(strats)}")
    
    while True:
        for sym in universe:
            for sc in strats:
                try:
                    candles = fetch_bars(sym, sc.get("timeframe", "1h"))
                    strat = load_strategy(sc["name"], sc.get("params", {}))
                    signals = strat.generate_signals(candles=candles, symbol=sym, timeframe=sc.get("timeframe", "1h"))
                    
                    for sig in signals:
                        qty = sc.get("paper_qty", 0.001)
                        if not demo:
                            resp = router.submit(sig["side"], sym, qty, "market")
                            print(f"[PAPER] {sym} {sig['side']} {qty} | {resp}")
                        else:
                            print(f"[DEMO] {sym} {sig['side']} {qty} (not executed)")
                except Exception as e:
                    print(f"[ERROR] {sym} {sc['name']}: {e}")
        
        time.sleep(3600)  # 1 hour

if __name__ == "__main__":
    run_paper_loop()
