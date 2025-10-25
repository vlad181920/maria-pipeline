#!/bin/zsh
set -euo pipefail

CMD="${1:-}"
EVERY_MIN="${2:-}"
[[ -z "${EVERY_MIN}" ]] && EVERY_MIN=10  # дефолт 10 хв

cd "$(dirname "$0")/../.."
export MARIA_HOME="$PWD"

LOG_DIR="artifacts/logs"
PID_DIR="artifacts/pids"
FLAG_DIR="artifacts/flags"
mkdir -p "$LOG_DIR" "$PID_DIR" "$FLAG_DIR"

LOG_FILE="$LOG_DIR/earn_autonomy_daemon.log"
PID_FILE="$PID_DIR/earn_autonomy_daemon.pid"
STOP_FLAG="$FLAG_DIR/earn_autonomy.stop"

rotate_logs() {
  # простенька ротація до 5 файлів
  local max_size=$((1024*1024)) # 1MB
  if [[ -f "$LOG_FILE" ]] && (( $(stat -f%z "$LOG_FILE") > max_size )); then
    for i in 5 4 3 2 1; do
      [[ -f "$LOG_FILE.$i" ]] && mv "$LOG_FILE.$i" "$LOG_FILE.$((i+1))" || true
    done
    mv "$LOG_FILE" "$LOG_FILE.1"
    : > "$LOG_FILE"
  fi
}

is_running() {
  [[ -f "$PID_FILE" ]] || return 1
  local pid; pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
  [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1
}

start_loop() {
  if is_running; then
    echo "already running (PID=$(cat "$PID_FILE"))"
    exit 0
  fi
  : > "$STOP_FLAG" # створимо, але порожній; видаленням будемо зупиняти
  rm -f "$STOP_FLAG" # зупинятимемо появою цього файлу; старт — без нього

  (
    echo "[$(date '+%F %T')] earn_daemon START (every ${EVERY_MIN} min)" >> "$LOG_FILE"
    while true; do
      # перевірка флагу зупинки
      if [[ -f "$STOP_FLAG" ]]; then
        echo "[$(date '+%F %T')] earn_daemon STOP FLAG detected — exiting" >> "$LOG_FILE"
        break
      fi
      rotate_logs
      echo "[$(date '+%F %T')] tick begin" >> "$LOG_FILE"
      tools/earn_autonomy/earn_tick.sh >> "$LOG_FILE" 2>&1 || echo "[$(date '+%F %T')] tick error (continuing)" >> "$LOG_FILE"
      echo "[$(date '+%F %T')] tick end" >> "$LOG_FILE"
      sleep $((EVERY_MIN*60))
    done
    echo "[$(date '+%F %T')] earn_daemon EXIT" >> "$LOG_FILE"
  ) &
  echo $! > "$PID_FILE"
  echo "started PID=$(cat "$PID_FILE") every=${EVERY_MIN}m"
}

stop_loop() {
  if ! is_running; then
    echo "not running"
    rm -f "$PID_FILE" "$STOP_FLAG"
    exit 0
  fi
  touch "$STOP_FLAG"
  local pid; pid=$(cat "$PID_FILE")
  echo "stopping PID=$pid ..."
  # дамо 2 секунди на м'яку зупинку
  for i in 1 2 3 4 5; do
    if ! ps -p "$pid" >/dev/null 2>&1; then
      rm -f "$PID_FILE" "$STOP_FLAG"
      echo "stopped"
      exit 0
    fi
    sleep 1
  done
  # форсова зупинка
  kill "$pid" 2>/dev/null || true
  rm -f "$PID_FILE" "$STOP_FLAG"
  echo "killed"
}

status_loop() {
  if is_running; then
    echo "running PID=$(cat "$PID_FILE")"
  else
    echo "stopped"
  fi
  [[ -f "$LOG_FILE" ]] && tail -n 10 "$LOG_FILE" || true
}

case "$CMD" in
  start) start_loop ;;
  stop)  stop_loop ;;
  status) status_loop ;;
  run-once) tools/earn_autonomy/earn_tick.sh ;;
  *)
    echo "usage: $0 {start [EVERY_MIN]|stop|status|run-once}"
    exit 1
    ;;
esac
