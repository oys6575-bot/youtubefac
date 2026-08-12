#!/usr/bin/env bash

if [ -n "${ZSH_VERSION:-}" ]; then
  factory_script_path="${(%):-%N}"
else
  factory_script_path="${BASH_SOURCE[0]}"
fi

export FACTORY_ROOT
FACTORY_ROOT="$(cd "$(dirname "$factory_script_path")/.." && pwd -P)"

if [ -f "$FACTORY_ROOT/.env" ]; then
  set -a
  source "$FACTORY_ROOT/.env"
  set +a
fi

# Generated state is deliberately forced into this repository. Credentials in
# .env may configure providers but cannot redirect factory-owned state outside.
export OPENMONTAGE_PROJECTS_DIR="$FACTORY_ROOT/projects"
export OPENMONTAGE_CACHE_DIR="$FACTORY_ROOT/.runtime/clips_cache"
export MEDIA_CACHE_DIR="$FACTORY_ROOT/.runtime/media_cache"
export MUSIC_LIBRARY_DIR="$FACTORY_ROOT/music_library"
export TOPVIEW_HANDOFF_ROOT="$FACTORY_ROOT/projects"
export TOPVIEW_INTEGRATION_MODE="manual_ui"
export COMFYUI_SERVER_URL="${COMFYUI_SERVER_URL:-http://127.0.0.1:8188}"
export OPENMONTAGE_CACHE_MAX_GB="${OPENMONTAGE_CACHE_MAX_GB:-20}"

factory_venv="$FACTORY_ROOT/.venv"
if [ ! -x "$factory_venv/bin/python" ]; then
  printf '유튜브공장 환경이 없습니다. scripts/bootstrap-youtube-factory.sh를 먼저 실행하세요.\n' >&2
  return 1 2>/dev/null || exit 1
fi

export VIRTUAL_ENV="$factory_venv"
export PATH="$factory_venv/bin:$PATH"
unset PYTHONHOME 2>/dev/null || true

printf '유튜브공장 환경 활성화: %s\n' "$FACTORY_ROOT"
