from pathlib import Path
import pandas as pd

CACHE_DIR = Path("cache")

CACHE_DIR.mkdir(exist_ok=True)

CACHE_FILE = CACHE_DIR / "processed.parquet"

def load_cache():

    if CACHE_FILE.exists():

        return pd.read_parquet(CACHE_FILE)

    return pd.DataFrame()

def save_cache(df):

    df.to_parquet(CACHE_FILE)