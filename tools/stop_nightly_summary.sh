#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
[ -f artifacts/logs/nightly_summary.pid ] && kill "$(cat artifacts/logs/nightly_summary.pid)" 2>/dev/null || true
rm -f artifacts/logs/nightly_summary.pid
echo "[ok] nightly_summary stopped"
