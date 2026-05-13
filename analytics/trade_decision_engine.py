# =========================================================
# IMPORTS
# =========================================================

import pandas as pd
import numpy as np
import yfinance as yf

# =========================================================
# SAFE NUMERIC
# =========================================================

def safe_numeric(series):

    return pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

# =========================================================
# LIVE PRICE FETCHER
# =========================================================

def get_live_market_data(symbol):

    try:

        stock = yf.Ticker(symbol)

        # =================================================
        # FAST LIVE PRICE
        # =================================================

        live_price = stock.fast_info.get(
            "lastPrice",
            None
        )

        # =================================================
        # HISTORICAL DATA
        # =================================================

        hist = stock.history(
            period="3mo",
            interval="1d",
            auto_adjust=True
        )

        if hist.empty:

            return {

                "current_price": live_price or 0,

                "ret_5d": 0,

                "ret_20d": 0,

                "volume_ratio": 1
            }

        # =================================================
        # CURRENT PRICE
        # =================================================

        if live_price is None:

            live_price = float(
                hist["Close"].iloc[-1]
            )

        # =================================================
        # MOMENTUM
        # =================================================

        ret_5d = 0
        ret_20d = 0

        if len(hist) >= 6:

            ret_5d = (

                (
                    hist["Close"].iloc[-1]

                    /

                    hist["Close"].iloc[-6]
                ) - 1

            ) * 100

        if len(hist) >= 21:

            ret_20d = (

                (
                    hist["Close"].iloc[-1]

                    /

                    hist["Close"].iloc[-21]
                ) - 1

            ) * 100

        # =================================================
        # VOLUME RATIO
        # =================================================

        avg_volume = hist["Volume"].tail(20).mean()

        current_volume = hist["Volume"].iloc[-1]

        volume_ratio = 1

        if avg_volume > 0:

            volume_ratio = (

                current_volume

                /

                avg_volume
            )

        return {

            "current_price": round(
                float(live_price),
                2
            ),

            "ret_5d": round(
                float(ret_5d),
                2
            ),

            "ret_20d": round(
                float(ret_20d),
                2
            ),

            "volume_ratio": round(
                float(volume_ratio),
                2
            )
        }

    except Exception as e:

        print(
            f"Live data error for {symbol}: {e}"
        )

        return {

            "current_price": 0,

            "ret_5d": 0,

            "ret_20d": 0,

            "volume_ratio": 1
        }

# =========================================================
# MARKET REGIME ENGINE
# =========================================================

def calculate_market_regime(df):

    avg_inst = df[
        "Institutional Score"
    ].mean()

    avg_alpha = df[
        "Alpha Score"
    ].mean()

    avg_rsi = df[
        "RSI"
    ].mean()

    avg_adx = df[
        "ADX"
    ].mean()

    avg_buy_prob = df[
        "Buy Probability"
    ].mean()

    regime_score = (

        avg_inst * 0.30

        +

        avg_alpha * 0.25

        +

        avg_buy_prob * 0.25

        +

        avg_rsi * 0.10

        +

        avg_adx * 0.10
    )

    # =====================================================
    # REGIME CLASSIFICATION
    # =====================================================

    if regime_score >= 80:

        return "🚀 Strong Bullish"

    elif regime_score >= 65:

        return "📈 Bullish"

    elif regime_score >= 50:

        return "⚖️ Neutral"

    elif regime_score >= 35:

        return "📉 Bearish"

    return "🩸 Strong Bearish"

# =========================================================
# BUILD TRADE DECISIONS
# =========================================================

