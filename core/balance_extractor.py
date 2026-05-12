import numpy as np

def extract_balance_sheet(ticker):

    balance = ticker.balance_sheet

    data = {

        "Total Assets": np.nan,
        "Total Debt": np.nan,
        "Cash": np.nan,
        "Equity": np.nan

    }

    try:
        data["Total Assets"] = balance.loc["Total Assets"].iloc[0]
    except:
        pass

    try:
        data["Total Debt"] = balance.loc["Total Debt"].iloc[0]
    except:
        pass

    try:
        data["Cash"] = balance.loc["Cash And Cash Equivalents"].iloc[0]
    except:
        pass

    try:
        data["Equity"] = balance.loc["Stockholders Equity"].iloc[0]
    except:
        pass

    return data