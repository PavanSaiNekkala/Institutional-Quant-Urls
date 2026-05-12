import yfinance as yf
import numpy as np

def extract_market_data(symbol):

    try:

        ticker = yf.Ticker(symbol)

        fast = ticker.fast_info

        return {

            "Current Price": fast.get("lastPrice", np.nan),

            "Market Cap": fast.get("marketCap", np.nan),

            "Day High": fast.get("dayHigh", np.nan),

            "Day Low": fast.get("dayLow", np.nan),

            "52W High": fast.get("yearHigh", np.nan),

            "52W Low": fast.get("yearLow", np.nan),

            "Volume": fast.get("lastVolume", np.nan),

            "Avg Volume": fast.get("tenDayAverageVolume", np.nan)

        }

    except Exception as e:

        return {
            "Market Error": str(e)
        }
