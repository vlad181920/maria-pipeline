#!/bin/zsh
# robust guard runner for launchd env -i

# --- bootstrap env (ніяких помилок на unset) ---
export HOME="${HOME:-/Users/macbook}"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

# опційно допоможемо імпортам для user-site (включно з 3.13)
export PYTHONPATH="$HOME/Library/Python/3.13/lib/python/site-packages:$HOME/Library/Python/3.11/lib/python/site-packages:$HOME/Library/Python/3.10/lib/python/site-packages:$PYTHONPATH"

set -Eeuo pipefail

WORKDIR="${WORKDIR:-$HOME/maria}"
LOGDIR="$WORKDIR/artifacts/earn/logs"
mkdir -p "$LOGDIR"
OUT="/tmp/maria_health.out"
ERR="/tmp/maria_health.err"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

cd "$WORKDIR" || { echo "[guard] $(ts) ERROR: no WORKDIR $WORKDIR" >>"$LOGDIR/guard.err"; exit 1; }

# гарантуємо jsonschema (в user site)
if ! python3 -c "import jsonschema" >/dev/null 2>&1; then
  python3 -m pip install --user --quiet jsonschema || true
fi

# health
if ./scripts/health.sh >"$OUT" 2>"$ERR"; then
  echo "[guard] $(ts) health OK" >>"$LOGDIR/guard.out"
else
  echo "[guard] $(ts) health FAIL → намагаюсь автолікування (міграції схем)" >>"$LOGDIR/guard.out"
  EV="$WORKDIR/artifacts/earn/experiments/20250919_211414__micro-service-offer-audit-implementation/events.jsonl"
  if [ -f "$EV" ]; then
    python3 tools/events_migrate_schema.py "$EV" || true
  else
    echo "[guard] $(ts) WARN: no events.jsonl at $EV" >>"$LOGDIR/guard.out"
  fi
  python3 tools/commands_migrate_schema.py || true
  if ./scripts/health.sh >"$OUT" 2>"$ERR"; then
    echo "[guard] $(ts) health OK після авто-міграцій" >>"$LOGDIR/guard.out"
  else
    echo "[guard] $(ts) health STILL FAIL — залишаю логи у $OUT,$ERR" >>"$LOGDIR/guard.out"
  fi
fi

# слідкуємо за loop-агентом
if ! launchctl print "gui/$(id -u)/com.maria.earn.loop" >/dev/null 2>&1; then
  echo "[guard] $(ts) launchd job missing → re-apply" >>"$LOGDIR/guard.out"
  "$WORKDIR/scripts/launchd_apply.sh" --workdir "$WORKDIR" --interval 300 --target-price 29 >/dev/null 2>&1 || true
fi

# статус + “свіжість” логів
if launchctl print "gui/$(id -u)/com.maria.earn.loop" >/dev/null 2>&1; then
  echo "[guard] $(ts) agent running" >>"$LOGDIR/guard.out"
else
  echo "[guard] $(ts) agent NOT running" >>"$LOGDIR/guard.out"
fi
if [ -f "$WORKDIR/artifacts/earn/logs/launchd.out" ]; then
  age=$(( $(date +%s) - $(stat -f %m "$WORKDIR/artifacts/earn/logs/launchd.out") ))
  echo "[guard] $(ts) stdout log fresh (${age}s)" >>"$LOGDIR/guard.out"
fi

echo "[guard] $(ts) guard done." >>"$LOGDIR/guard.out"
