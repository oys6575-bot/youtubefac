#!/usr/bin/env bash
set -euo pipefail

FACTORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMFYUI_SOURCE="${FACTORY_ROOT}/vendor/comfyui/src"
COMFYUI_VENV="${FACTORY_ROOT}/.runtime/venvs/comfyui"
COMFYUI_MODELS="${FACTORY_ROOT}/.runtime/models/comfyui"

if [[ ! -f "${COMFYUI_SOURCE}/main.py" ]]; then
  echo "Vendored ComfyUI source is missing: ${COMFYUI_SOURCE}" >&2
  exit 1
fi
if ! command -v python3.11 >/dev/null 2>&1; then
  echo "Python 3.11 is required for the isolated ComfyUI runtime." >&2
  exit 1
fi

mkdir -p \
  "${COMFYUI_MODELS}/checkpoints" \
  "${COMFYUI_MODELS}/diffusion_models" \
  "${COMFYUI_MODELS}/text_encoders" \
  "${COMFYUI_MODELS}/clip_vision" \
  "${COMFYUI_MODELS}/vae" \
  "${COMFYUI_MODELS}/loras" \
  "${COMFYUI_MODELS}/controlnet" \
  "${COMFYUI_MODELS}/upscale_models" \
  "${COMFYUI_MODELS}/audio_encoders" \
  "${FACTORY_ROOT}/.runtime/comfyui/custom_nodes" \
  "${FACTORY_ROOT}/.runtime/comfyui/input" \
  "${FACTORY_ROOT}/.runtime/comfyui/output" \
  "${FACTORY_ROOT}/.runtime/comfyui/temp"

if [[ ! -x "${COMFYUI_VENV}/bin/python" ]]; then
  python3.11 -m venv "${COMFYUI_VENV}"
fi

"${COMFYUI_VENV}/bin/python" -m pip install --upgrade pip
"${COMFYUI_VENV}/bin/python" -m pip install -r "${COMFYUI_SOURCE}/requirements.txt"

echo "ComfyUI runtime prepared inside the YouTube Factory."
echo "Model weights were not downloaded. Review config/local-models.lock.json first."
