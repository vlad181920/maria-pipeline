#!/bin/zsh
EXP="$1"
CFG="$EXP/config.json"
MET="$EXP/metrics_summary.json"
wave=$(jq -r .wave "$CFG" 2>/dev/null)
var=$(jq -r .active_variant "$CFG" 2>/dev/null)
price=$(jq -r .price "$CFG" 2>/dev/null)
A=$(jq -r '.by_variant.A| "A: L=" + (.leads|tostring) + " C=" + (.conversions|tostring) + " CR=" + (.cr_pct|tostring) + "% R=$" + (.revenue|tostring)' "$MET" 2>/dev/null)
B=$(jq -r '.by_variant.B| "B: L=" + (.leads|tostring) + " C=" + (.conversions|tostring) + " CR=" + (.cr_pct|tostring) + "% R=$" + (.revenue|tostring)' "$MET" 2>/dev/null)
echo "wave=$wave variant=$var price=\$$price | $A | $B"
