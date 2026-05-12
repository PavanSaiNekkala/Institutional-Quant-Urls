import asyncio
import yfinance as yf

from async_core.async_rate_limiter import (
    RATE_LIMITER
)

# =========================================================
# SAFE ASYNC FINANCIAL EXTRACTOR
# =========================================================

async def extract_financials_async(symbol):

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
            # FINANCIALS
            # =============================================

            financials = await asyncio.to_thread(
                lambda: ticker.financials
            )

            revenue = 0

            net_income = 0

            operating_income = 0

            ebitda = 0

            gross_profit = 0

            if not financials.empty:

                # =========================================
                # TOTAL REVENUE
                # =========================================

                if "Total Revenue" in financials.index:

                    revenue = financials.loc[
                        "Total Revenue"
                    ].iloc[0]

                # =========================================
                # NET INCOME
                # =========================================

                if "Net Income" in financials.index:

                    net_income = financials.loc[
                        "Net Income"
                    ].iloc[0]

                # =========================================
                # OPERATING INCOME
                # =========================================

                if "Operating Income" in financials.index:

                    operating_income = financials.loc[
                        "Operating Income"
                    ].iloc[0]

                # =========================================
                # EBITDA
                # =========================================

                if "EBITDA" in financials.index:

                    ebitda = financials.loc[
                        "EBITDA"
                    ].iloc[0]

                # =========================================
                # GROSS PROFIT
                # =========================================

                if "Gross Profit" in financials.index:

                    gross_profit = financials.loc[
                        "Gross Profit"
                    ].iloc[0]

            # =============================================
            # FINAL OUTPUT
            # =============================================

            return {

                "Revenue": revenue,

                "Net Income": net_income,

                "Operating Income": operating_income,

                "EBITDA": ebitda,

                "Gross Profit": gross_profit
            }

        except Exception as e:

            print(
                f"Financial Error: "
                f"{symbol} | {e}"
            )

            return {}