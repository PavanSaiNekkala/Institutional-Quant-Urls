import pandas as pd
import ray
import polars as pl
import duckdb
import time

from pathlib import Path

from distributed.ray_engine import (

    initialize_ray,

    shutdown_ray
)

from distributed.distributed_processor import (
    process_stock_distributed
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR
    / "input"
    / "yfinance_stock_urls.xlsx"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
)

DATABASE_DIR = (
    BASE_DIR
    / "database"
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)

DATABASE_DIR.mkdir(
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "distributed_results.parquet"
)

DB_FILE = (
    DATABASE_DIR
    / "institutional_quant.db"
)

# =========================================================
# INITIALIZE RAY
# =========================================================

initialize_ray()

# =========================================================
# LOAD INPUT
# =========================================================

print("=" * 60)
print("LOADING INPUT...")
print("=" * 60)

df = pd.read_excel(INPUT_FILE)

stocks = (
    df["Stock"]
    .dropna()
    .astype(str)
    .tolist()
)

print(f"Total Stocks : {len(stocks)}")

# =========================================================
# START TIMER
# =========================================================

start = time.time()

# =========================================================
# DISTRIBUTED TASKS
# =========================================================

tasks = [

    process_stock_distributed.remote(
        stock
    )

    for stock in stocks
]

# =========================================================
# EXECUTE TASKS
# =========================================================

results = ray.get(tasks)

# =========================================================
# POLARS DATAFRAME
# =========================================================

pl_df = pl.DataFrame(results)

# =========================================================
# SAVE PARQUET
# =========================================================

pl_df.write_parquet(
    OUTPUT_FILE
)

# =========================================================
# DUCKDB SAVE
# =========================================================

conn = duckdb.connect(
    str(DB_FILE)
)

pd_df = pl_df.to_pandas()

conn.register(
    "pd_df",
    pd_df
)

conn.execute(
    '''
    CREATE OR REPLACE TABLE
    distributed_stocks AS

    SELECT *
    FROM pd_df
    '''
)

conn.close()

# =========================================================
# SHUTDOWN RAY
# =========================================================

shutdown_ray()

# =========================================================
# SUMMARY
# =========================================================

elapsed = round(
    time.time() - start,
    2
)

print("=" * 60)

print("DISTRIBUTED PROCESSING COMPLETED")

print(
    f"Processed Stocks : "
    f"{len(pd_df)}"
)

print(
    f"Execution Time : "
    f"{elapsed} sec"
)

print(
    f"Output File : "
    f"{OUTPUT_FILE}"
)

print("=" * 60)