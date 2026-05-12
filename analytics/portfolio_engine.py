import pandas as pd
import numpy as np

# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

def normalize_weights(series):

    total = series.sum()

    if total <= 0:

        return series

    return (
        series / total
    ) * 100

# =========================================================
# PORTFOLIO ENGINE
# =========================================================

def build_portfolio(df):

    portfolio_df = df.copy()

    # =====================================================
    # COMBINED SCORE
    # =====================================================

    portfolio_df["Combined Score"] = (

        portfolio_df[
            "Institutional Score"
        ] * 0.60 +

        portfolio_df[
            "Alpha Score"
        ] * 0.40
    )

    # =====================================================
    # SORT BEST STOCKS
    # =====================================================

    portfolio_df = portfolio_df.sort_values(

        by="Combined Score",

        ascending=False
    )

    # =====================================================
    # TOP STOCKS ONLY
    # =====================================================

    portfolio_df = portfolio_df.head(25)

    # =====================================================
    # WEIGHT GENERATION
    # =====================================================

    portfolio_df[
        "Portfolio Weight"
    ] = normalize_weights(

        portfolio_df[
            "Combined Score"
        ]
    )

    # =====================================================
    # RISK BUCKET
    # =====================================================

    portfolio_df[
        "Risk Bucket"
    ] = np.where(

        portfolio_df[
            "Risk Score"
        ] >= 80,

        "Low Risk",

        np.where(

            portfolio_df[
                "Risk Score"
            ] >= 60,

            "Medium Risk",

            "High Risk"
        )
    )

    # =====================================================
    # PORTFOLIO RANK
    # =====================================================

    portfolio_df[
        "Portfolio Rank"
    ] = range(
        1,
        len(portfolio_df) + 1
    )

    return portfolio_df