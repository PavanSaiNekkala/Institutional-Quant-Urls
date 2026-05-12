import ray
import yfinance as yf

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

# =========================================================
# DISTRIBUTED STOCK PROCESSOR
# =========================================================

@ray.remote

def process_stock_distributed(symbol):

    try:

        ticker = yf.Ticker(symbol)

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

        combined_data = {

            **market_data,

            **financial_data,

            **balance_data,

            **cashflow_data,

            **technical_data
        }

        ai_scores = calculate_institutional_score(
            combined_data
        )

        quant_scores = calculate_quant_scores(
            combined_data
        )

        return {

            "Stock": symbol,

            **combined_data,

            **ai_scores,

            **quant_scores
        }

    except Exception as e:

        return {

            "Stock": symbol,

            "Error": str(e)
        }