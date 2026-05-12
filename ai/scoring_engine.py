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
# VALUE SCORE
# =========================================================

def calculate_value_score(data):

    market_cap = safe(
        data.get("Market Cap")
    )

    revenue = safe(
        data.get("Revenue")
    )

    score = 50

    if revenue > market_cap * 0.5:
        score += 25

    if market_cap > 0:
        score += 25

    return min(score, 100)

# =========================================================
# GROWTH SCORE
# =========================================================

def calculate_growth_score(data):

    revenue = safe(
        data.get("Revenue")
    )

    net_income = safe(
        data.get("Net Income")
    )

    score = 50

    if revenue > 0:
        score += 25

    if net_income > 0:
        score += 25

    return min(score, 100)

# =========================================================
# QUALITY SCORE
# =========================================================

def calculate_quality_score(data):

    debt = safe(
        data.get("Total Debt")
    )

    cash = safe(
        data.get("Cash")
    )

    equity = safe(
        data.get("Equity")
    )

    score = 50

    if cash > debt:
        score += 25

    if equity > 0:
        score += 25

    return min(score, 100)

# =========================================================
# MOMENTUM SCORE
# =========================================================

def calculate_momentum_score(data):

    rsi = safe(
        data.get("RSI")
    )

    sma50 = safe(
        data.get("SMA50")
    )

    sma200 = safe(
        data.get("SMA200")
    )

    score = 50

    if rsi > 60:
        score += 25

    if sma50 > sma200:
        score += 25

    return min(score, 100)

# =========================================================
# RISK SCORE
# =========================================================

def calculate_risk_score(data):

    debt = safe(
        data.get("Total Debt")
    )

    equity = safe(
        data.get("Equity")
    )

    score = 100

    if equity > 0:

        debt_equity = debt / equity

        if debt_equity > 2:
            score -= 50

        elif debt_equity > 1:
            score -= 25

    return max(score, 0)

# =========================================================
# INSTITUTIONAL SCORE
# =========================================================

def calculate_institutional_score(data):

    value_score = calculate_value_score(data)

    growth_score = calculate_growth_score(data)

    quality_score = calculate_quality_score(data)

    momentum_score = calculate_momentum_score(data)

    risk_score = calculate_risk_score(data)

    institutional_score = (

        value_score * 0.20 +

        growth_score * 0.20 +

        quality_score * 0.25 +

        momentum_score * 0.20 +

        risk_score * 0.15
    )

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    if institutional_score >= 85:

        recommendation = "Strong Buy"

    elif institutional_score >= 70:

        recommendation = "Buy"

    elif institutional_score >= 55:

        recommendation = "Watch"

    else:

        recommendation = "Avoid"

    return {

        "Value Score": round(value_score, 2),

        "Growth Score": round(growth_score, 2),

        "Quality Score": round(quality_score, 2),

        "Momentum Score": round(momentum_score, 2),

        "Risk Score": round(risk_score, 2),

        "Institutional Score": round(
            institutional_score,
            2
        ),

        "Recommendation": recommendation
    }
