import yfinance as yf
import pandas as pd
from datetime import datetime


def fetch_gold_prices(symbol: str = "GC=F", period: str = "5y") -> pd.DataFrame:
    """
    Récupère les prix de l'or (futures) via Yahoo Finance.
    symbol par défaut : GC=F (Gold Futures)
    """
    data = yf.download(symbol, period=period, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.reset_index()
    date_col = "Date" if "Date" in data.columns else data.columns[0]
    data.rename(columns={date_col: "date"}, inplace=True)
    return data
