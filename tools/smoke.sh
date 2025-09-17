#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
./tools/api_status.py >/dev/null
./tools/api_learn.py "https://example.com" "Smoke Example" >/dev/null
python3 thought_pipeline.py >/dev/null
./tools/agents_list.py
