import os
import sys

RUNPOD_REFERRAL_URL = "https://runpod.io?ref=s3sprbrk"

API_KEY_ENV_VAR = "RUNPOD_API_KEY"

# See projects/mad/reference/runpod-serverless-gpu-pricing.md — ADA_24 (RTX 4090)
# is priced higher than AMPERE_24 but rated HIGH availability everywhere, which
# matters more than $0.40/hr for a first-run experience.
DEFAULT_GPU_POOL = "ADA_24"
FALLBACK_GPU_POOL = "AMPERE_24"

# Built from docker/Dockerfile — see that file for the exact model/node versions baked in.
WORKER_IMAGE = "tonifrance/mad-worker-ltxv:latest"

TEMPLATE_NAME = "mad-ltxv-worker"
ENDPOINT_NAME = "mad-ltxv-endpoint"
CONTAINER_DISK_GB = 30

ONBOARDING_MESSAGE = f"""
No {API_KEY_ENV_VAR} found.

1. Sign up to RunPod (Google SSO required) via our referral link:
   {RUNPOD_REFERRAL_URL}

2. In the RunPod dashboard, create an API key with "Restricted" permission,
   scoped to the endpoint this tool will create for you (create the key
   after running `mad provision` once, if the dashboard asks you to pick
   an endpoint to scope it to).

3. Export it and re-run:
   export {API_KEY_ENV_VAR}=your-key-here

We never see this key or your account - every job runs on your own RunPod
endpoint, billed to your own account.
""".strip()


def get_api_key() -> str:
    key = os.environ.get(API_KEY_ENV_VAR)
    if not key:
        print(ONBOARDING_MESSAGE, file=sys.stderr)
        sys.exit(1)
    return key
