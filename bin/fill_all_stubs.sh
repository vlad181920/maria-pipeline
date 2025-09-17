#!/usr/bin/env bash
set -euo pipefail
MARIA_HOME="${MARIA_HOME:-$HOME/Desktop/Марія}"
python3 "$MARIA_HOME/tools/auto_fill_stub.py"
