import pandas as pd


def prepare_timeseries(df: pd.DataFrame, target_col: str = "Close") -> pd.Series:
    """
    Extrait la série temporelle cible (prix de clôture).
    Index aligné sur les dates (évite le décalage après dropna).
    """
    df = df.copy()
    if target_col not in df.columns:
        candidates = [c for c in df.columns if str(c).startswith("Close")]
        if candidates:
            target_col = candidates[0]

    df["date"] = pd.to_datetime(df["date"])
    ts = df.set_index("date")[target_col].dropna()
    return ts.sort_index()
