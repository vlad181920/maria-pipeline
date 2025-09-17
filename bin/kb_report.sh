#!/usr/bin/env bash
set -euo pipefail

MARIA_HOME="${MARIA_HOME:-$HOME/Desktop/Марія}"
INS_DIR="$MARIA_HOME/artifacts/insights"
TMP="$MARIA_HOME/artifacts/tmp"
mkdir -p "$TMP"

python3 "$MARIA_HOME/tools/kb_report.py" > "$TMP/kb.json"
cat "$TMP/kb.json"
