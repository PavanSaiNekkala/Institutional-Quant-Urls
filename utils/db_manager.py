# =========================================================
# DATABASE MANAGER
# =========================================================

import duckdb

from pathlib import Path

# =========================================================
# BASE PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = (
    BASE_DIR
    / "database"
)

DATABASE_DIR.mkdir(
    exist_ok=True
)

DATABASE_FILE = (
    DATABASE_DIR
    / "institutional_quant.db"
)

# =========================================================
# GET CONNECTION
# =========================================================

def get_connection():

    conn = duckdb.connect(

        str(DATABASE_FILE)
    )

    return conn
