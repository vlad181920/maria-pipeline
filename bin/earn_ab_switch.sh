#!/bin/zsh
set -e
EXP="${1:?exp path}"
VAR="${2:?A_or_B}"
PRICE="${3:?price}"
python3 tools/exp_next_wave.py --exp "$EXP" --variant "$VAR" --price "$PRICE" >/dev/null
python3 tools/metrics_aggregate.py "$EXP" >/dev/null
scripts/exp_release.sh "$EXP" >/dev/null
scripts/exp_status.sh "$EXP"
