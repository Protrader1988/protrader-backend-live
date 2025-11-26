# Protrader Full Backend (Render-ready)

Always-on backend for paper + gated live trading. Includes:
- API (health, screener, signals, backtest, news)
- Workers (paper loop, news sentiment)
- Strategy loader + your WickMasterPro strategy
- Real OHLCV providers (Alpaca/Gemini + yfinance)
- Brokers (Alpaca paper, Gemini sandbox)
- Risk/metrics/portfolio stubs
- Render blueprint (`render.yaml`)

## Deploy (Render → Blueprint)
1. Push this repo to GitHub.
2. In Render: New → Blueprint → pick the repo (auto-detects `render.yaml`).
3. Add env vars to **both** services (web + worker):
   - `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_BASE_URL=https://paper-api.alpaca.markets`
   - `GEMINI_API_KEY`, `GEMINI_API_SECRET`, `GEMINI_BASE_URL=https://api.sandbox.gemini.com`
4. Deploy. Test `GET /api/health/`.

## Paper worker
`workers/paper_trader.py` reads `config/strategies.yaml`, pulls data, generates signals, and submits **paper** orders via the execution router.
