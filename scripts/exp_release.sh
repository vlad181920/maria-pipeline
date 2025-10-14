#!/bin/zsh
set -e

EXP="${1:?exp path}"

# throttle: не частіше ніж раз на 10 хв
last="$(ls -t "$EXP/release" 2>/dev/null | head -n1)"
if [ -n "$last" ]; then
  last_path="$EXP/release/$last"
  if [ -f "$last_path" ]; then
    if [ $(($(date +%s) - $(stat -f %m "$last_path"))) -lt 600 ]; then
      echo "$last_path"
      exit 0
    fi
  fi
fi

python3 tools/metrics_aggregate.py "$EXP" > /tmp/exp_metrics.json

CFG="$EXP/config.json"
WAVE=$(jq -r '.wave//0' "$CFG" 2>/dev/null || echo 0)
VAR=$(jq -r '.active_variant//"?"' "$CFG" 2>/dev/null || echo "?")
PRICE=$(jq -r '.price//0' "$CFG" 2>/dev/null || echo 0)
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

A_LEADS=$(jq -r '.by_variant.A.leads//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
A_CONV=$(jq -r '.by_variant.A.conversions//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
A_CR=$(jq -r '.by_variant.A.cr_pct//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
A_REV=$(jq -r '.by_variant.A.revenue//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
B_LEADS=$(jq -r '.by_variant.B.leads//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
B_CONV=$(jq -r '.by_variant.B.conversions//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
B_CR=$(jq -r '.by_variant.B.cr_pct//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
B_REV=$(jq -r '.by_variant.B.revenue//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
T_LEADS=$(jq -r '.total.leads//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
T_CONV=$(jq -r '.total.conversions//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)
T_REV=$(jq -r '.total.revenue//0' /tmp/exp_metrics.json 2>/dev/null || echo 0)

mkdir -p "$EXP/release"
OUT="$EXP/release/release_$(date -u +%Y%m%d_%H%M%S).md"
{
  echo "# Release"
  echo
  echo "- Time (UTC): $TS"
  echo "- Experiment: $(basename "$EXP")"
  echo "- Wave: $WAVE"
  echo "- Active variant: $VAR"
  echo "- Price: \$$PRICE"
  echo
  echo "## Metrics"
  echo
  echo "| Variant | Leads | Conversions | CR % | Revenue |"
  echo "|---|---:|---:|---:|---:|"
  echo "| A | $A_LEADS | $A_CONV | $A_CR | \$$A_REV |"
  echo "| B | $B_LEADS | $B_CONV | $B_CR | \$$B_REV |"
  echo "| Total | $T_LEADS | $T_CONV |  | \$$T_REV |"
} > "$OUT"

# заштовхнути подію release_published (v1 schema)
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
mkdir -p bus
printf '{"ts_utc":"%s","type":"release_published","exp_path":"%s","schema_ver":"v1"}\n' "$ts" "$EXP" >> bus/events.jsonl

echo "$OUT"
