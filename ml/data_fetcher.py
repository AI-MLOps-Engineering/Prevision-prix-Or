import yfinance as yf
import pandas as pd
from datetime import datetime


def fetch_gold_prices(symbol: str = "GC=F", period: str = "5y") -> pd.DataFrame:
    """
    Récupère les prix de l'or (futures) via Yahoo Finance.
    symbol par défaut : GC=F (Gold Futures)
    """
    data = yf.download(symbol, period=period)
    data = data.reset_index()
    data.rename(columns={"Date": "date"}, inplace=True)
    return data
