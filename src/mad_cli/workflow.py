DEFAULT_NEGATIVE_PROMPT = (
    "low quality, worst quality, deformed, distorted, disfigured, motion smear, "
    "motion artifacts, fused fingers, bad anatomy, weird hand, ugly"
)

# Converted by hand from the official UI-format workflow at
# comfyanonymous.github.io/ComfyUI_examples/ltxv/ltxv_text_to_video_0.9.5.json
# (fetched 2026-09-16) into the flat API format worker-comfyui expects. The
# graph topology and widget *values* are taken directly from that source; the
# widget *field names* for the less common LTX-specific nodes (LTXVConditioning,
# LTXVScheduler, EmptyLTXVLatentVideo) are inferred from ComfyUI's usual naming
# conventions, not confirmed against ComfyUI-LTXVideo's actual node source —
# this has NOT been run against a live worker-comfyui endpoint yet. Treat a
# validation run (see mvp-launch-plan.md) as required before trusting this in
# front of a real user.


def build_workflow(
    prompt: str,
    negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
    width: int = 768,
    height: int = 512,
    length: int = 97,
    seed: int = 42,
) -> dict:
    return {
        "38": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": "t5xxl_fp16.safetensors", "type": "ltxv", "device": "default"},
        },
        "44": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "ltx-video-2b-v0.9.5.safetensors"},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["38", 0]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_prompt, "clip": ["38", 0]},
        },
        "69": {
            "class_type": "LTXVConditioning",
            "inputs": {"positive": ["6", 0], "negative": ["7", 0], "frame_rate": 25},
        },
        "70": {
            "class_type": "EmptyLTXVLatentVideo",
            "inputs": {"width": width, "height": height, "length": length, "batch_size": 1},
        },
        "71": {
            "class_type": "LTXVScheduler",
            "inputs": {
                "latent": ["70", 0],
                "steps": 30,
                "max_shift": 2.05,
                "base_shift": 0.95,
                "stretch": True,
                "terminal": 0.1,
            },
        },
        "73": {
            "class_type": "KSamplerSelect",
            "inputs": {"sampler_name": "res_multistep"},
        },
        "72": {
            "class_type": "SamplerCustom",
            "inputs": {
                "model": ["44", 0],
                "positive": ["69", 0],
                "negative": ["69", 1],
                "sampler": ["73", 0],
                "sigmas": ["71", 0],
                "latent_image": ["70", 0],
                "add_noise": True,
                "noise_seed": seed,
                "cfg": 3,
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["72", 0], "vae": ["44", 2]},
        },
        "77": {
            "class_type": "SaveWEBM",
            "inputs": {"images": ["8", 0], "filename_prefix": "mad", "codec": "vp9", "fps": 24, "crf": 18},
        },
    }
