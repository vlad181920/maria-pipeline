#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONUNBUFFERED=1
mkdir -p artifacts/logs artifacts/stats
start() { p="$1"; shift; if pgrep -f "$p" >/dev/null; then :; else nohup "$@" > "artifacts/logs/$(basename "$p" .py).out" 2>&1 & fi; }
bash tools/log_rotate.sh || true
start tools/initiative_daemon.py python3 tools/initiative_daemon.py
start tools/review_daemon.py python3 tools/review_daemon.py --loop 600
start tools/reprioritization_daemon.py python3 tools/reprioritization_daemon.py --interval 3600
python3 tools/stats_report.py || true
echo "OK"
