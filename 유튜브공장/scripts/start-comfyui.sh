#!/usr/bin/env bash
set -euo pipefail

FACTORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FACTORY_ROOT
export PYTORCH_ENABLE_MPS_FALLBACK=1

COMFYUI_SOURCE="${FACTORY_ROOT}/vendor/comfyui/src"
COMFYUI_PYTHON="${FACTORY_ROOT}/.runtime/venvs/comfyui/bin/python"
COMFYUI_MODELS="${FACTORY_ROOT}/.runtime/models/comfyui"

if [[ ! -x "${COMFYUI_PYTHON}" ]]; then
  echo "Run scripts/bootstrap-comfyui.sh first." >&2
  exit 1
fi

# Apple MPS has known unsupported or corrupt FP8 paths. Require an explicit,
# independently verified opt-in instead of silently loading an FP8 model.
if [[ "${ALLOW_UNVERIFIED_MPS_FP8:-0}" != "1" ]] && \
   find "${COMFYUI_MODELS}" -type f -iname '*fp8*' -print -quit | grep -q .; then
  echo "FP8 model detected. Use an FP16/verified quantized workflow or set ALLOW_UNVERIFIED_MPS_FP8=1 after a local proof test." >&2
  exit 1
fi

exec "${COMFYUI_PYTHON}" "${COMFYUI_SOURCE}/main.py" \
  --listen 127.0.0.1 \
  --port 8188 \
  --extra-model-paths-config "${FACTORY_ROOT}/config/comfyui-extra-model-paths.yaml" \
  --input-directory "${FACTORY_ROOT}/.runtime/comfyui/input" \
  --output-directory "${FACTORY_ROOT}/.runtime/comfyui/output" \
  --temp-directory "${FACTORY_ROOT}/.runtime/comfyui/temp"
