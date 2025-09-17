#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p artifacts/logs
BASE_SLEEP="${BASE_SLEEP:-90}"
MIN_BATCH="${MIN_BATCH:-1}"
nohup python3 tools/initiative_autoadapt.py --base-sleep "$BASE_SLEEP" --min-batch "$MIN_BATCH" > artifacts/logs/initiative_daemon.out 2>&1 &
echo $! > artifacts/initiative_autoadapt.pid
printf "%s\n" "$!"
