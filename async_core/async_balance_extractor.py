import asyncio
import yfinance as yf

from async_core.async_rate_limiter import (
    RATE_LIMITER
)

# =========================================================
# SAFE ASYNC BALANCE SHEET EXTRACTOR
# =========================================================

async def extract_balance_sheet_async(symbol):

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
            # BALANCE SHEET
            # =============================================

            balance = await asyncio.to_thread(
                lambda: ticker.balance_sheet
            )

            cash = 0

            debt = 0

            equity = 0

            total_assets = 0

            current_assets = 0

            current_liabilities = 0

            if not balance.empty:

                # =========================================
                # CASH
                # =========================================

                if "Cash And Cash Equivalents" in balance.index:

                    cash = balance.loc[
                        "Cash And Cash Equivalents"
                    ].iloc[0]

                # =========================================
                # TOTAL DEBT
                # =========================================

                if "Total Debt" in balance.index:

                    debt = balance.loc[
                        "Total Debt"
                    ].iloc[0]

                # =========================================
                # EQUITY
                # =========================================

                if "Stockholders Equity" in balance.index:

                    equity = balance.loc[
                        "Stockholders Equity"
                    ].iloc[0]

                # =========================================
                # TOTAL ASSETS
                # =========================================

                if "Total Assets" in balance.index:

                    total_assets = balance.loc[
                        "Total Assets"
                    ].iloc[0]

                # =========================================
                # CURRENT ASSETS
                # =========================================

                if "Current Assets" in balance.index:

                    current_assets = balance.loc[
                        "Current Assets"
                    ].iloc[0]

                # =========================================
                # CURRENT LIABILITIES
                # =========================================

                if "Current Liabilities" in balance.index:

                    current_liabilities = balance.loc[
                        "Current Liabilities"
                    ].iloc[0]

            # =============================================
            # FINAL OUTPUT
            # =============================================

            return {

                "Cash": cash,

                "Total Debt": debt,

                "Equity": equity,

                "Total Assets": total_assets,

                "Current Assets": current_assets,

                "Current Liabilities": current_liabilities
            }

        except Exception as e:

            print(
                f"Balance Sheet Error: "
                f"{symbol} | {e}"
            )

            return {}