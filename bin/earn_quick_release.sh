#!/bin/zsh
set -e
EXP="${1:?exp path}"
python3 tools/metrics_aggregate.py "$EXP" >/dev/null
scripts/exp_release.sh "$EXP"
scripts/exp_status.sh "$EXP"
