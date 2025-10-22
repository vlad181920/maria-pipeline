#!/bin/bash
set -euo pipefail

VAR="${1:-}"
PRICE="${2:-}"

if [[ -z "${VAR}" || -z "${PRICE}" ]]; then
  echo "usage: $0 <A|B> <price>" >&2
  exit 1
fi

VAR_UP="$(echo "$VAR" | tr '[:lower:]' '[:upper:]')"
if [[ "$VAR_UP" != "A" && "$VAR_UP" != "B" ]]; then
  echo "error: variant must be A or B" >&2
  exit 2
fi
if ! [[ "$PRICE" =~ ^[0-9]+$ ]]; then
  echo "error: price must be integer (e.g. 27)" >&2
  exit 3
fi

WD="$(cd "$(dirname "$0")/.." && pwd)"
BUS_DIR="$WD/bus"
CMDS="$BUS_DIR/commands.jsonl"
mkdir -p "$BUS_DIR"

TS="$(python3 - <<'PY'
import datetime
print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
PY
)"

# Кладемо команду в чергу
printf '{"ts":"%s","type":"auto_switch","variant":"%s","price":%s}\n' "$TS" "$VAR_UP" "$PRICE" >> "$CMDS"

echo "queued auto switch (action) -> ${VAR_UP} (${PRICE})"
