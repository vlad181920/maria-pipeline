#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONUNBUFFERED=1
mkdir -p artifacts/logs artifacts/stats
bash tools/log_rotate.sh || true
python3 tools/stats_report.py || true
python3 tools/kpi_assert_DoD.py || true
date -u +%FT%TZ
