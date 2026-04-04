import pandas as pd


def prepare_timeseries(df: pd.DataFrame, target_col: str = "Close") -> pd.Series:
    """
    Extrait la série temporelle cible (prix de clôture).
    """
    ts = df[target_col].dropna()
    ts.index = pd.to_datetime(df["date"])
    return ts
