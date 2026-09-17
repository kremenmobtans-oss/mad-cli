# mad-cli

Generate video with LTX-Video on **your own** RunPod account — no dashboard
clicks, no run-time caps, no credit expiry. See
[the project's `how-it-works` doc](../product/how-it-works.md) for why it
works this way (short version: RunPod pays *us* a referral commission on
your usage; you pay RunPod directly, same as if you'd set this up yourself).

> **Status: first real end-to-end run succeeded 2026-09-17.** On a fresh
> RunPod account (reusing a key from another of the project owner's
> RunPod-using projects, kept separate from any referred account per the
> project's own testing guidance), with zero dashboard clicks:
> `mad provision` created endpoint `keldmyypizq77q` on `ADA_24`, then
> `mad run --prompt "a drone shot rising over a foggy alpine lake at
> sunrise"` produced a real, playable `.webm` file. GPU execution itself
> was fast and cheap (**29.7s**); the queue delay was long (**533.6s**)
> because `ADA_24` had zero spare capacity at the time — RunPod spun up 7
> workers across 3 data centers before one finished pulling the 24.7GB
> image and went healthy. This is the exact `ADA_24`-availability risk
> the launch plan already flagged, not a bug — see "Risks" there for the
> `AMPERE_24` fallback if it recurs often.
>
> **A real bug was found and fixed during this run**:
> `RunPodClient.list_endpoints()` read the wrong JSON key
> (`"items"` instead of the API's actual `"endpoints"`), so it always
> returned an empty list — `mad run`'s auto-provision path could never
> find an endpoint that already existed, and tried (and failed, on a
> template-name conflict) to recreate one every time. Fixed in
> `src/mad_cli/runpod_client.py`.
>
> **`docker/Dockerfile` build+push status: done, matches `config.WORKER_IMAGE`.**
> `mad-worker-ltxv:latest` (24.7GB) built locally, pushed to Docker Hub as
> `tonifrance/mad-worker-ltxv:latest` — digest
> `sha256:7965e9d94c35e7b20a691b4f82b396e7865b5b653153db8d2e698c1f8a9eb3b0`.
> The build itself took three attempts on this machine, none caused by
> the Dockerfile: a host disk-space I/O error (fixed by moving Docker
> Desktop's disk to a drive with more room), a power loss that corrupted
> the build cache, and a transient DNS failure inside Docker's network
> after a WSL2 reset.
>
> See [the launch plan](../product/mvp-launch-plan.md) for what's left
> before this can go to a real stranger (packaging, the real referral
> link, testing on a *separate* non-referred account for the public
> launch itself).

## Setup

1. Sign up to RunPod via [our referral link](https://runpod.io?ref=s3sprbrk)
   (Google SSO required).
2. Build and push the worker image (until this is published for you):
   ```
   docker build -t <your-registry>/mad-worker-ltxv:latest docker/
   docker push <your-registry>/mad-worker-ltxv:latest
   ```
   and update `WORKER_IMAGE` in `src/mad_cli/config.py` to match.
3. Create a RunPod API key and export it:
   ```
   export RUNPOD_API_KEY=your-key-here
   ```
   (Start with an "All" permission key for the first `provision` run, then
   switch to a "Restricted" key scoped to the created endpoint — see
   [the key-custody reference note](../reference/runpod-provisioning-and-key-custody.md).)

## Usage

```
pip install -e .
mad provision              # idempotent — safe to re-run
mad run --prompt "a drone shot rising over a foggy alpine lake"
```

## Known gaps before this can be handed to a real user

- ~~The LTX-Video workflow's field names need a real validation run~~ —
  **confirmed working 2026-09-17** against a live `ADA_24` endpoint (see
  the status note above): `mad run` produced a real, playable `.webm`
  with no code changes needed. `output.images` (not `videos`/`files`)
  is indeed what fires, as predicted from source inspection beforehand.
- `WORKER_IMAGE` and the referral link in `config.py` are both now real
  (no more placeholders).
- Only one workflow (LTX-Video 0.9.5, one fixed resolution/length set of
  defaults) has been validated end to end — different `--width`/`--height`/
  `--length`/`--prompt` combinations, and repeat runs against a warm
  (already-scaled-up) endpoint, haven't been tried yet.
