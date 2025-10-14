#!/bin/zsh
set -e

EXP="${1:?exp path}"
target_price="${2:?target_price}"

# прочитати поточний стан
CFG="$EXP/config.json"
cur_var=$(jq -r '.active_variant' "$CFG" 2>/dev/null)
cur_price=$(jq -r '.price' "$CFG" 2>/dev/null)

# визначити кращий варіант з metrics_summary.json (якщо є)
MET="$EXP/metrics_summary.json"
if [ -f "$MET" ]; then
  a_cr=$(jq -r '.by_variant.A.cr_pct // 0' "$MET")
  b_cr=$(jq -r '.by_variant.B.cr_pct // 0' "$MET")
  if (( $(echo "$a_cr > $b_cr" | bc -l) )); then
    target_variant="A"
  elif (( $(echo "$b_cr > $a_cr" | bc -l) )); then
    target_variant="B"
  else
    target_variant="$cur_var"
  fi
else
  target_variant="$cur_var"
fi

# cooldown на перемикання (30 хв з моменту оновлення конфігу)
cooldown_sec=1800
updated_at=$(jq -r '.updated_at_utc // empty' "$CFG")
if [ -n "$updated_at" ]; then
  last=$(date -j -u -f "%Y-%m-%dT%H:%M:%SZ" "$updated_at" +"%s" 2>/dev/null || echo 0)
  now=$(date -u +"%s")
  if [ $((now - last)) -lt $cooldown_sec ]; then
    echo "auto_switch: cooldown active ($(($cooldown_sec - (now - last)))s left), skip"
    exit 0
  fi
fi

# ідемпотентність: якщо вже в цільовому стані — нічого не робимо
if [ "$cur_var" = "$target_variant" ] && [ "$(printf '%.2f' "$cur_price")" = "$(printf '%.2f' "$target_price")" ]; then
  echo "auto_switch: already at $cur_var (\$$cur_price), skip queue"
  exit 0
fi

# поставити команду у шину (v1 schema)
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
mkdir -p bus
cat >> bus/commands.jsonl <<CMD
{"ts_utc":"$ts","action":"switch_variant","args":{"exp_path":"$EXP","variant":"$target_variant","price":$target_price},"schema_ver":"v1"}
CMD

echo "queued auto switch (action) -> $target_variant ($target_price)"
