import asyncio
import yfinance as yf

from async_core.async_rate_limiter import (
    RATE_LIMITER
)

# =========================================================
# SAFE ASYNC MARKET EXTRACTOR
# =========================================================

async def extract_market_data_async(symbol):

    async with RATE_LIMITER:

        try:

            await asyncio.sleep(0.5)

            ticker = yf.Ticker(symbol)

            info = await asyncio.to_thread(
                lambda: ticker.info
            )

            return {

                "Market Cap": info.get(
                    "marketCap",
                    0
                ),

                "Current Price": info.get(
                    "currentPrice",
                    0
                ),

                "52 Week High": info.get(
                    "fiftyTwoWeekHigh",
                    0
                ),

                "52 Week Low": info.get(
                    "fiftyTwoWeekLow",
                    0
                ),

                "Volume": info.get(
                    "volume",
                    0
                )
            }

        except Exception as e:

            print(
                f"Market Error: {symbol} | {e}"
            )

            return {}