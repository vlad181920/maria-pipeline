#!/usr/bin/env bash
set -e
mkdir -p artifacts/logs
python3 tools/pipeline_autolaunch.py --watch --interval 1 >/dev/null 2>&1 &
echo $! > artifacts/logs/autolaunch.pid
echo "[ok] autolaunch pid=$(cat artifacts/logs/autolaunch.pid)"
