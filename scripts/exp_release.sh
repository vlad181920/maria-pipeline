#!/bin/zsh
set -e
EXP="$1"
[ -z "$EXP" ] && echo "usage: exp_release.sh EXP_PATH" && exit 1
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
echo "$OUT"
