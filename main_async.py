# =========================================================
# IMPORTS
# =========================================================

import asyncio
import pandas as pd
import time
import duckdb

from pathlib import Path

from async_core.async_market_extractor import (
    extract_market_data_async
)

from async_core.async_financial_extractor import (
    extract_financials_async
)

from async_core.async_balance_extractor import (
    extract_balance_sheet_async
)

from async_core.async_technical_engine import (
    calculate_indicators_async
)

from analytics.quant_factor_engine import (
    calculate_quant_scores
)

from ai.scoring_engine import (
    calculate_institutional_score
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
# CONFIG
# =========================================================

BATCH_SIZE = 100

BATCH_SLEEP = 3

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
    / "async_enriched_data.xlsx"
)

PORTFOLIO_FILE = (
    OUTPUT_DIR
    / "async_portfolio.xlsx"
)

ML_FILE = (
    OUTPUT_DIR
    / "async_ml_predictions.xlsx"
)

TECHNICAL_FILE = (
    OUTPUT_DIR
    / "async_technical_leaders.xlsx"
)

BACKTEST_FILE = (
    OUTPUT_DIR
    / "async_backtest_results.xlsx"
)

DB_FILE = (
    DATABASE_DIR
    / "institutional_quant.db"
)

# =========================================================
# LOAD DATA
# =========================================================

print("=" * 60)
print("LOADING INPUT DATA...")
print("=" * 60)

df = pd.read_excel(INPUT_FILE)

stocks = (
    df["Stock"]
    .dropna()
    .astype(str)
    .tolist()
)

print(f"Total Stocks Loaded : {len(stocks)}")

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = duckdb.connect(
    str(DB_FILE)
)

# =========================================================
# PROCESS SINGLE STOCK
# =========================================================

async def process_stock(symbol):

    try:

        # =================================================
        # MARKET DATA
        # =================================================

        market_data = await extract_market_data_async(
            symbol
        )

        # =================================================
        # FINANCIALS
        # =================================================

        financial_data = await extract_financials_async(
            symbol
        )

        # =================================================
        # BALANCE SHEET
        # =================================================

        balance_data = await extract_balance_sheet_async(
            symbol
        )

        # =================================================
        # TECHNICALS
        # =================================================

        technical_data = await calculate_indicators_async(
            symbol
        )

        # =================================================
        # COMBINED DATA
        # =================================================

        combined_data = {

            **market_data,

            **financial_data,

            **balance_data,

            **technical_data
        }

        # =================================================
        # AI INSTITUTIONAL SCORE
        # =================================================

        ai_scores = calculate_institutional_score(
            combined_data
        )

        # =================================================
        # QUANT FACTORS
        # =================================================

        quant_scores = calculate_quant_scores(
            combined_data
        )

        # =================================================
        # FINAL RECORD
        # =================================================

        final_record = {

            "Stock": symbol,

            **market_data,

            **financial_data,

            **balance_data,

            **technical_data,

            **ai_scores,

            **quant_scores
        }

        print(
            f"Completed : {symbol}"
        )

        return final_record

    except Exception as e:

        print(
            f"Failed : {symbol} | {e}"
        )

        return None

# =========================================================
# MAIN ASYNC RUNNER
# =========================================================

