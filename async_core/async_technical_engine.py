import asyncio
import yfinance as yf
import pandas as pd
import pandas_ta as ta

from async_core.async_rate_limiter import (
    RATE_LIMITER
)

# =========================================================
# SAFE ASYNC ADVANCED TECHNICAL ENGINE
# =========================================================

async def calculate_indicators_async(symbol):

    async with RATE_LIMITER:

        try:

            # =============================================
            # SAFE DELAY
            # =============================================

            await asyncio.sleep(0.5)

            # =============================================
            # TICKER
            # =============================================

            ticker = yf.Ticker(symbol)

            # =============================================
            # HISTORICAL DATA
            # =============================================

            hist = await asyncio.to_thread(

                lambda: ticker.history(
                    period="1y"
                )
            )

            if hist.empty:

                return {}

            # =============================================
            # PRICE SERIES
            # =============================================

            close = hist["Close"]

            high = hist["High"]

            low = hist["Low"]

            volume = hist["Volume"]

            # =============================================
            # SMA
            # =============================================

            sma50 = ta.sma(
                close,
                length=50
            ).iloc[-1]

            sma200 = ta.sma(
                close,
                length=200
            ).iloc[-1]

            # =============================================
            # RSI
            # =============================================

            rsi = ta.rsi(
                close,
                length=14
            ).iloc[-1]

            # =============================================
            # MACD
            # =============================================

            macd_df = ta.macd(close)

            macd = macd_df[
                "MACD_12_26_9"
            ].iloc[-1]

            macd_signal = macd_df[
                "MACDs_12_26_9"
            ].iloc[-1]

            # =============================================
            # BOLLINGER BANDS
            # =============================================

            bbands = ta.bbands(close)

            bb_upper = bbands[
                "BBU_5_2.0"
            ].iloc[-1]

            bb_lower = bbands[
                "BBL_5_2.0"
            ].iloc[-1]

            # =============================================
            # ATR
            # =============================================

            atr = ta.atr(
                high,
                low,
                close,
                length=14
            ).iloc[-1]

            # =============================================
            # VWAP
            # =============================================

            vwap = ta.vwap(
                high,
                low,
                close,
                volume
            ).iloc[-1]

            # =============================================
            # ADX
            # =============================================

            adx_df = ta.adx(
                high,
                low,
                close
            )

            adx = adx_df[
                "ADX_14"
            ].iloc[-1]

            # =============================================
            # STOCH RSI
            # =============================================

            stoch_rsi = ta.stochrsi(
                close
            )

            stoch_rsi_value = stoch_rsi[
                "STOCHRSIk_14_14_3_3"
            ].iloc[-1]

            # =============================================
            # VOLATILITY SCORE
            # =============================================

            volatility_score = min(
                atr * 10,
                100
            )

            # =============================================
            # FINAL OUTPUT
            # =============================================

            return {

                "SMA50": round(
                    sma50,
                    2
                ),

                "SMA200": round(
                    sma200,
                    2
                ),

                "RSI": round(
                    rsi,
                    2
                ),

                "MACD": round(
                    macd,
                    2
                ),

                "MACD Signal": round(
                    macd_signal,
                    2
                ),

                "BB Upper": round(
                    bb_upper,
                    2
                ),

                "BB Lower": round(
                    bb_lower,
                    2
                ),

                "ATR": round(
                    atr,
                    2
                ),

                "VWAP": round(
                    vwap,
                    2
                ),

                "ADX": round(
                    adx,
                    2
                ),

                "Stoch RSI": round(
                    stoch_rsi_value,
                    2
                ),

                "Volatility Score": round(
                    volatility_score,
                    2
                )
            }

        except Exception as e:

            print(
                f"Technical Error: "
                f"{symbol} | {e}"
            )

            return {}