# =========================================================
# IMPORTS
# =========================================================

import pandas as pd
import time
import traceback
import yfinance as yf
import multiprocessing
import duckdb

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from pathlib import Path

from utils.symbol_validator import validate_symbol

from utils.retry_engine import retry_request

from utils.cache_manager import (
    load_cache,
    save_cache
)

from utils.db_manager import get_connection

from utils.sector_mapper import (
    get_sector_data
)

from utils.failure_handler import (
    categorize_failure
)

from core.market_extractor import (
    extract_market_data
)

from core.financial_extractor import (
    extract_financials
)

from core.balance_extractor import (
    extract_balance_sheet
)

from core.cashflow_extractor import (
    extract_cashflow
)

from technicals.indicator_engine import (
    calculate_indicators
)

from ai.scoring_engine import (
    calculate_institutional_score
)

from analytics.quant_factor_engine import (
    calculate_quant_scores
)

from analytics.portfolio_engine import (
    build_portfolio
)

from ml.ml_prediction_engine import (

    train_ml_model,

    generate_predictions
)

from backtesting.backtest_engine import (
    run_backtest
)

# =========================================================
# CPU + WORKER CONFIG
# =========================================================

CPU_COUNT = multiprocessing.cpu_count()

MAX_WORKERS = 15

# =========================================================
# BATCH CONFIG
# =========================================================

BATCH_SIZE = 100

BATCH_SLEEP = 2

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

CACHE_DIR = (
    BASE_DIR
    / "cache"
)

DATABASE_DIR = (
    BASE_DIR
    / "database"
)

LOG_DIR = (
    BASE_DIR
    / "logs"
)

# =========================================================
# CREATE DIRECTORIES
# =========================================================

OUTPUT_DIR.mkdir(
    exist_ok=True
)

CACHE_DIR.mkdir(
    exist_ok=True
)

DATABASE_DIR.mkdir(
    exist_ok=True
)

LOG_DIR.mkdir(
    exist_ok=True
)

# =========================================================
# OUTPUT FILES
# =========================================================

OUTPUT_FILE = (
    OUTPUT_DIR
    / "enriched_stock_data.xlsx"
)

TEMP_PARQUET = (
    OUTPUT_DIR
    / "temp_results.parquet"
)

PORTFOLIO_FILE = (
    OUTPUT_DIR
    / "institutional_portfolio.xlsx"
)

BACKTEST_FILE = (
    OUTPUT_DIR
    / "backtest_results.xlsx"
)

FAILED_FILE = (
    OUTPUT_DIR
    / "failed_symbols.xlsx"
)

DB_FILE = (
    DATABASE_DIR
    / "institutional_quant.db"
)

# =========================================================
# START
# =========================================================

print("=" * 60)
print("LOADING DATASET...")
print("=" * 60)

# =========================================================
# LOAD INPUT
# =========================================================

df = pd.read_excel(
    INPUT_FILE
)

print(
    f"Total Stocks Loaded : "
    f"{len(df)}"
)

print(
    f"CPU Count : "
    f"{CPU_COUNT}"
)

print(
    f"Max Workers : "
    f"{MAX_WORKERS}"
)

# =========================================================
# LOAD CACHE
# =========================================================

cache_df = load_cache()

processed_symbols = set()

if not cache_df.empty:

    processed_symbols = set(

        cache_df[
            "Stock"
        ].astype(str)
    )

print(
    f"Cached Stocks : "
    f"{len(processed_symbols)}"
)

# =========================================================
# DATABASE
# =========================================================

conn = get_connection()

print("DuckDB Connected")

# =========================================================
# STORAGE
# =========================================================

results = []

failed = []

success_count = 0

failure_count = 0

skipped_count = 0

# =========================================================
# CHUNK GENERATOR
# =========================================================

def chunk_dataframe(
    dataframe,
    chunk_size
):

    for i in range(
        0,
        len(dataframe),
        chunk_size
    ):

        yield dataframe.iloc[
            i:i + chunk_size
        ]

# =========================================================
# PROCESS STOCK
# =========================================================

