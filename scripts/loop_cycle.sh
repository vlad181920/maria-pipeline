#!/bin/zsh
set -e

# ---- Defaults ----
EXP_DEFAULT="artifacts/earn/experiments/20250919_211414__micro-service-offer-audit-implementation"
TARGET_PRICE_DEFAULT="29"   # яку ціну ставити після перемикання
SLEEP_SEC_DEFAULT=0         # якщо >0, скрипт циклічно працює з паузою

# ---- Args ----
EXP="$EXP_DEFAULT"
TARGET_PRICE="$TARGET_PRICE_DEFAULT"
SLEEP_SEC="$SLEEP_SEC_DEFAULT"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --exp)          EXP="$2"; shift 2;;
    --target-price) TARGET_PRICE="$2"; shift 2;;
    --sleep)        SLEEP_SEC="$2"; shift 2;;
    -h|--help)
      cat <<H
Usage: scripts/loop_cycle.sh [--exp PATH] [--target-price N] [--sleep SECONDS]

Steps per iteration:
  1) metrics_aggregate
  2) auto_switch (порог вирішує tools/metrics_aggregate.py / scripts/auto_switch.sh)
  3) exp_release
  4) bus_dispatcher (рознесення подій/команд)
  5) quick_report (збереження markdown-репорту)

Defaults:
  --exp "$EXP_DEFAULT"
  --target-price $TARGET_PRICE_DEFAULT
  --sleep $SLEEP_SEC_DEFAULT  (0 = один прохід і вихід)
H
      exit 0;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
done

# ---- Helpers ----
ok(){   print -P "%F{green}✔%f $*"; }
warn(){ print -P "%F{yellow}⚠%f $*"; }
err(){  print -P "%F{red}✖%f $*"; }

LOG_DIR="artifacts/earn/logs"
mkdir -p "$LOG_DIR"

run_once() {
  local start_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  local tag="$(date -u +%Y%m%d_%H%M%S)"
  local log="$LOG_DIR/loop_$tag.log"
  {
    echo "== loop start $start_utc =="
    echo "EXP=$EXP | TARGET_PRICE=$TARGET_PRICE"

    # 1) Перерахунок метрик
    if python3 tools/metrics_aggregate.py "$EXP"; then
      ok "metrics aggregated"
    else
      err "metrics_aggregate failed"; return 1
    fi

    # 2) Автоперемикання (приймає рішення на основі metrics_summary.json)
    if scripts/auto_switch.sh "$EXP" "$TARGET_PRICE"; then
      ok "auto_switch executed"
    else
      warn "auto_switch returned non-zero (можливо, немає підстав для перемикання)"
    fi

    # 3) Реліз + подія у шину
    rel_path="$(scripts/exp_release.sh "$EXP" | tail -n1 || true)"
    [ -n "$rel_path" ] && ok "release: $rel_path" || warn "release path not captured"

    # 4) Обробити шину (події/команди)
    if python3 tools/bus_dispatcher.py; then
      ok "bus_dispatcher processed"
    else
      warn "bus_dispatcher completed with non-zero"
    fi

    # 5) Швидкий репорт
    if scripts/quick_report.sh "$EXP"; then
      ok "quick_report generated"
    else
      warn "quick_report failed"
    fi

    echo "== loop end $(date -u +"%Y-%m-%dT%H:%M:%SZ") =="
  } | tee -a "$log"
  echo "Log: $log"
}

if [ ! -d "$EXP" ]; then
  err "EXP not found: $EXP"; exit 1
fi

if [ "$SLEEP_SEC" -gt 0 ] 2>/dev/null; then
  while true; do
    run_once || true
    sleep "$SLEEP_SEC"
  done
else
  run_once
fi
