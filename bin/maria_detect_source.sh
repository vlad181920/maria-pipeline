#!/usr/bin/env bash
set -euo pipefail
candidates=( "$PWD" "$HOME/Desktop/Марія" "$HOME/Desktop/Марiя" "$HOME/Desktop/Maria" )
for c in "${candidates[@]}"; do
  if [ -d "$c/tools" ] && [ -f "$c/tools/stats_report.py" ]; then
    printf "%s\n" "$c"
    exit 0
  fi
done
found=""
for depth in 2 3 4 5 6; do
  f=$(find "$HOME" -maxdepth "$depth" -type f -name 'stats_report.py' -path '*/tools/stats_report.py' -print -quit 2>/dev/null || true)
  if [ -n "${f:-}" ]; then found="$f"; break; fi
done
if [ -n "${found:-}" ]; then
  dir="$(cd "$(dirname "$found")/.." && pwd)"
  printf "%s\n" "$dir"
  exit 0
fi
echo "ERR: source not found" >&2
exit 1
