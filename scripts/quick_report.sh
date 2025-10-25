#!/bin/zsh
set -e

EXP_DEFAULT="artifacts/earn/experiments/20250919_211414__micro-service-offer-audit-implementation"
EXP="${1:-$EXP_DEFAULT}"

CFG="$EXP/config.json"
MS="$EXP/metrics_summary.json"
[ -f "$MS" ] || { echo "metrics_summary.json missing, run metrics_aggregate first"; exit 1; }

# Pull fields via jq (with fallbacks)
wave=$(jq -r '.wave // "?"' "$CFG" 2>/dev/null || echo "?")
active=$(jq -r '.active_variant // "?"' "$CFG" 2>/dev/null || echo "?")
price=$(jq -r '.price // "?"' "$CFG" 2>/dev/null || echo "?")

ts=$(jq -r '.ts_utc' "$MS")
p=$(jq -r '.significance.p_value // empty' "$MS")
z=$(jq -r '.significance.z // empty' "$MS")
minok=$(jq -r '.significance.min_sample_ok // false' "$MS")
better=$(jq -r '.better_variant // empty' "$MS")
should=$(jq -r '.should_switch // false' "$MS")

A_L=$(jq -r '.by_variant.A.leads' "$MS")
A_C=$(jq -r '.by_variant.A.conversions' "$MS")
A_CR=$(jq -r '.by_variant.A.cr_pct' "$MS")
A_R=$(jq -r '.by_variant.A.revenue' "$MS")

B_L=$(jq -r '.by_variant.B.leads' "$MS")
B_C=$(jq -r '.by_variant.B.conversions' "$MS")
B_CR=$(jq -r '.by_variant.B.cr_pct' "$MS")
B_R=$(jq -r '.by_variant.B.revenue' "$MS")

T_L=$(jq -r '.total.leads' "$MS")
T_C=$(jq -r '.total.conversions' "$MS")
T_R=$(jq -r '.total.revenue' "$MS")

# Latest release file if exists
REL_DIR="$EXP/release"
LATEST_REL=""
if [ -d "$REL_DIR" ]; then
  LATEST_REL=$(ls -t "$REL_DIR" 2>/dev/null | head -n1)
fi

UTC_NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
OUT_DIR="artifacts/earn/reports"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/report_$(date -u +%Y%m%d_%H%M%S).md"

gen_report() {
cat <<MRK
# Experiment Report — $(basename "$EXP")
- Generated (UTC): $UTC_NOW
- Metrics snapshot (UTC): $ts
- Wave: **$wave**
- Active variant: **$active** (price **\$$price**)

## Metrics
| Variant | Leads | Conversions | CR % | Revenue |
|---|---:|---:|---:|---:|
| A | $A_L | $A_C | $A_CR | \$$A_R |
| B | $B_L | $B_C | $B_CR | \$$B_R |
| **Total** | **$T_L** | **$T_C** |  | **\$$T_R** |

## Significance
- z-score: ${z:-n/a}
- p-value: ${p:-n/a}
- Min sample ok: ${minok}
- Better variant: ${better:-n/a}
- Should switch now: ${should}

## Recommendation
$( if [ "$should" = "true" ] && [ -n "$better" ]; then
     echo "- **Switch to $better** at price **\$$price** (meets decision rule)."
   else
     echo "- **Hold current** ($active). Keep collecting data."
   fi )

## Latest release
$( if [ -n "$LATEST_REL" ]; then
     echo "- $REL_DIR/$LATEST_REL"
   else
     echo "- (no releases yet)"
   fi )

MRK
}

# Print to console and save to file
gen_report | tee "$OUT" >/dev/null
echo "Saved: $OUT"
