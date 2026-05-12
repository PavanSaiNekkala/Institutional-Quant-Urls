import pandas as pd
import numpy as np
import yfinance as yf

# =========================================================
# FETCH RETURNS
# =========================================================

def fetch_returns(symbols):

    returns_dict = {}

    for symbol in symbols:

        try:

            ticker = yf.Ticker(symbol)

            hist = ticker.history(
                period="1y"
            )

            if hist.empty:

                continue

            returns = hist[
                "Close"
            ].pct_change().dropna()

            returns_dict[symbol] = returns

        except:

            continue

    return pd.DataFrame(
        returns_dict
    )

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

def build_portfolio_returns(

    returns_df,

    weights
):

    aligned_weights = np.array(
        weights
    )

    portfolio_returns = (

        returns_df * aligned_weights

    ).sum(axis=1)

    return portfolio_returns

# =========================================================
# CAGR
# =========================================================

def calculate_cagr(returns):

    cumulative = (
        1 + returns
    ).prod()

    years = len(returns) / 252

    if years == 0:

        return 0

    cagr = (

        cumulative ** (1 / years)

    ) - 1

    return cagr

# =========================================================
# SHARPE RATIO
# =========================================================

def calculate_sharpe_ratio(

    returns,

    risk_free_rate=0.05
):

    excess_returns = (

        returns - risk_free_rate / 252
    )

    if excess_returns.std() == 0:

        return 0

    sharpe = (

        np.sqrt(252)

        * excess_returns.mean()

        / excess_returns.std()
    )

    return sharpe

# =========================================================
# MAX DRAWDOWN
# =========================================================

def calculate_max_drawdown(
    returns
):

    cumulative = (
        1 + returns
    ).cumprod()

    peak = cumulative.cummax()

    drawdown = (

        cumulative - peak

    ) / peak

    return drawdown.min()

# =========================================================
# VOLATILITY
# =========================================================

def calculate_volatility(
    returns
):

    volatility = (

        returns.std()

        * np.sqrt(252)
    )

    return volatility

# =========================================================
# PERFORMANCE METRICS
# =========================================================

def calculate_metrics(
    portfolio_returns
):

    cumulative_returns = (

        1 + portfolio_returns

    ).cumprod()

    cagr = calculate_cagr(
        portfolio_returns
    )

    sharpe = calculate_sharpe_ratio(
        portfolio_returns
    )

    max_drawdown = calculate_max_drawdown(
        portfolio_returns
    )

    volatility = calculate_volatility(
        portfolio_returns
    )

    win_rate = (

        (
            portfolio_returns > 0
        ).sum()

        / len(portfolio_returns)

    ) * 100

    return {

        "CAGR": round(
            cagr * 100,
            2
        ),

        "Sharpe Ratio": round(
            sharpe,
            2
        ),

        "Max Drawdown": round(
            max_drawdown * 100,
            2
        ),

        "Volatility": round(
            volatility * 100,
            2
        ),

        "Win Rate": round(
            win_rate,
            2
        ),

        "Equity Curve": cumulative_returns
    }

# =========================================================
# MASTER BACKTEST ENGINE
# =========================================================

def run_backtest(portfolio_df):

    symbols = portfolio_df[
        "Stock"
    ].tolist()

    weights = (

        portfolio_df[
            "Portfolio Weight"
        ] / 100

    ).tolist()

    returns_df = fetch_returns(
        symbols
    )

    if returns_df.empty:

        return None

    valid_symbols = returns_df.columns.tolist()

    filtered_portfolio = portfolio_df[

        portfolio_df["Stock"].isin(
            valid_symbols
        )
    ]

    weights = (

        filtered_portfolio[
            "Portfolio Weight"
        ] / 100

    ).tolist()

    portfolio_returns = build_portfolio_returns(

        returns_df,

        weights
    )

    metrics = calculate_metrics(
        portfolio_returns
    )

    return metrics