async def main():

    start = time.time()

    all_results = []

    total_batches = (

        len(stocks) // BATCH_SIZE
    ) + 1

    print("=" * 60)
    print("STARTING ASYNC PROCESSING...")
    print("=" * 60)

    # =====================================================
    # PROCESS BATCHES
    # =====================================================

    for i in range(
        0,
        len(stocks),
        BATCH_SIZE
    ):

        batch_number = (
            i // BATCH_SIZE
        ) + 1

        batch = stocks[
            i:i + BATCH_SIZE
        ]

        print("=" * 60)

        print(
            f"PROCESSING BATCH "
            f"{batch_number}/"
            f"{total_batches}"
        )

        print("=" * 60)

        tasks = [

            process_stock(stock)

            for stock in batch
        ]

        batch_results = await asyncio.gather(
            *tasks
        )

        batch_results = [

            result

            for result in batch_results

            if result is not None
        ]

        all_results.extend(
            batch_results
        )

        print(
            f"Batch Completed : "
            f"{batch_number}"
        )

        print(
            f"Current Total : "
            f"{len(all_results)}"
        )

        # =================================================
        # SAFE COOL DOWN
        # =================================================

        await asyncio.sleep(
            BATCH_SLEEP
        )

    # =====================================================
    # DATAFRAME
    # =====================================================

    results_df = pd.DataFrame(
        all_results
    )

    # =====================================================
    # ML ENGINE
    # =====================================================

    print("=" * 60)
    print("TRAINING ML MODEL...")
    print("=" * 60)

    ml_model, ml_accuracy = train_ml_model(
        results_df
    )

    print(
        f"ML Accuracy : "
        f"{ml_accuracy}%"
    )

    if ml_model is not None:

        results_df = generate_predictions(

            ml_model,

            results_df
        )

        print(
            "ML Predictions Generated"
        )

    # =====================================================
    # BUILD PORTFOLIO
    # =====================================================

    portfolio_df = build_portfolio(
        results_df
    )

    # =====================================================
    # RUN BACKTEST
    # =====================================================

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

    # =====================================================
    # TECHNICAL LEADERS
    # =====================================================

    technical_leaders = results_df[

        (results_df["RSI"] > 60)

        &

        (results_df["MACD"] > 0)

        &

        (results_df["ADX"] > 25)

    ].sort_values(

        by="Alpha Score",

        ascending=False

    ).head(20)

    # =====================================================
    # ML LEADERS
    # =====================================================

    if "Buy Probability" in results_df.columns:

        ml_leaders = results_df.sort_values(

            by="Buy Probability",

            ascending=False

        ).head(20)

    else:

        ml_leaders = pd.DataFrame()

    # =====================================================
    # SAVE TO DUCKDB
    # =====================================================

    print("=" * 60)
    print("SAVING TO DATABASE...")
    print("=" * 60)

    conn.register(
        "results_df",
        results_df
    )

    conn.execute(
        '''
        CREATE OR REPLACE TABLE
        enriched_stocks AS

        SELECT *
        FROM results_df
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

    # =====================================================
    # EXPORT BACKTEST RESULTS
    # =====================================================

    if backtest_results is not None:

        backtest_df = pd.DataFrame([{

            "CAGR": backtest_results["CAGR"],

            "Sharpe Ratio": backtest_results[
                "Sharpe Ratio"
            ],

            "Max Drawdown": backtest_results[
                "Max Drawdown"
            ],

            "Volatility": backtest_results[
                "Volatility"
            ],

            "Win Rate": backtest_results[
                "Win Rate"
            ]
        }])

        backtest_df.to_excel(
            BACKTEST_FILE,
            index=False
        )

    # =====================================================
    # EXPORT EXCEL FILES
    # =====================================================

    results_df.to_excel(
        OUTPUT_FILE,
        index=False
    )

    portfolio_df.to_excel(
        PORTFOLIO_FILE,
        index=False
    )

    ml_leaders.to_excel(
        ML_FILE,
        index=False
    )

    technical_leaders.to_excel(
        TECHNICAL_FILE,
        index=False
    )

    # =====================================================
    # CLOSE DB
    # =====================================================

    conn.close()

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    elapsed = round(
        time.time() - start,
        2
    )

    print("=" * 60)

    print("ASYNC PROCESS COMPLETED")

    print(
        f"Processed Stocks : "
        f"{len(results_df)}"
    )

    print(
        f"ML Accuracy : "
        f"{ml_accuracy}%"
    )

    print(
        f"Execution Time : "
        f"{elapsed} sec"
    )

    print(
        f"Main Output : "
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

    print(
        f"ML Leaders File : "
        f"{ML_FILE}"
    )

    print(
        f"Technical Leaders File : "
        f"{TECHNICAL_FILE}"
    )

    print("=" * 60)

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())