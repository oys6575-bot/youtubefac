#!/bin/sh
set -eu

FACTORY_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
RUNTIME_DIR=${YTF_MOBILE_RUNTIME_DIR:-"$FACTORY_ROOT/.runtime/mobile-dashboard/tailscale"}
SOCKET_DIR=${YTF_MOBILE_SOCKET_DIR:-"/tmp/ytf-mobile-$(id -u)"}
SOCKET="$SOCKET_DIR/tailscaled.sock"
STATE="$RUNTIME_DIR/tailscaled.state"
STATE_DIR="$RUNTIME_DIR/state"
PID_FILE="$RUNTIME_DIR/tailscaled.pid"
LOG_FILE="$RUNTIME_DIR/tailscaled.log"
PORT=${YTF_MOBILE_PORT:-8787}
TAILSCALE_BIN=${TAILSCALE_BIN:-/opt/homebrew/bin/tailscale}
TAILSCALED_BIN=${TAILSCALED_BIN:-/opt/homebrew/opt/tailscale/bin/tailscaled}

mkdir -p "$RUNTIME_DIR" "$STATE_DIR" "$SOCKET_DIR"

is_running() {
  [ -f "$PID_FILE" ] && kill -0 "$(sed -n '1p' "$PID_FILE")" 2>/dev/null
}

daemon_healthy() {
  [ -S "$SOCKET" ] && "$TAILSCALE_BIN" --socket="$SOCKET" status --json >/dev/null 2>&1
}

start_daemon() {
  if daemon_healthy; then
    printf '%s\n' "launchd의 유튜브공장 Tailscale daemon을 사용합니다."
    return
  fi
  if is_running; then
    printf '%s\n' "유튜브공장 Tailscale daemon은 이미 실행 중입니다."
    return
  fi
  "$TAILSCALED_BIN" \
    --tun=userspace-networking \
    --state="$STATE" \
    --statedir="$STATE_DIR" \
    --socket="$SOCKET" \
    >"$LOG_FILE" 2>&1 &
  daemon_pid=$!
  printf '%s\n' "$daemon_pid" >"$PID_FILE"
  attempt=0
  while [ ! -S "$SOCKET" ] && [ "$attempt" -lt 50 ]; do
    sleep 0.1
    attempt=$((attempt + 1))
  done
  if [ ! -S "$SOCKET" ]; then
    printf '%s\n' "전용 Tailscale socket을 만들지 못했습니다. $LOG_FILE 확인" >&2
    exit 1
  fi
  printf '%s\n' "전용 Tailscale daemon 시작 완료: $SOCKET"
}

case "${1:-status}" in
  start-daemon)
    start_daemon
    ;;
  login)
    start_daemon
    "$TAILSCALE_BIN" --socket="$SOCKET" up --hostname=youtube-factory --qr
    ;;
  serve)
    start_daemon
    curl --fail --silent --show-error "http://127.0.0.1:$PORT/api/health" >/dev/null
    "$TAILSCALE_BIN" --socket="$SOCKET" serve --bg "http://127.0.0.1:$PORT"
    "$TAILSCALE_BIN" --socket="$SOCKET" serve status --json
    ;;
  status)
    start_daemon
    "$TAILSCALE_BIN" --socket="$SOCKET" status --json
    "$TAILSCALE_BIN" --socket="$SOCKET" serve status --json
    ;;
  reset-serve)
    "$TAILSCALE_BIN" --socket="$SOCKET" serve reset
    ;;
  stop-daemon)
    if is_running; then
      daemon_pid=$(sed -n '1p' "$PID_FILE")
      kill "$daemon_pid"
      rm -f "$PID_FILE"
      printf '%s\n' "유튜브공장 전용 Tailscale daemon을 중지했습니다."
    fi
    ;;
  *)
    printf '%s\n' "사용법: $0 {start-daemon|login|serve|status|reset-serve|stop-daemon}" >&2
    exit 2
    ;;
esac
