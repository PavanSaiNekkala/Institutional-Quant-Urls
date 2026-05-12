# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

from pathlib import Path

from streamlit_autorefresh import (
    st_autorefresh
)

from analytics.realtime_market_engine import (

    fetch_live_market_data,

    get_top_gainers,

    get_top_losers,

    get_volume_shocks,

    calculate_market_breadth
)

from analytics.trade_decision_engine import (
    build_trade_decisions
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

    page_icon="📈",

    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(

    interval=60000,

    key="market_refresh"
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DB_FILE = (
    BASE_DIR
    / "database"
    / "institutional_quant.db"
)

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = duckdb.connect(
    str(DB_FILE)
)

# =========================================================
# CHECK TABLES
# =========================================================

tables = conn.execute(
    '''
    SHOW TABLES
    '''
).fetchall()

tables = [
    table[0]
    for table in tables
]

# =========================================================
# VALIDATE DATABASE
# =========================================================

if "enriched_stocks" not in tables:

    st.error(
        """
        enriched_stocks table not found.

        Please run:

        python main.py

        before launching Streamlit.
        """
    )

    st.stop()

# =========================================================
# LOAD MAIN DATA
# =========================================================

df = conn.execute(
    '''
    SELECT *
    FROM enriched_stocks
    '''
).df()

# =========================================================
# LOAD PORTFOLIO
# =========================================================

if "institutional_portfolio" in tables:

    portfolio_df = conn.execute(
        '''
        SELECT *
        FROM institutional_portfolio
        '''
    ).df()

else:

    portfolio_df = pd.DataFrame()

# =========================================================
# CLEAN NUMERIC DATA
# =========================================================

numeric_columns = [

    "Institutional Score",

    "Alpha Score",

    "RSI",

    "ADX",

    "MACD",

    "Market Cap",

    "Buy Probability",

    "Prediction Confidence",

    "Portfolio Weight",

    "Current Price"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(

            df[column],

            errors="coerce"
        )

# =========================================================
# LIVE MARKET DATA
# =========================================================

if "Validated Symbol" in df.columns:

    symbols = df[
        "Validated Symbol"
    ].dropna().tolist()

else:

    symbols = df[
        "Stock"
    ].dropna().tolist()

live_df = fetch_live_market_data(
    symbols[:30]
)

# =========================================================
# LIVE ANALYTICS
# =========================================================

top_gainers = get_top_gainers(
    live_df
)

top_losers = get_top_losers(
    live_df
)

volume_shocks = get_volume_shocks(
    live_df
)

breadth = calculate_market_breadth(
    live_df
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "Institutional Controls"
)

# =========================================================
# SECTOR FILTER
# =========================================================

if "Sector" in df.columns:

    selected_sector = st.sidebar.selectbox(

        "Select Sector",

        ["All"] + sorted(
            df["Sector"]
            .dropna()
            .unique()
            .tolist()
        )
    )

else:

    selected_sector = "All"

# =========================================================
# QUANT FILTER
# =========================================================

if "Quant Rank" in df.columns:

    selected_rank = st.sidebar.selectbox(

        "Quant Rank",

        ["All"] + sorted(
            df["Quant Rank"]
            .dropna()
            .unique()
            .tolist()
        )
    )

else:

    selected_rank = "All"

# =========================================================
# SIGNAL FILTER
# =========================================================

selected_signal = st.sidebar.selectbox(

    "Trade Signal",

    [

        "All",

        "Strong Buy",

        "Buy",

        "Watch",

        "Avoid"
    ]
)

# =========================================================
# SCORE FILTER
# =========================================================

min_score = st.sidebar.slider(

    "Minimum Institutional Score",

    0,

    100,

    60
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df.copy()

if (
    selected_sector != "All"
    and "Sector" in filtered_df.columns
):

    filtered_df = filtered_df[
        filtered_df["Sector"]
        == selected_sector
    ]

if (
    selected_rank != "All"
    and "Quant Rank" in filtered_df.columns
):

    filtered_df = filtered_df[
        filtered_df["Quant Rank"]
        == selected_rank
    ]

if "Institutional Score" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df[
            "Institutional Score"
        ] >= min_score
    ]

# =========================================================
# BUILD TRADE DECISIONS
# =========================================================

filtered_df = build_trade_decisions(
    filtered_df
)

# =========================================================
# SIGNAL FILTER
# =========================================================

if selected_signal != "All":

    filtered_df = filtered_df[
        filtered_df["Trade Signal"]
        == selected_signal
    ]

# =========================================================
# TITLE
# =========================================================

st.title(
    "Institutional Quant Platform"
)

st.markdown("---")

# =========================================================
# TOP TRADE DECISIONS
# =========================================================

st.subheader(
    "Institutional Trade Signals"
)

priority_columns = [

    "Stock",

    "Trade Signal",

    "Current Price",

    "Target Price",

    "Stoploss",

    "Confidence"
]

available_columns = [

    col

    for col in priority_columns

    if col in filtered_df.columns
]

priority_df = filtered_df[

    available_columns

].copy()

signal_order = {

    "Strong Buy": 0,

    "Buy": 1,

    "Watch": 2,

    "Avoid": 3
}

priority_df["Signal Rank"] = priority_df[
    "Trade Signal"
].map(signal_order)

priority_df = priority_df.sort_values(

    by=[

        "Signal Rank",

        "Confidence"
    ],

    ascending=[True, False]
)

priority_df = priority_df.drop(
    columns=["Signal Rank"]
)

st.dataframe(

    priority_df.head(25),

    use_container_width=True
)

st.markdown("---")

# =========================================================
# MARKET BREADTH
# =========================================================

st.subheader(
    "Live Market Breadth"
)

breadth_col1, breadth_col2, breadth_col3, breadth_col4 = st.columns(4)

breadth_col1.metric(
    "Advancing",
    breadth["Advancing"]
)

breadth_col2.metric(
    "Declining",
    breadth["Declining"]
)

breadth_col3.metric(
    "Unchanged",
    breadth["Unchanged"]
)

breadth_col4.metric(
    "Breadth Ratio",
    breadth["Breadth Ratio"]
)

st.markdown("---")

# =========================================================
# MAIN KPIs
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Stocks",
    len(filtered_df)
)

if "Institutional Score" in filtered_df.columns:

    avg_inst_score = round(

        filtered_df[
            "Institutional Score"
        ].mean(),

        2
    )

else:

    avg_inst_score = 0

col2.metric(
    "Avg Institutional Score",
    avg_inst_score
)

if "Alpha Score" in filtered_df.columns:

    avg_alpha_score = round(

        filtered_df[
            "Alpha Score"
        ].mean(),

        2
    )

else:

    avg_alpha_score = 0

col3.metric(
    "Avg Alpha Score",
    avg_alpha_score
)

col4.metric(
    "Portfolio Stocks",
    len(portfolio_df)
)

st.markdown("---")

# =========================================================
# TOP GAINERS / LOSERS
# =========================================================

gainer_col, loser_col = st.columns(2)

with gainer_col:

    st.subheader(
        "Top Gainers"
    )

    st.dataframe(
        top_gainers,
        use_container_width=True
    )

with loser_col:

    st.subheader(
        "Top Losers"
    )

    st.dataframe(
        top_losers,
        use_container_width=True
    )

st.markdown("---")

# =========================================================
# VOLUME SHOCK MONITOR
# =========================================================

st.subheader(
    "Volume Shock Monitor"
)

st.dataframe(
    volume_shocks,
    use_container_width=True
)

st.markdown("---")

# =========================================================
# SECTOR DISTRIBUTION
# =========================================================

if "Sector" in filtered_df.columns:

    st.subheader(
        "Sector Distribution"
    )

    sector_chart = px.pie(

        filtered_df,

        names="Sector",

        title="Sector Allocation"
    )

    st.plotly_chart(
        sector_chart,
        use_container_width=True
    )

# =========================================================
# ALPHA DISTRIBUTION
# =========================================================

if "Alpha Score" in filtered_df.columns:

    st.subheader(
        "Alpha Score Distribution"
    )

    alpha_chart = px.histogram(

        filtered_df,

        x="Alpha Score",

        nbins=20,

        title="Alpha Score Distribution"
    )

    st.plotly_chart(
        alpha_chart,
        use_container_width=True
    )

# =========================================================
# TECHNICAL MOMENTUM MAP
# =========================================================

required_technical_columns = [

    "RSI",

    "ADX",

    "Alpha Score",

    "Market Cap"
]

technical_available = all(

    column in filtered_df.columns

    for column in required_technical_columns
)

if technical_available:

    st.subheader(
        "Technical Momentum Map"
    )

    technical_chart = px.scatter(

        filtered_df,

        x="RSI",

        y="ADX",

        color="Alpha Score",

        size="Market Cap",

        hover_data=["Stock"],

        title="RSI vs ADX Momentum"
    )

    st.plotly_chart(
        technical_chart,
        use_container_width=True
    )

# =========================================================
# AI PREDICTION MAP
# =========================================================

required_ml_columns = [

    "Buy Probability",

    "Prediction Confidence"
]

ml_available = all(

    column in filtered_df.columns

    for column in required_ml_columns
)

if ml_available:

    st.subheader(
        "AI Prediction Leaders"
    )

    ml_chart = px.scatter(

        filtered_df,

        x="Buy Probability",

        y="Prediction Confidence",

        color="Trade Signal",

        size="Confidence",

        hover_data=["Stock"],

        title="AI Prediction Map"
    )

    st.plotly_chart(
        ml_chart,
        use_container_width=True
    )

# =========================================================
# PORTFOLIO VIEW
# =========================================================

st.subheader(
    "Institutional Portfolio"
)

if not portfolio_df.empty:

    display_columns = [

        column

        for column in [

            "Portfolio Rank",

            "Stock",

            "Sector",

            "Institutional Score",

            "Alpha Score",

            "Portfolio Weight"
        ]

        if column in portfolio_df.columns
    ]

    st.dataframe(

        portfolio_df[
            display_columns
        ],

        use_container_width=True
    )

else:

    st.warning(
        "Portfolio table not found."
    )

# =========================================================
# TOP QUANT LEADERS
# =========================================================

st.subheader(
    "Top Quant Leaders"
)

if "Alpha Score" in filtered_df.columns:

    quant_leaders = filtered_df.sort_values(

        by="Alpha Score",

        ascending=False

    ).head(20)

    st.dataframe(
        quant_leaders,
        use_container_width=True
    )

# =========================================================
# RAW DATA
# =========================================================

with st.expander(
    "View Full Enriched Dataset"
):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Institutional Quant Platform"
)

# =========================================================
# CLOSE DB
# =========================================================

conn.close()