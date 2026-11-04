import pandas as pd
from .config import REQUIRED

def load_prices(path):
    """Load course-provided adjusted close matrix; never download or synthesize live data."""
    df = pd.read_csv(path)
    df.columns = df.columns.str.replace('\\','',regex=False).str.strip()
    if 'Date' not in df.columns:
        raise ValueError('CSV requires a Date column')
    missing = sorted(set(REQUIRED)-set(df.columns))
    if missing:
        raise ValueError(f'Missing required ETF columns: {missing}')
    df['Date'] = pd.to_datetime(df['Date'], errors='raise')
    if df['Date'].duplicated().any():
        raise ValueError('Duplicate trading dates in input CSV')
    df = df.set_index('Date').sort_index()
    df = df.loc[:,list(REQUIRED)].apply(pd.to_numeric, errors='coerce')
    df = df.where(df > 0)
    if df.empty:
        raise ValueError('No rows in input data')
    return df

def returns_from_prices(prices):
    return prices.pct_change(fill_method=None)
