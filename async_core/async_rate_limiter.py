import asyncio

# =========================================================
# GLOBAL SEMAPHORE
# =========================================================

RATE_LIMITER = asyncio.Semaphore(5)