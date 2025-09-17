#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
while true; do
  py='from datetime import datetime, timedelta; import time, zoneinfo
tz=zoneinfo.ZoneInfo("Europe/Prague")
now=datetime.now(tz)
tom=(now+timedelta(days=1)).replace(hour=0,minute=1,second=0,microsecond=0)
print(int((tom-now).total_seconds()))'
  S=$(python3 - <<PY
import zoneinfo
$py
PY
)
  sleep "$S"
  python3 make_summary.py || true
  SUM="artifacts/reports/daily_summary_$(date +%F).md"
  SNIP=$(tail -n +2 "$SUM" | head -n 6 | tr '\n' '; ')
  echo "[\$(date +%F' '%T)] nightly summary: $SNIP" >> project_manifest.md
done
