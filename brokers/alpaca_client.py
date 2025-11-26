import os, requests
ALPACA_KEY = os.getenv("ALPACA_API_KEY","")
ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY","")
ALPACA_BASE = os.getenv("ALPACA_BASE_URL","https://paper-api.alpaca.markets")

class AlpacaClient:
    def __init__(self): 
        self.sess = requests.Session()
        self.sess.headers.update({"APCA-API-KEY-ID":ALPACA_KEY,"APCA-API-SECRET-KEY":ALPACA_SECRET})
    def submit_order(self, side, symbol, qty, order_type="market", tif="gtc", limit_price=None, stop_price=None):
        url = f"{ALPACA_BASE}/v2/orders"
        body = {"symbol":symbol.upper(),"qty":str(qty),"side":side,"type":order_type,"time_in_force":tif}
        if limit_price: body["limit_price"]=str(limit_price)
        if stop_price: body["stop_price"]=str(stop_price)
        r = self.sess.post(url, json=body, timeout=15)
        try:
            resp = r.json()
        except Exception:
            resp = {"text": r.text}
        return {"ok": r.ok, "status": r.status_code, "resp": resp}
