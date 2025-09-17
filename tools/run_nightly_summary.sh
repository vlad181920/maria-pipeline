#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
mkdir -p artifacts/logs
nohup bash tools/nightly_summary.sh > artifacts/logs/nightly_summary.out 2> artifacts/logs/nightly_summary.err &
echo $! > artifacts/logs/nightly_summary.pid
echo "[ok] nightly_summary pid=$(cat artifacts/logs/nightly_summary.pid)"
