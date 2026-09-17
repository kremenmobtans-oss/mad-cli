import time

import requests

# Verified directly against RunPod's own OpenAPI spec (api.runpod.io/v2/openapi.json)
# on 2026-09-16 — the management API and the job-execution API live on two
# different hosts, which is easy to get wrong by guessing.
MANAGEMENT_BASE = "https://api.runpod.io/v2"
JOB_BASE = "https://api.runpod.ai/v2"


class RunPodError(RuntimeError):
    pass


class RunPodClient:
    def __init__(self, api_key: str):
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, url: str, **kwargs):
        resp = requests.request(method, url, headers=self._headers, timeout=30, **kwargs)
        if resp.status_code >= 400:
            raise RunPodError(f"{method} {url} -> {resp.status_code}: {resp.text}")
        if not resp.content:
            return {}
        return resp.json()

    def list_endpoints(self) -> list[dict]:
        result = self._request("GET", f"{MANAGEMENT_BASE}/serverless")
        return result if isinstance(result, list) else result.get("endpoints", [])

    def create_template(self, name: str, image: str, disk_gb: int) -> dict:
        body = {"name": name, "image": image, "disk": disk_gb, "serverless": True}
        return self._request("POST", f"{MANAGEMENT_BASE}/templates", json=body)

    def create_endpoint(
        self,
        name: str,
        template_id: str,
        gpu_pool: str,
        idle_timeout: int = 5,
        max_workers: int = 3,
    ) -> dict:
        body = {
            "name": name,
            "type": "QUEUE",
            "templateId": template_id,
            "gpu": {"pools": [gpu_pool]},
            "scaling": {"type": "QUEUE_DELAY", "queueDelay": 4},
            "workers": {"min": 0, "max": max_workers, "idleTimeout": idle_timeout},
        }
        return self._request("POST", f"{MANAGEMENT_BASE}/serverless", json=body)

    def submit_job(self, endpoint_id: str, workflow: dict) -> dict:
        payload = {"input": {"workflow": workflow}}
        return self._request("POST", f"{JOB_BASE}/{endpoint_id}/run", json=payload)

    def get_status(self, endpoint_id: str, job_id: str) -> dict:
        return self._request("GET", f"{JOB_BASE}/{endpoint_id}/status/{job_id}")

    def wait_for_completion(
        self,
        endpoint_id: str,
        job_id: str,
        poll_interval: int = 5,
        timeout: int = 1800,
        on_poll=None,
    ) -> dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            status = self.get_status(endpoint_id, job_id)
            if on_poll:
                on_poll(status)
            if status.get("status") in ("COMPLETED", "FAILED"):
                return status
            time.sleep(poll_interval)
        raise RunPodError(f"job {job_id} did not finish within {timeout}s")
