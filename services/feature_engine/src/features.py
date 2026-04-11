from __future__ import annotations


def compute_feature_snapshot(rows: list[dict]) -> dict:
    closes = [r["close"] for r in rows]
    highs = [r["high"] for r in rows]
    lows = [r["low"] for r in rows]
    vols = [r["volume"] for r in rows]

    def pct(a: float, b: float) -> float:
        return 0.0 if b == 0 else (a / b) - 1

    ret_1 = pct(closes[-1], closes[-2]) if len(closes) > 1 else 0.0
    ret_5 = pct(closes[-1], closes[-6]) if len(closes) > 5 else 0.0

    window = min(20, len(closes))
    mean = sum(closes[-window:]) / window
    var = sum((x - mean) ** 2 for x in closes[-window:]) / window
    std = var ** 0.5

    atr_window = min(14, len(highs))
    atr = sum((highs[-i] - lows[-i]) for i in range(1, atr_window + 1)) / atr_window

    cum_pv = 0.0
    cum_v = 0.0
    for c, v in zip(closes, vols):
        cum_pv += c * v
        cum_v += v
    vwap = closes[-1] if cum_v == 0 else cum_pv / cum_v

    vol20 = std
    mom10 = pct(closes[-1], closes[-10]) if len(closes) >= 10 else 0.0
    breakout = closes[-1] - max(closes[-20:]) if len(closes) >= 20 else 0.0
    vol_exp = vols[-1] / (sum(vols[-window:]) / window)
    rv_window = min(50, len(vols))
    rel_vol = vols[-1] / (sum(vols[-rv_window:]) / rv_window)

    return {
        "ret_1": ret_1,
        "ret_5": ret_5,
        "rolling_vol_20": vol20,
        "atr_14": atr,
        "vwap_distance": 0.0 if closes[-1] == 0 else (closes[-1] - vwap) / closes[-1],
        "zscore_20": 0.0 if std == 0 else (closes[-1] - mean) / std,
        "momentum_10": mom10,
        "breakout_distance_20": breakout,
        "volume_expansion": vol_exp,
        "relative_volume": rel_vol,
    }
