# =========================================================
# INSTITUTIONAL - QUANT - URLS
# POWER BI STYLE DASHBOARD
# =========================================================

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import pandas as pd
import duckdb

from pathlib import Path
from datetime import datetime

from analytics.trade_decision_engine import (

    build_trade_decisions,

    calculate_market_regime
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional - Quant - Urls",

    page_icon="📈",

    layout="wide",

    initial_sidebar_state="expanded"
)

# =========================================================
# POWER BI STYLE CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {

        background-color: #f3f4f6;

        color: #111827;
    }

    .main .block-container {

        max-width: 1450px;

        padding-top: 1rem;

        padding-bottom: 1rem;
    }

    /* =====================================================
       SIDEBAR
    ===================================================== */

    section[data-testid="stSidebar"] {

        background-color: #ffffff;

        border-right: 1px solid #d1d5db;
    }

    section[data-testid="stSidebar"] * {

        color: #111827;
    }

    /* =====================================================
       HEADER
    ===================================================== */

    .dashboard-header {

        background: linear-gradient(
            90deg,
            #2563eb,
            #1d4ed8
        );

        padding: 24px;

        border-radius: 18px;

        margin-bottom: 20px;

        color: white;

        box-shadow:
            0 6px 18px rgba(0,0,0,0.12);
    }

    .dashboard-title {

        font-size: 42px;

        font-weight: 800;

        margin-bottom: 0px;
    }

    .dashboard-subtitle {

        font-size: 16px;

        opacity: 0.92;
    }

    /* =====================================================
       KPI CARDS
    ===================================================== */

    .kpi-card {

        background-color: white;

        padding: 22px;

        border-radius: 18px;

        border-left: 6px solid #2563eb;

        box-shadow:
            0 3px 12px rgba(0,0,0,0.08);

        margin-bottom: 10px;
    }

    .kpi-title {

        font-size: 14px;

        color: #6b7280;

        margin-bottom: 10px;
    }

    .kpi-value {

        font-size: 34px;

        font-weight: 800;

        color: #111827;
    }

    .kpi-sub {

        font-size: 13px;

        color: #10b981;

        margin-top: 6px;
    }

    /* =====================================================
       SECTION TITLES
    ===================================================== */

    .section-title {

        font-size: 28px;

        font-weight: 700;

        color: #111827;

        margin-top: 18px;

        margin-bottom: 12px;
    }

    /* =====================================================
       STATUS CARD
    ===================================================== */

    .status-card {

        background-color: white;

        padding: 20px;

        border-radius: 18px;

        box-shadow:
            0 3px 12px rgba(0,0,0,0.08);

        margin-bottom: 15px;
    }

    /* =====================================================
       TABLES
    ===================================================== */

    .stDataFrame {

        border-radius: 16px;

        overflow: hidden;

        border: 1px solid #e5e7eb;

        background-color: white;
    }

    /* =====================================================
       METRICS
    ===================================================== */

    div[data-testid="metric-container"] {

        background-color: white;

        border-radius: 16px;

        padding: 14px;

        border: 1px solid #e5e7eb;

        box-shadow:
            0 3px 12px rgba(0,0,0,0.06);
    }

    </style>
    """,

    unsafe_allow_html=True
)

# =========================================================
# SECTOR NORMALIZATION
# =========================================================

def normalize_sector(sector):

    if pd.isna(sector):

        return "Other"

    sector = str(sector).strip().lower()

    sector_mapping = {

        "it services": "Technology",
        "software": "Technology",
        "information technology": "Technology",

        "banking": "Banking",
        "banks": "Banking",

        "financial services": "Financial Services",

        "pharma": "Healthcare",

        "oil & gas": "Energy",

        "fmcg": "Consumer",

        "auto": "Automobile",

        "metals": "Metals & Mining",

        "chemicals": "Chemicals"
    }

    for key, value in sector_mapping.items():

        if key in sector:

            return value

    return "Other"

# =========================================================
# DATABASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DB_FILE = (

    BASE_DIR

    / "database"

    / "institutional_quant.db"
)

conn = duckdb.connect(
    str(DB_FILE),
    read_only=True
)

# =========================================================
# LOAD DATABASE
# =========================================================

@st.cache_data(ttl=300)

def load_database():

    return conn.execute(
        """
        SELECT *
        FROM enriched_stocks
        """
    ).df()

df = load_database()

# =========================================================
# CLEAN NUMERIC
# =========================================================

numeric_columns = [

    "Institutional Score",

    "Alpha Score",

    "Buy Probability",

    "RSI",

    "ADX"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(

            df[column],

            errors="coerce"

        ).fillna(0)

# =========================================================
# SECTOR NORMALIZATION
# =========================================================

if "Sector" in df.columns:

    df["Sector"] = df[
        "Sector"
    ].apply(
        normalize_sector
    )

else:

    df["Sector"] = "Other"

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    "## Institutional Controls"
)

st.sidebar.caption(
    "Live Quantitative Filtering Engine"
)

# =========================================================
# LIVE UNIVERSE
# =========================================================

live_universe_size = st.sidebar.slider(

    "Live Analysis Universe",

    min_value=25,

    max_value=100,

    value=50,

    step=25
)

# =========================================================
# FILTERS
# =========================================================

sectors = sorted(

    df["Sector"]

    .dropna()

    .unique()

    .tolist()
)

selected_sector = st.sidebar.selectbox(

    "Sector",

    ["All"] + sectors
)

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

min_score = st.sidebar.slider(

    "Minimum Institutional Score",

    0,

    100,

    60
)

# =========================================================
# FILTERING
# =========================================================

filtered_df = df.copy()

if selected_sector != "All":

    filtered_df = filtered_df[
        filtered_df["Sector"] == selected_sector
    ]

filtered_df = filtered_df[
    filtered_df["Institutional Score"] >= min_score
]

# =========================================================
# LIMIT LIVE ENGINE
# =========================================================

filtered_df = filtered_df.sort_values(

    by="Institutional Score",

    ascending=False

).head(
    live_universe_size
)

# =========================================================
# BUILD TRADE DECISIONS
# =========================================================

with st.spinner(
    "Running Institutional Quant Engine..."
):

    filtered_df = build_trade_decisions(
        filtered_df
    )

# =========================================================
# EMPTY CHECK
# =========================================================

if filtered_df.empty:

    st.warning(
        "No stocks available after processing."
    )

    st.stop()

# =========================================================
# MARKET REGIME
# =========================================================

market_regime = calculate_market_regime(
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
# HEADER
# =========================================================

st.markdown(

    """
    <div class="dashboard-header">

        <div class="dashboard-title">
            Institutional - Quant - Urls
        </div>

        <div class="dashboard-subtitle">
            AI-Powered Institutional Quantitative Analytics Platform
        </div>

    </div>
    """,

    unsafe_allow_html=True
)

st.caption(

    f"Last Updated: "

    f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

# =========================================================
# STATUS
# =========================================================

col_a, col_b = st.columns([1, 2])

with col_a:

    current_hour = datetime.now().hour

    if 9 <= current_hour <= 15:

        st.success(
            "🟢 Indian Market Live"
        )

    else:

        st.warning(
            "🔴 Market Closed"
        )

with col_b:

    st.markdown(

        f"""
        <div class="status-card">

        ⚡ <b>Live Quant Engine Active</b>

        <br><br>

        Universe Size:
        <b>{live_universe_size}</b>

        <br><br>

        Market Regime:
        <b>{market_regime}</b>

        </div>
        """,

        unsafe_allow_html=True
    )

# =========================================================
# KPI CALCULATIONS
# =========================================================

avg_score = round(
    filtered_df["Institutional Score"].mean(),
    2
)

avg_confidence = round(
    filtered_df["Confidence"].mean(),
    2
)

strong_buys = len(
    filtered_df[
        filtered_df["Trade Signal"]
        == "Strong Buy"
    ]
)

# =========================================================
# KPI CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

kpi_data = [

    (
        "Live Stocks",
        len(filtered_df),
        "Active Universe"
    ),

    (
        "Avg Institutional Score",
        avg_score,
        "Institutional Strength"
    ),

    (
        "Strong Buys",
        strong_buys,
        "High Conviction Signals"
    ),

    (
        "Avg Confidence",
        avg_confidence,
        "Model Confidence"
    )
]

for col, data in zip(

    [col1, col2, col3, col4],

    kpi_data
):

    title, value, subtitle = data

    with col:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-title">
                    {title}
                </div>

                <div class="kpi-value">
                    {value}
                </div>

                <div class="kpi-sub">
                    {subtitle}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# TABLE DATA
# =========================================================

top_signals = filtered_df[
    filtered_df["Trade Signal"].isin(
        ["Strong Buy", "Buy"]
    )
].copy()

if top_signals.empty:

    top_signals = filtered_df.head(20)

display_columns = [

    "Stock",

    "Sector",

    "Trade Signal",

    "Current Price",

    "Target Price",

    "Stoploss",

    "Confidence",

    "Composite Score"
]

available_columns = [

    col

    for col in display_columns

    if col in top_signals.columns
]

styled_df = top_signals[
    available_columns
].head(50)

# =========================================================
# POWER BI LAYOUT
# =========================================================

left_col, right_col = st.columns([2, 1])

with left_col:

    st.markdown(
        '<div class="section-title">Top Institutional Trade Signals</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=650
    )

with right_col:

    st.markdown(
        '<div class="section-title">Market Intelligence</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # SAFE TOP SECTOR
    # =====================================================

    if "Sector" in filtered_df.columns:

        sector_series = (

            filtered_df["Sector"]

            .dropna()

            .astype(str)
        )

        if not sector_series.empty:

            top_sector = (

                sector_series
                .mode()
                .iloc[0]
            )

        else:

            top_sector = "Unknown"

    else:

        top_sector = "Unknown"

    st.info(
        f"""
        Dominant Sector:

        {top_sector}
        """
    )

    bullish_count = len(
        filtered_df[
            filtered_df[
                "Trade Signal"
            ].isin([
                "Strong Buy",
                "Buy"
            ])
        ]
    )

    bearish_count = len(
        filtered_df[
            filtered_df[
                "Trade Signal"
            ] == "Avoid"
        ]
    )

    st.metric(
        "Bullish Signals",
        bullish_count
    )

    st.metric(
        "Bearish Signals",
        bearish_count
    )

    st.metric(
        "Market Regime",
        market_regime
    )

# =========================================================
# QUANT LEADERS
# =========================================================

st.markdown(
    '<div class="section-title">Top Quant Leaders</div>',
    unsafe_allow_html=True
)

quant_df = filtered_df.sort_values(

    by="Composite Score",

    ascending=False

).head(20)

st.dataframe(

    quant_df[
        available_columns
    ],

    use_container_width=True
)

# =========================================================
# FULL DATASET
# =========================================================

with st.expander(
    "View Full Dataset"
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
    "Institutional - Quant - Urls | Power BI Style Institutional Analytics Dashboard"
)

# =========================================================
# CLOSE DATABASE
# =========================================================

conn.close()
