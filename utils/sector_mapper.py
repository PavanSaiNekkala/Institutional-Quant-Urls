import numpy as np

# =========================================================
# SECTOR MAPPING
# =========================================================

SECTOR_KEYWORDS = {

    "BANK": "Banking",

    "FIN": "Financial Services",

    "INS": "Insurance",

    "TECH": "Technology",

    "INFY": "Technology",

    "TCS": "Technology",

    "WIPRO": "Technology",

    "PHARMA": "Pharmaceuticals",

    "LAB": "Healthcare",

    "AUTO": "Automobile",

    "MOTORS": "Automobile",

    "POWER": "Power",

    "ENERGY": "Energy",

    "OIL": "Oil & Gas",

    "GAS": "Oil & Gas",

    "STEEL": "Metals",

    "METAL": "Metals",

    "CEMENT": "Cement",

    "REALTY": "Real Estate",

    "TEXTILE": "Textiles",

    "CHEM": "Chemicals",

    "FMCG": "FMCG",

    "FOOD": "FMCG",

    "CONSUMER": "Consumer",

    "IT": "Technology"
}

# =========================================================
# INDUSTRY MAPPING
# =========================================================

INDUSTRY_KEYWORDS = {

    "BANK": "Private Banking",

    "TECH": "Software Services",

    "PHARMA": "Drug Manufacturing",

    "AUTO": "Automobile Manufacturing",

    "POWER": "Power Generation",

    "STEEL": "Steel Manufacturing",

    "CEMENT": "Cement Production"
}

# =========================================================
# THEME MAPPING
# =========================================================

THEME_KEYWORDS = {

    "AI": "Artificial Intelligence",

    "GREEN": "Green Energy",

    "SOLAR": "Renewable Energy",

    "EV": "Electric Vehicles",

    "DIGITAL": "Digital Transformation",

    "TECH": "Technology",

    "BANK": "Financialization"
}

# =========================================================
# DETECT SECTOR
# =========================================================

def detect_sector(stock):

    stock = str(stock).upper()

    for keyword, sector in SECTOR_KEYWORDS.items():

        if keyword in stock:

            return sector

    return "Other"

# =========================================================
# DETECT INDUSTRY
# =========================================================

def detect_industry(stock):

    stock = str(stock).upper()

    for keyword, industry in INDUSTRY_KEYWORDS.items():

        if keyword in stock:

            return industry

    return "General"

# =========================================================
# DETECT THEME
# =========================================================

def detect_theme(stock):

    stock = str(stock).upper()

    for keyword, theme in THEME_KEYWORDS.items():

        if keyword in stock:

            return theme

    return "Diversified"

# =========================================================
# MASTER FUNCTION
# =========================================================

def get_sector_data(stock):

    return {

        "Sector": detect_sector(stock),

        "Industry": detect_industry(stock),

        "Theme": detect_theme(stock)
    }
