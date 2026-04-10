from services.feature_engine.src.features import compute_feature_snapshot


def test_compute_feature_snapshot_has_expected_fields():
    rows = [
        {"open": 100 + i, "high": 101 + i, "low": 99 + i, "close": 100 + i, "volume": 1000 + i * 10}
        for i in range(60)
    ]
    out = compute_feature_snapshot(rows)
    for k in ["ret_1", "rolling_vol_20", "atr_14", "vwap_distance", "zscore_20", "relative_volume"]:
        assert k in out
