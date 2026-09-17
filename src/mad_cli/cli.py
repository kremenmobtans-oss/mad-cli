import argparse
import base64
import sys
import time

from . import config
from .runpod_client import RunPodClient, RunPodError
from .workflow import build_workflow


def _find_existing_endpoint(client: RunPodClient) -> dict | None:
    for ep in client.list_endpoints():
        if ep.get("name") == config.ENDPOINT_NAME:
            return ep
    return None


def cmd_provision(client: RunPodClient) -> str:
    existing = _find_existing_endpoint(client)
    if existing:
        print(f"Endpoint already exists: {existing['id']}")
        return existing["id"]

    print(f"Creating template from {config.WORKER_IMAGE} ...")
    template = client.create_template(
        name=config.TEMPLATE_NAME,
        image=config.WORKER_IMAGE,
        disk_gb=config.CONTAINER_DISK_GB,
    )

    print(f"Creating endpoint on GPU pool {config.DEFAULT_GPU_POOL} ...")
    try:
        endpoint = client.create_endpoint(
            name=config.ENDPOINT_NAME,
            template_id=template["id"],
            gpu_pool=config.DEFAULT_GPU_POOL,
        )
    except RunPodError as e:
        print(f"{config.DEFAULT_GPU_POOL} unavailable ({e}); retrying on {config.FALLBACK_GPU_POOL}")
        endpoint = client.create_endpoint(
            name=config.ENDPOINT_NAME,
            template_id=template["id"],
            gpu_pool=config.FALLBACK_GPU_POOL,
        )

    print(f"Endpoint created: {endpoint['id']}")
    return endpoint["id"]


def cmd_run(client: RunPodClient, endpoint_id: str, args: argparse.Namespace) -> None:
    workflow = build_workflow(
        prompt=args.prompt,
        width=args.width,
        height=args.height,
        length=args.length,
        seed=args.seed,
    )

    print("Submitting job (cold start can take a few minutes on first run) ...")
    job = client.submit_job(endpoint_id, workflow)
    job_id = job["id"]

    def on_poll(status: dict) -> None:
        print(f"  status: {status.get('status')}", file=sys.stderr)

    result = client.wait_for_completion(endpoint_id, job_id, on_poll=on_poll, timeout=args.timeout)

    if result.get("status") != "COMPLETED":
        print(f"Job did not complete: {result}", file=sys.stderr)
        sys.exit(1)

    delay = result.get("delayTime", 0) / 1000
    exec_time = result.get("executionTime", 0) / 1000
    print(f"Done. Queue delay: {delay:.1f}s, GPU execution time: {exec_time:.1f}s.")

    output = result.get("output", {})
    saved_any = False
    for key in ("images", "videos", "files"):
        for item in output.get(key, []):
            if item.get("type") == "base64":
                out_path = args.out or item.get("filename", "output.bin")
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(item["data"]))
                print(f"Saved: {out_path}")
                saved_any = True
            elif item.get("type") == "s3_url":
                print(f"Result at: {item['data']}")
                saved_any = True

    if not saved_any:
        print(
            "Could not find a known output shape (images/videos/files) — "
            "printing the raw output so nothing is silently lost:",
            file=sys.stderr,
        )
        print(output, file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(prog="mad", description="LTX-Video generation on your own RunPod account.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("provision", help="Create the RunPod endpoint under your own account (idempotent).")

    run_parser = sub.add_parser("run", help="Generate a video.")
    run_parser.add_argument("--prompt", required=True)
    run_parser.add_argument("--width", type=int, default=768)
    run_parser.add_argument("--height", type=int, default=512)
    run_parser.add_argument("--length", type=int, default=97, help="Frame count.")
    run_parser.add_argument("--seed", type=int, default=42)
    run_parser.add_argument("--timeout", type=int, default=1800, help="Seconds to wait for the job.")
    run_parser.add_argument("--out", help="Output file path (defaults to the worker's own filename).")

    args = parser.parse_args()
    client = RunPodClient(config.get_api_key())

    try:
        if args.command == "provision":
            cmd_provision(client)
        elif args.command == "run":
            endpoint = _find_existing_endpoint(client)
            if not endpoint:
                print("No endpoint found - provisioning one first.")
                endpoint_id = cmd_provision(client)
            else:
                endpoint_id = endpoint["id"]
            cmd_run(client, endpoint_id, args)
    except RunPodError as e:
        print(f"RunPod API error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
