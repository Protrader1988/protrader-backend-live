from flask import Blueprint, request, jsonify
bp = Blueprint("screener", __name__)

@bp.get("/recommendations")
def recommendations():
    bot = request.args.get("bot", "wickmaster")
    universe = request.args.get("universe","AAPL,MSFT,ETH/USD,BTC/USD").split(",")
    out = []
    for sym in [s.strip() for s in universe if s.strip()]:
        a_type = "crypto" if "/" in sym else "stock"
        why = "Above MA with rising volume" if a_type=="stock" else "Higher highs on 4h momentum"
        out.append({"symbol": sym, "asset_type": a_type, "why": why})
    return jsonify({"bot": bot, "candidates": out})
