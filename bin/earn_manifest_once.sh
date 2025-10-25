#!/bin/zsh
set -e
EXP="${1:?exp path}"
CFG="$EXP/config.json"
W=$(jq -r .wave "$CFG"); V=$(jq -r .active_variant "$CFG"); P=$(jq -r .price "$CFG")
D="$(date -u +%Y-%m-%d)"
hdr="## $D — Експеримент $(basename "$EXP")"
grep -qF "$hdr" MANIFEST.md || cat >> MANIFEST.md <<M
$hdr
- Активна хвиля: $V (\$$P), wave=$W
- Див. metrics_history.jsonl та release/*
M
chg="## $D"
grep -qF "$chg" CHANGELOG.md || cat >> CHANGELOG.md <<C
$chg
- Хвиля $W активна: $V (\$$P); оновлено метрики та реліз.
C
