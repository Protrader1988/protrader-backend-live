import time
from data.providers.news_providers import fetch_headlines, simple_sentiment

def run_news_loop():
    tickers = ["AAPL", "MSFT", "BTC-USD", "ETH-USD"]
    print(f"[NEWS] Starting sentiment loop for {tickers}")
    
    while True:
        try:
            items = fetch_headlines(tickers)
            for it in items:
                sent = simple_sentiment(it.get("title", "") + " " + it.get("summary", ""))
                print(f"[NEWS] {it.get('ticker', 'N/A')}: {sent:.2f} | {it.get('title', '')[:60]}")
        except Exception as e:
            print(f"[NEWS ERROR] {e}")
        
        time.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    run_news_loop()
