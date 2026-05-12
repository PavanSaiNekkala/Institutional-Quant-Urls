# =========================================================
# IMPORTS
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# SAFE NUMERIC
# =========================================================

def safe_numeric(series):

    return pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

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

        "ADX",

        "Current Price"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = safe_numeric(
                df[column]
            )

        else:

            df[column] = 0

    # =====================================================
    # COMPOSITE SCORE
    # =====================================================

    df["Composite Score"] = (

        (
            df["Institutional Score"] * 0.35
        )

        +

        (
            df["Alpha Score"] * 0.30
        )

        +

        (
            df["Buy Probability"] * 0.20
        )

        +

        (
            df["ADX"] * 0.10
        )

        +

        (
            (100 - abs(50 - df["RSI"])) * 0.05
        )
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
                df["Composite Score"] / 100
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
    # SORTING
    # =====================================================

    df = df.sort_values(

        by="Composite Score",

        ascending=False
    )

    return df