def build_trade_decisions(df):

    df = df.copy()

    # =====================================================
    # SAFE NUMERIC
    # =====================================================

    numeric_columns = [

        "Institutional Score",

        "Alpha Score",

        "Buy Probability",

        "RSI",

        "ADX"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = safe_numeric(
                df[column]
            )

        else:

            df[column] = 0

    # =====================================================
    # LIVE MARKET DATA
    # =====================================================

    live_prices = []
    ret_5d_list = []
    ret_20d_list = []
    volume_ratio_list = []

    for _, row in df.iterrows():

        symbol = row.get(
            "Stock",
            None
        )

        if symbol is None:

            symbol = row.get(
                "Symbol",
                ""
            )

        market_data = get_live_market_data(
            symbol
        )

        live_prices.append(
            market_data["current_price"]
        )

        ret_5d_list.append(
            market_data["ret_5d"]
        )

        ret_20d_list.append(
            market_data["ret_20d"]
        )

        volume_ratio_list.append(
            market_data["volume_ratio"]
        )

    df["Current Price"] = live_prices

    df["5D Return"] = ret_5d_list

    df["20D Return"] = ret_20d_list

    df["Volume Ratio"] = volume_ratio_list

    # =====================================================
    # MOMENTUM SCORE
    # =====================================================

    df["Momentum Score"] = (

        (

            df["5D Return"] * 0.40
        )

        +

        (

            df["20D Return"] * 0.60
        )
    )

    # =====================================================
    # VOLUME SCORE
    # =====================================================

    df["Volume Score"] = (

        df["Volume Ratio"]

        * 50
    ).clip(0, 100)

    # =====================================================
    # MARKET REGIME
    # =====================================================

    market_regime = calculate_market_regime(
        df
    )

    # =====================================================
    # REGIME-BASED WEIGHTS
    # =====================================================

    if "Bearish" in market_regime:

        institutional_weight = 0.45
        momentum_weight = 0.15
        volume_weight = 0.10
        alpha_weight = 0.20
        probability_weight = 0.10

    else:

        institutional_weight = 0.30
        momentum_weight = 0.25
        volume_weight = 0.15
        alpha_weight = 0.20
        probability_weight = 0.10

    # =====================================================
    # COMPOSITE SCORE
    # =====================================================

    df["Composite Score"] = (

        (

            df["Institutional Score"]

            * institutional_weight
        )

        +

        (

            df["Momentum Score"]

            * momentum_weight
        )

        +

        (

            df["Volume Score"]

            * volume_weight
        )

        +

        (

            df["Alpha Score"]

            * alpha_weight
        )

        +

        (

            df["Buy Probability"]

            * probability_weight
        )
    )

    # =====================================================
    # NORMALIZE SCORE
    # =====================================================

    df["Composite Score"] = (

        df["Composite Score"]

        .clip(0, 100)

        .round(2)
    )

    # =====================================================
    # PERCENTILE RANK
    # =====================================================

    df["Percentile Rank"] = (

        df["Composite Score"]

        .rank(pct=True)
    )

    # =====================================================
    # SIGNAL ENGINE
    # =====================================================

    def generate_signal(rank):

        if rank >= 0.95:

            return "Strong Buy"

        elif rank >= 0.80:

            return "Buy"

        elif rank >= 0.50:

            return "Watch"

        return "Avoid"

    df["Trade Signal"] = df[
        "Percentile Rank"
    ].apply(generate_signal)

    # =====================================================
    # TARGET PRICE
    # =====================================================

    df["Target Price"] = (

        df["Current Price"]

        * (

            1

            +

            (
                df["Composite Score"]

                / 100
            ) * 0.25
        )
    ).round(2)

    # =====================================================
    # STOPLOSS
    # =====================================================

    df["Stoploss"] = (

        df["Current Price"]

        * 0.93
    ).round(2)

    # =====================================================
    # CONFIDENCE
    # =====================================================

    df["Confidence"] = (

        df["Composite Score"]

        .clip(0, 100)

        .round(2)
    )

    # =====================================================
    # LIQUIDITY FILTER
    # =====================================================

    df = df[
        df["Current Price"] > 0
    ]

    # =====================================================
    # SORTING
    # =====================================================

    df = df.sort_values(

        by="Composite Score",

        ascending=False
    )

    # =====================================================
    # FINAL COLUMN ORDER
    # =====================================================

    final_columns = [

        "Stock",

        "Trade Signal",

        "Current Price",

        "Target Price",

        "Stoploss",

        "Confidence",

        "Institutional Score",

        "Alpha Score",

        "Buy Probability",

        "Momentum Score",

        "Volume Score",

        "5D Return",

        "20D Return",

        "Volume Ratio",

        "Composite Score"
    ]

    available_columns = [

        col for col in final_columns

        if col in df.columns
    ]

    df = df[
        available_columns
    ]

    return df
