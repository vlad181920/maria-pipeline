#!/bin/zsh
set -e
cd "$(dirname "$0")/../.."
export MARIA_HOME="$PWD"

# Тимчасові оверрайди лише для цього запуску (не чіпають .env)
export GUMROAD_HEADLESS=false
export GUMROAD_MAX_SECONDS=45
export GUMROAD_ACTION_TIMEOUT_MS=3000

echo "plan:"
ls -l artifacts/gumroad/plans/upload_plan.json

echo "running uploader (headful)…"
python3 tools/earn_gumroad/gumroad_uploader.py | tee artifacts/logs/earn_diag.out || true

echo "--- REPORT (head) ---"
sed -n '1,120p' artifacts/gumroad/upload_report.json 2>/dev/null || echo "(no report)"
echo "--- DEBUG FILES ---"
ls -lh artifacts/gumroad/debug 2>/dev/null | tail -n 20 || echo "(no debug)"
