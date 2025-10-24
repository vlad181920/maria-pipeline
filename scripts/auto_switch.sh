#!/bin/bash
set -euo pipefail

# --- parse args: підтримуємо і позиційні "A 27", і прапорці "--variant A --price 27"
VAR=""; PRICE=""
if [[ $# -ge 1 && "$1" =~ ^[AaBb]$ ]]; then
  VAR="$1"; PRICE="${2:-}"
else
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -v|--variant) VAR="${2:-}"; shift 2 ;;
      -p|--price)   PRICE="${2:-}"; shift 2 ;;
      *) shift ;;
    esac
  done
fi

# Якщо loop викликав без аргументів — тиха no-op і успішний вихід.
if [[ -z "${VAR:-}" || -z "${PRICE:-}" ]]; then
  echo "auto_switch: noop (no variant/price provided by caller)"
  exit 0
fi

VAR="$(echo -n "$VAR" | tr '[:lower:]' '[:upper:]')"
if [[ "$VAR" != "A" && "$VAR" != "B" ]]; then
  echo "error: variant must be A or B" >&2
  exit 2
fi
if ! [[ "$PRICE" =~ ^[0-9]+$ ]]; then
  echo "error: price must be integer" >&2
  exit 3
fi

WD="$(cd "$(dirname "$0")/.." && pwd)"
BUS_DIR="$WD/bus"
CMDS="$BUS_DIR/commands.jsonl"
mkdir -p "$BUS_DIR"

TS_UTC="$(python3 - <<'PY'
import datetime
print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
PY
)"

# Пишемо валідну команду за схемою bus (ts_utc, action, schema_ver, args)
printf '{"ts_utc":"%s","action":"switch_variant","schema_ver":"v1","initiator":"cli","args":{"variant":"%s","price":%s}}\n' \
  "$TS_UTC" "$VAR" "$PRICE" >> "$CMDS"

echo "queued auto switch -> ${VAR} (@${PRICE})"
