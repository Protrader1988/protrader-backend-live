def load_strategy(name: str, params: dict):
    if name == "wick_master_pro":
        from strategies.wick_master_pro import WickMasterPro
        return WickMasterPro(**params)
    raise ValueError(f"Unknown strategy: {name}")
