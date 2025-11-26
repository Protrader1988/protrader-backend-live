from flask import Blueprint, jsonify
bp = Blueprint("health", __name__)

@bp.get("/")
def ok():
    return jsonify({"ok": True})
