import pandas as pd

def build_trade_decisions(df):

    df = df.copy()

    # =====================================================
    # DEFAULTS
    # =====================================================

    if "Current Price" not in df.columns:

        df["Current Price"] = 0

    if "Institutional Score" not in df.columns:

        df["Institutional Score"] = 0

    # =====================================================
    # TRADE SIGNAL
    # =====================================================

    def generate_signal(score):

        if score >= 85:

            return "Strong Buy"

        elif score >= 70:

            return "Buy"

        elif score >= 50:

            return "Watch"

        return "Avoid"

    # =====================================================
    # APPLY SIGNAL
    # =====================================================

    df["Trade Signal"] = df[
        "Institutional Score"
    ].apply(generate_signal)

    # =====================================================
    # TARGET
    # =====================================================

    df["Target Price"] = (

        df["Current Price"]

        * 1.15
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

    df["Confidence"] = df[
        "Institutional Score"
    ]

    return df