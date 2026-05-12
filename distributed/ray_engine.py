import ray

# =========================================================
# INITIALIZE RAY
# =========================================================

def initialize_ray():

    if not ray.is_initialized():

        ray.init(

            ignore_reinit_error=True,

            include_dashboard=False
        )

        print("Ray Initialized")

# =========================================================
# SHUTDOWN RAY
# =========================================================

def shutdown_ray():

    if ray.is_initialized():

        ray.shutdown()

        print("Ray Shutdown")