#!/usr/bin/env bash
set -euo pipefail
EXP="${1:?Usage: $0 <exp-dir>}"
for name in message_A_19.txt message_B_29.txt message.txt; do
  f="$EXP/deliverables/$name"
  printf "\n== %s ==\n" "$name"
  if [[ -s "$f" ]]; then
    wc -l -c "$f"
    sed -n '1,12p' "$f"
  else
    echo "MISSING or empty: $f"
  fi
done
