# =========================================================
# RETRY ENGINE
# =========================================================

import time
import random

# =========================================================
# RETRY REQUEST
# =========================================================

def retry_request(

    func,

    retries=6,

    base_delay=3
):

    last_exception = None

    for attempt in range(retries):

        try:

            return func()

        except Exception as e:

            last_exception = e

            wait_time = (

                base_delay

                * (attempt + 1)

                +

                random.uniform(
                    1,
                    3
                )
            )

            print(

                f"Retry {attempt+1}"

                f" | Waiting {wait_time:.2f}s"

            )

            time.sleep(wait_time)

    raise last_exception
