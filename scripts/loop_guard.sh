#!/bin/bash
# loop_guard.sh
# Викликається launchd як com.maria.guard кожні ~3 хв.
# Завдання:
#  - прогнати maria health
#  - зберегти health snapshot у /tmp
#  - перевірити, що loop живий, якщо ні — підняти
#  - (WIP) вирівняти ціну/variant з TARGET_PRICE

set -euo pipefail

ts_iso() {
  date +"%Y-%m-%dT%H:%M:%S%z"
}

log() {
  # пишемо і в stdout (який launchd направляє в guard.out), і в stderr при помилці
  echo "[guard] $(ts_iso) $*"
}

err() {
  echo "[guard][ERR] $(ts_iso) $*" >&2
}

# -------------------------------------------------
# Bootstrap env, бо launchd стартує нас з майже пустим env (-i)
# -------------------------------------------------
export HOME="${HOME:-/Users/macbook}"
export PATH="${PATH:-/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin}"
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

# REPO_ROOT = директорія репо Марії (один рівень вище за scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

TMP_OUT="/tmp/maria_health.out"
TMP_ERR="/tmp/maria_health.err"

# де логуються рантайм-логи (має існувати за маніфестом)
LOG_DIR="$REPO_ROOT/artifacts/earn/logs"
mkdir -p "$LOG_DIR"

log "guard start (cwd=$REPO_ROOT)"

# -------------------------------------------------
# 1. Зняти health snapshot
# -------------------------------------------------
HEALTH_RAW_JSON=""
HEALTH_HUMAN=""
HEALTH_OK=true

if ./bin/maria health >"$TMP_OUT" 2>"$TMP_ERR"; then
  log "health executed OK"
else
  err "health returned non-zero exit code"
  HEALTH_OK=false
fi

# прочитати файл /tmp/maria_health.out і витягнути перший JSON-блок (до лінії ---),
# щоб можна було парсити loop.running та інші поля
if [[ -s "$TMP_OUT" ]]; then
  # Витягуємо JSON частину (до лінії ---)
  HEALTH_RAW_JSON="$(awk 'BEGIN{injson=0} 
    /^{/{injson=1} 
    injson{print} 
    /---/{if(injson){exit}}' "$TMP_OUT")"
else
  err "health output file empty"
  HEALTH_OK=false
fi

# -------------------------------------------------
# 2. Проаналізувати стан loop з HEALTH_RAW_JSON
#    Нам треба дізнатися: process.loop.running == true ?
# -------------------------------------------------
loop_running="unknown"
guard_running="unknown"

if [[ -n "$HEALTH_RAW_JSON" ]]; then
  # пробуємо jq
  if command -v jq >/dev/null 2>&1; then
    loop_running="$(echo "$HEALTH_RAW_JSON" | jq -r '.process.loop.running // "unknown")"
    guard_running="$(echo "$HEALTH_RAW_JSON" | jq -r '.process.guard.running // "unknown")"
  else
    # fallback: якщо jq нема (але по health бачили jq ✔, так що fallback рідко)
    loop_running="unknown(nojq)"
    guard_running="unknown(nojq)"
  fi
else
  err "no HEALTH_RAW_JSON parsed"
  HEALTH_OK=false
fi

log "loop_running=$loop_running guard_running=$guard_running health_ok=$HEALTH_OK"

# -------------------------------------------------
# 3. Якщо loop не біжить -> спробувати підняти
# launchd label: com.maria.earn.loop
# -------------------------------------------------
if [[ "$loop_running" != "true" ]]; then
  err "loop not running, attempting restart via launchctl"

  # Ми будемо робити kickstart. Якщо не вийде — спробуємо load.
  USER_ID="$(id -u)"
  if launchctl kickstart -k "gui/${USER_ID}/com.maria.earn.loop" 2>>"$TMP_ERR"; then
    log "kickstart com.maria.earn.loop OK"
  else
    err "kickstart failed, trying load"
    launchctl load "$HOME/Library/LaunchAgents/com.maria.earn.loop.plist" 2>>"$TMP_ERR" || err "load failed"
  fi
else
  log "loop is healthy"
fi

# -------------------------------------------------
# 4. (WIP) Синхронізація ціни
#    Ідея:
#      - Ціна, яка реально крутиться в loop, зараз задається у launchd аргументах --target-price 29
#      - У майбутньому ми хочемо, щоб guard тримав TARGET_PRICE з конфіга/CLI (maria price N)
#    Ми поки тільки зчитаємо це і залогуємо (без авто-правки).
# -------------------------------------------------

target_price_launchd="unknown"
if command -v launchctl >/dev/null 2>&1; then
  USER_ID2="$(id -u)"
  # знімемо current launchd print і витягнемо значення після "--target-price"
  launchctl print "gui/${USER_ID2}/com.maria.earn.loop" 2>/dev/null \
    | awk '/--target-price/{print $0}' \
    | head -n1 > "$TMP_OUT.targetprice" 2>/dev/null || true

  if [[ -s "$TMP_OUT.targetprice" ]]; then
    # приклад рядка:
    #   /Users/macbook/maria/scripts/loop_cycle.sh
    #   --sleep
    #   300
    #   --target-price
    #   29
    # ми просто витягнемо останнє число в цьому блоці
    target_price_launchd="$(awk '{last=$0} END{print last}' "$TMP_OUT.targetprice")"
  fi
fi

# Витягнемо active_price_usd з HEALTH_RAW_JSON
active_price_json="unknown"
if [[ -n "$HEALTH_RAW_JSON" ]]; then
  if command -v jq >/dev/null 2>&1; then
    active_price_json="$(echo "$HEALTH_RAW_JSON" | jq -r '.business.active_price_usd // "unknown")"
  fi
fi

log "pricing: launchd_target_price=$target_price_launchd vs business.active_price_usd=$active_price_json"
# TODO (майбутнє): якщо не співпадає, викликати `maria price <N>` або `maria switch ...`

log "guard end"
