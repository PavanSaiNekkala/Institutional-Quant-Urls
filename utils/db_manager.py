import duckdb
from pathlib import Path

# =====================================================
# DATABASE PATH
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = BASE_DIR / "database"

DB_DIR.mkdir(exist_ok=True)

DB_FILE = DB_DIR / "institutional_quant.db"

# =====================================================
# CONNECTION
# =====================================================

def get_connection():

    return duckdb.connect(
        str(DB_FILE)
    )