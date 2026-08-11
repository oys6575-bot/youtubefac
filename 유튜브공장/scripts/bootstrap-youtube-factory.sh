#!/usr/bin/env bash
set -euo pipefail

factory_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
factory_root="$(cd "$factory_script_dir/.." && pwd -P)"

if ! command -v python3.11 >/dev/null 2>&1; then
  printf 'Python 3.11이 필요합니다. Homebrew python@3.11을 설치한 뒤 다시 실행하세요.\n' >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  printf 'Node.js와 npm이 필요합니다. 설치한 뒤 다시 실행하세요.\n' >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  printf 'FFmpeg와 ffprobe가 필요합니다. 설치한 뒤 다시 실행하세요.\n' >&2
  exit 1
fi

mkdir -p \
  "$factory_root/.runtime/clips_cache" \
  "$factory_root/.runtime/media_cache" \
  "$factory_root/projects" \
  "$factory_root/music_library"

if [ ! -x "$factory_root/.venv/bin/python" ]; then
  python3.11 -m venv "$factory_root/.venv"
fi

"$factory_root/.venv/bin/python" -m pip install --upgrade pip
"$factory_root/.venv/bin/python" -m pip install -r "$factory_root/requirements-dev.txt"
npm ci --prefix "$factory_root/remotion-composer"

printf '유튜브공장 독립 환경 설치 완료: %s\n' "$factory_root"
printf '다음 명령: source "%s/scripts/activate-youtube-factory.sh"\n' "$factory_root"
