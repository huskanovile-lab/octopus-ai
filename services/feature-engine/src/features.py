from __future__ import annotations

import numpy as np
import pandas as pd


def compute_feature_snapshot(df: pd.DataFrame) -> pd.Series:
    c = df["close"]
    v = df["volume"]
    high = df["high"]
    low = df["low"]

    returns = c.pct_change().fillna(0)
    rolling_vol = returns.rolling(20).std().iloc[-1]
    atr = (high - low).rolling(14).mean().iloc[-1]
    vwap = (c * v).cumsum() / v.cumsum().replace(0, np.nan)

    out = pd.Series(
        {
            "ret_1": returns.iloc[-1],
            "ret_5": c.pct_change(5).iloc[-1],
            "rolling_vol_20": rolling_vol,
            "atr_14": atr,
            "vwap_distance": (c.iloc[-1] - vwap.iloc[-1]) / c.iloc[-1],
            "zscore_20": (c.iloc[-1] - c.rolling(20).mean().iloc[-1]) / (c.rolling(20).std().iloc[-1] + 1e-9),
            "momentum_10": c.iloc[-1] / c.iloc[-10] - 1 if len(c) >= 10 else 0,
            "breakout_distance_20": c.iloc[-1] - high.rolling(20).max().iloc[-1],
            "volume_expansion": v.iloc[-1] / (v.rolling(20).mean().iloc[-1] + 1e-9),
            "relative_volume": v.iloc[-1] / (v.rolling(50).mean().iloc[-1] + 1e-9),
        }
    )
    return out.replace([np.inf, -np.inf], 0).fillna(0)
