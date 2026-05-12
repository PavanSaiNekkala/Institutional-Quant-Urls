import numpy as np

# =========================================================
# SAFE VALUE
# =========================================================

def safe(value):

    if value is None:
        return 0

    if isinstance(value, str):
        return 0

    try:

        if np.isnan(value):
            return 0

    except:
        pass

    return value

# =========================================================
# VALUE FACTOR
# =========================================================

def calculate_value_factor(data):

    market_cap = safe(
        data.get("Market Cap")
    )

    revenue = safe(
        data.get("Revenue")
    )

    if market_cap <= 0:

        return 0

    ratio = revenue / market_cap

    return round(
        min(ratio * 100, 100),
        2
    )

# =========================================================
# QUALITY FACTOR
# =========================================================

def calculate_quality_factor(data):

    equity = safe(
        data.get("Equity")
    )

    debt = safe(
        data.get("Total Debt")
    )

    if equity <= 0:

        return 0

    score = (
        1 - min(
            debt / equity,
            1
        )
    ) * 100

    return round(score, 2)

# =========================================================
# MOMENTUM FACTOR
# =========================================================

def calculate_momentum_factor(data):

    rsi = safe(
        data.get("RSI")
    )

    sma50 = safe(
        data.get("SMA50")
    )

    sma200 = safe(
        data.get("SMA200")
    )

    score = 0

    if rsi > 60:

        score += 50

    if sma50 > sma200:

        score += 50

    return score

# =========================================================
# LOW RISK FACTOR
# =========================================================

def calculate_low_risk_factor(data):

    debt = safe(
        data.get("Total Debt")
    )

    cash = safe(
        data.get("Cash")
    )

    if debt <= 0:

        return 100

    score = min(
        (cash / debt) * 100,
        100
    )

    return round(score, 2)

# =========================================================
# PROFITABILITY FACTOR
# =========================================================

def calculate_profitability_factor(data):

    revenue = safe(
        data.get("Revenue")
    )

    net_income = safe(
        data.get("Net Income")
    )

    if revenue <= 0:

        return 0

    margin = (
        net_income / revenue
    ) * 100

    return round(
        max(min(margin, 100), 0),
        2
    )

# =========================================================
# MASTER QUANT ENGINE
# =========================================================

def calculate_quant_scores(data):

    value_factor = calculate_value_factor(data)

    quality_factor = calculate_quality_factor(data)

    momentum_factor = calculate_momentum_factor(data)

    low_risk_factor = calculate_low_risk_factor(data)

    profitability_factor = (
        calculate_profitability_factor(data)
    )

    # =====================================================
    # ALPHA SCORE
    # =====================================================

    alpha_score = (

        value_factor * 0.20 +

        quality_factor * 0.25 +

        momentum_factor * 0.20 +

        low_risk_factor * 0.15 +

        profitability_factor * 0.20
    )

    alpha_score = round(alpha_score, 2)

    # =====================================================
    # QUANT RANK
    # =====================================================

    if alpha_score >= 85:

        quant_rank = "Elite"

    elif alpha_score >= 70:

        quant_rank = "Strong"

    elif alpha_score >= 55:

        quant_rank = "Moderate"

    else:

        quant_rank = "Weak"

    return {

        "Value Factor": value_factor,

        "Quality Factor": quality_factor,

        "Momentum Factor": momentum_factor,

        "Low Risk Factor": low_risk_factor,

        "Profitability Factor": profitability_factor,

        "Alpha Score": alpha_score,

        "Quant Rank": quant_rank
    }