def process_stock(row):

    stock = "UNKNOWN"

    try:

        stock = str(
            row["Stock"]
        ).strip()

        # =================================================
        # CACHE SKIP
        # =================================================

        if stock in processed_symbols:

            return {
                "status": "SKIPPED",
                "data": {
                    "Stock": stock
                }
            }

        print(
            f"Processing : {stock}"
        )

        # =================================================
        # VALIDATION
        # =================================================

        validation = validate_symbol(
            stock
        )

        if validation["valid"] is False:

            return {

                "status": "FAILED",

                "data": {

                    "Stock": stock,

                    "Reason": "INVALID_SYMBOL"
                }
            }

        symbol = validation["symbol"]

        # =================================================
        # TICKER
        # =================================================

        ticker = retry_request(
            lambda: yf.Ticker(symbol)
        )

        # =================================================
        # EXTRACTION
        # =================================================

        market_data = extract_market_data(
            ticker
        )

        financial_data = extract_financials(
            ticker
        )

        balance_data = extract_balance_sheet(
            ticker
        )

        cashflow_data = extract_cashflow(
            ticker
        )

        technical_data = calculate_indicators(
            ticker
        )

        sector_data = get_sector_data(
            stock
        )

        # =================================================
        # COMBINED DATA
        # =================================================

        combined_data = {

            **market_data,

            **financial_data,

            **balance_data,

            **cashflow_data,

            **technical_data
        }

        # =================================================
        # AI SCORE
        # =================================================

        ai_scores = calculate_institutional_score(
            combined_data
        )

        # =================================================
        # QUANT SCORE
        # =================================================

        quant_scores = calculate_quant_scores(
            combined_data
        )

        # =================================================
        # FINAL RECORD
        # =================================================

        final_record = {

            "Stock": stock,

            "Validated Symbol": symbol,

            **market_data,

            **financial_data,

            **balance_data,

            **cashflow_data,

            **technical_data,

            **sector_data,

            **ai_scores,

            **quant_scores
        }

        return {

            "status": "SUCCESS",

            "data": final_record
        }

    except Exception as e:

        return {

            "status": "FAILED",

            "data": {

                "Stock": stock,

                "Reason": categorize_failure(e),

                "Error": str(e)
            }
        }

# =========================================================
# START TIMER
# =========================================================

start_time = time.time()

# =========================================================
# PROCESSING START
# =========================================================

print("=" * 60)
print("STARTING PROCESSING...")
print("=" * 60)

batches = list(

    chunk_dataframe(
        df,
        BATCH_SIZE
    )
)

total_batches = len(batches)

print(
    f"Total Batches : "
    f"{total_batches}"
)

# =========================================================
# BATCH LOOP
# =========================================================

for batch_num, batch_df in enumerate(
    batches,
    start=1
):

    print("=" * 60)

    print(
        f"PROCESSING BATCH "
        f"{batch_num}/{total_batches}"
    )

    print("=" * 60)

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [

            executor.submit(
                process_stock,
                row
            )

            for _, row in batch_df.iterrows()
        ]

        for future in as_completed(futures):

            try:

                result = future.result()

                if result["status"] == "SUCCESS":

                    results.append(
                        result["data"]
                    )

                    success_count += 1

                    print(
                        f"SUCCESS : "
                        f"{success_count}"
                    )

                elif result["status"] == "FAILED":

                    failed.append(
                        result["data"]
                    )

                    failure_count += 1

                    print(
                        f"FAILED : "
                        f"{failure_count}"
                    )

                elif result["status"] == "SKIPPED":

                    skipped_count += 1

                    print(
                        f"SKIPPED : "
                        f"{skipped_count}"
                    )

            except Exception as e:

                failed.append({

                    "Stock": "UNKNOWN",

                    "Reason":
                    "THREAD_ERROR",

                    "Error": str(e)
                })

    # =====================================================
    # TEMP SAVE
    # =====================================================

    temp_df = pd.DataFrame(
        results
    )

    temp_df.to_parquet(
        TEMP_PARQUET
    )

    print(
        f"Emergency Save Complete : "
        f"{TEMP_PARQUET}"
    )

    print(
        f"Sleeping {BATCH_SLEEP} sec..."
    )

    time.sleep(
        BATCH_SLEEP
    )

# =========================================================
# DATAFRAMES
# =========================================================

results_df = pd.DataFrame(
    results
)

failed_df = pd.DataFrame(
    failed
)

# =========================================================
# CACHE MERGE
# =========================================================

