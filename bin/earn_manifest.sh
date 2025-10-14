#!/bin/zsh
set -e
EXP="${1:?exp path}"
BR="exp/$(date -u +%Y%m%d_%H%M%S)-earn"
CFG="$EXP/config.json"
WAVE=$(jq -r .wave "$CFG")
VAR=$(jq -r .active_variant "$CFG")
PRICE=$(jq -r .price "$CFG")
DATE="$(date -u +%Y-%m-%d)"
cat >> MANIFEST.md <<M
## $DATE — Експеримент $(basename "$EXP")
- Активна хвиля: $VAR (\$$PRICE), wave=$WAVE
- Див. metrics_history.jsonl та release/*
M
cat >> CHANGELOG.md <<C
## $DATE
- Хвиля $WAVE активна: $VAR (\$$PRICE); оновлено метрики та реліз.
C
git switch -c "$BR"
git add MANIFEST.md CHANGELOG.md
git commit -m "exp: wave$WAVE $VAR(\$$PRICE) — docs snapshot"
git push -u origin "$BR"
gh pr create -B main -H "$BR" -t "exp: wave$WAVE $VAR(\$$PRICE) — docs & metrics" -b "Авто: MANIFEST/CHANGELOG для wave=$WAVE $VAR(\$$PRICE)."
gh pr checks --watch
gh pr merge --squash --auto
