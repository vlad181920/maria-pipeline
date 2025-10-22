#!/bin/bash
set -euo pipefail

# --- parse args: support "A 27" and "--variant A --price 27"
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

VAR="$(echo -n "${VAR:-}" | tr '[:lower:]' '[:upper:]')"
[[ "$VAR" == "A" || "$VAR" == "B" ]] || { echo "error: variant must be A or B" >&2; exit 2; }
[[ "${PRICE:-}" =~ ^[0-9]+$ ]]      || { echo "error: price must be integer" >&2; exit 3; }

WD="$(cd "$(dirname "$0")/.." && pwd)"
BUS_DIR="$WD/bus"
CMDS="$BUS_DIR/commands.jsonl"
mkdir -p "$BUS_DIR"

TS_UTC="$(python3 - <<'PY'
import datetime
print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
PY
)"

# BUS schema expects: ts_utc, action, schema_ver, (optional initiator), args{}
# action must be one of: aggregate_metrics | publish_release | switch_variant | generate_report | sync_manifest | validate_schema
printf '{"ts_utc":"%s","action":"switch_variant","schema_ver":"v1","initiator":"cli","args":{"variant":"%s","price":%s}}\n' \
  "$TS_UTC" "$VAR" "$PRICE" >> "$CMDS"

echo "queued auto switch -> ${VAR} (@${PRICE})"
