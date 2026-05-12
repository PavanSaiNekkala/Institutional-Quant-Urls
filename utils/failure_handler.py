def categorize_failure(error):

    error = str(error)

    if "404" in error:
        return "INVALID_SYMBOL"

    elif "No price data" in error:
        return "DELISTED"

    elif "Unauthorized" in error:
        return "RATE_LIMITED"

    elif "Empty" in error:
        return "NO_HISTORY"

    else:
        return "UNKNOWN"
