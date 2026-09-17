# mad-cli

Generate video with **LTX-Video** on **your own RunPod account** — no
dashboard clicks, no 30-60 minute run caps, no credit decay. One command
turns a text prompt into a `.webm`.

```
uvx --from "git+https://github.com/kremenmobtans-oss/mad-cli.git" mad provision
uvx --from "git+https://github.com/kremenmobtans-oss/mad-cli.git" mad run --prompt "a drone shot rising over a foggy alpine lake at sunrise"
```

(no [uv](https://docs.astral.sh/uv/)? `pipx install git+https://github.com/kremenmobtans-oss/mad-cli.git` or plain `pip install git+https://github.com/kremenmobtans-oss/mad-cli.git` both work the same way.)

## Why this exists

Every other hosted ComfyUI service (Comfy Cloud, ThinkDiffusion, RunComfy,
ComfyDeploy) bills you through their own markup on top of GPU cost, and
caps how long a single run can take. This tool does neither: it runs
entirely on **your own** RunPod account, under **your own** API key. You
pay RunPod directly — the same price as if you'd set this up by hand
yourself — and RunPod pays *us* a small referral commission on your usage
if you signed up through [our referral link](https://runpod.io?ref=s3sprbrk).
No markup, no separate bill, no vendor lock-in: it's your endpoint, in
your account, and you can inspect or delete it from the RunPod dashboard
at any time.

## Security & privacy

- **We never see your prompts, your videos, or your RunPod bill.** Every
  job runs on an endpoint created directly under your own account — this
  tool only talks to RunPod's API on your behalf, using a key you provide
  and that never leaves your machine.
- **Use a Restricted, endpoint-scoped API key, not your all-access key.**
  RunPod supports minting a key scoped to a single endpoint. Start with
  an "All"-permission key only for the one-time `mad provision` step
  (it needs to create the endpoint), then switch to a Restricted key
  scoped to that endpoint for everyday `mad run` use.
- **This repo is the whole tool.** Nothing is fetched or executed beyond
  what you can read in `src/mad_cli/` and `docker/Dockerfile` before you
  run it.

## Setup

1. Sign up to RunPod via [our referral link](https://runpod.io?ref=s3sprbrk)
   (Google SSO). Signing up this way is what funds this tool staying free
   and open source — using an existing RunPod account works too, it just
   doesn't support the project.
2. Create a RunPod API key (Settings → API Keys) and export it:
   ```
   export RUNPOD_API_KEY=your-key-here
   ```
3. Install and run — no separate install step needed with `uvx`:
   ```
   uvx --from "git+https://github.com/kremenmobtans-oss/mad-cli.git" mad provision
   uvx --from "git+https://github.com/kremenmobtans-oss/mad-cli.git" mad run --prompt "..."
   ```
   or install it once with `pipx`/`pip` and just call `mad` from then on:
   ```
   pipx install git+https://github.com/kremenmobtans-oss/mad-cli.git
   mad provision
   mad run --prompt "..."
   ```

The worker image (`tonifrance/mad-worker-ltxv:latest`, built from
[`docker/Dockerfile`](docker/Dockerfile)) is already published — you
don't need to build anything unless you want to change the model or
inspect the image yourself:

```
docker build -t your-registry/mad-worker-ltxv:latest docker/
docker push your-registry/mad-worker-ltxv:latest
```
then set `WORKER_IMAGE` in `src/mad_cli/config.py` to match.

## Status

Verified end to end against a live RunPod endpoint: `mad provision` →
`mad run --prompt "..."` → a real, playable `.webm`, no dashboard clicks.
GPU execution takes well under a minute; queue time varies with RunPod's
`ADA_24` pool availability at the time.

Known gaps:
- Only the default LTX-Video 0.9.5 resolution/length has been validated
  end to end — other `--width`/`--height`/`--length` combinations haven't
  been tried yet.
- One workflow only (LTX-Video). More may be added later.

## License

MIT — see [LICENSE](LICENSE).
