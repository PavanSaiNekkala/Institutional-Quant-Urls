from core.multi_source_market_engine import (
    fetch_market_data
)

# =========================================================
# MARKET EXTRACTOR
# =========================================================

def extract_market_data(ticker):

    try:

        symbol = ticker.ticker

        market_data = fetch_market_data(
            symbol
        )

        return market_data

    except:

        return {}