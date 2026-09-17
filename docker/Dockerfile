FROM runpod/worker-comfyui:5.8.5-base

RUN comfy-node-install ComfyUI-LTXVideo

RUN comfy model download \
    --url https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.5.safetensors \
    --relative-path models/checkpoints \
    --filename ltx-video-2b-v0.9.5.safetensors

RUN comfy model download \
    --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors \
    --relative-path models/text_encoders \
    --filename t5xxl_fp16.safetensors