if not cache_df.empty:

    final_cache_df = pd.concat(

        [
            cache_df,
            results_df
        ],

        ignore_index=True
    )

    final_cache_df = (

        final_cache_df
        .drop_duplicates(
            subset=["Stock"]
        )
    )

else:

    final_cache_df = results_df.copy()

# =========================================================
# ML MODEL
# =========================================================

print("=" * 60)
print("TRAINING ML MODEL...")
print("=" * 60)

ml_model, ml_accuracy = train_ml_model(
    final_cache_df
)

print(
    f"ML Accuracy : "
    f"{ml_accuracy}%"
)

if ml_model is not None:

    final_cache_df = generate_predictions(

        ml_model,

        final_cache_df
    )

# =========================================================
# BUILD PORTFOLIO
# =========================================================

portfolio_df = build_portfolio(
    final_cache_df
)

# =========================================================
# RUN BACKTEST
# =========================================================

print("=" * 60)
print("RUNNING BACKTEST...")
print("=" * 60)

backtest_results = run_backtest(
    portfolio_df
)

if backtest_results is not None:

    print("=" * 60)

    print("BACKTEST RESULTS")

    print("=" * 60)

    print(
        f"CAGR : "
        f"{backtest_results['CAGR']}%"
    )

    print(
        f"Sharpe Ratio : "
        f"{backtest_results['Sharpe Ratio']}"
    )

    print(
        f"Max Drawdown : "
        f"{backtest_results['Max Drawdown']}%"
    )

    print(
        f"Volatility : "
        f"{backtest_results['Volatility']}%"
    )

    print(
        f"Win Rate : "
        f"{backtest_results['Win Rate']}%"
    )

# =========================================================
# SAVE DATABASE
# =========================================================

print("=" * 60)
print("SAVING TO DUCKDB...")
print("=" * 60)

conn.register(
    "final_cache_df",
    final_cache_df
)

conn.execute(
    '''
    CREATE OR REPLACE TABLE
    enriched_stocks AS

    SELECT *
    FROM final_cache_df
    '''
)

conn.register(
    "portfolio_df",
    portfolio_df
)

conn.execute(
    '''
    CREATE OR REPLACE TABLE
    institutional_portfolio AS

    SELECT *
    FROM portfolio_df
    '''
)

# =========================================================
# EXPORT BACKTEST
# =========================================================

if backtest_results is not None:

    backtest_df = pd.DataFrame([{

        "CAGR":
        backtest_results["CAGR"],

        "Sharpe Ratio":
        backtest_results[
            "Sharpe Ratio"
        ],

        "Max Drawdown":
        backtest_results[
            "Max Drawdown"
        ],

        "Volatility":
        backtest_results[
            "Volatility"
        ],

        "Win Rate":
        backtest_results[
            "Win Rate"
        ]
    }])

    backtest_df.to_excel(

        BACKTEST_FILE,

        index=False
    )

# =========================================================
# EXPORT FILES
# =========================================================

portfolio_df.to_excel(

    PORTFOLIO_FILE,

    index=False
)

failed_df.to_excel(

    FAILED_FILE,

    index=False
)

with pd.ExcelWriter(

    OUTPUT_FILE,

    engine="openpyxl"

) as writer:

    final_cache_df.to_excel(

        writer,

        sheet_name="Enriched Data",

        index=False
    )

    failed_df.to_excel(

        writer,

        sheet_name="Failed Symbols",

        index=False
    )

# =========================================================
# SAVE CACHE
# =========================================================

save_cache(
    final_cache_df
)

# =========================================================
# CLOSE DB
# =========================================================

conn.close()

# =========================================================
# FINAL SUMMARY
# =========================================================

elapsed = round(
    time.time() - start_time,
    2
)

print("=" * 60)

print("PROCESS COMPLETED")

print(
    f"Successful Stocks : "
    f"{len(results_df)}"
)

print(
    f"Failed Stocks : "
    f"{len(failed_df)}"
)

print(
    f"Skipped Stocks : "
    f"{skipped_count}"
)

print(
    f"Execution Time : "
    f"{elapsed} sec"
)

print(
    f"Output File : "
    f"{OUTPUT_FILE}"
)

print(
    f"Portfolio File : "
    f"{PORTFOLIO_FILE}"
)

print(
    f"Backtest File : "
    f"{BACKTEST_FILE}"
)

print("=" * 60)