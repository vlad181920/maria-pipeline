#!/bin/zsh
set -e
EXP="${1:?exp path}"
VAR="${2:?A_or_B}"
PRICE="${3:?price}"
# 1) Перемкнути хвилю, зібрати метрики, зробити реліз
python3 tools/exp_next_wave.py --exp "$EXP" --variant "$VAR" --price "$PRICE" >/dev/null
python3 tools/metrics_aggregate.py "$EXP" >/dev/null
LAST_REL="$(scripts/exp_release.sh "$EXP" | tail -n1)"
scripts/exp_status.sh "$EXP"
# 2) Зафіксувати MANIFEST/CHANGELOG + PR з авто-мерджем
BR="exp/$(date -u +%Y%m%d_%H%M%S)-earn"
CFG="$EXP/config.json"
W=$(jq -r .wave "$CFG"); V=$(jq -r .active_variant "$CFG"); P=$(jq -r .price "$CFG")
D="$(date -u +%Y-%m-%d)"
cat >> MANIFEST.md <<M
## $D — Експеримент $(basename "$EXP")
- Активна хвиля: $V (\$$P), wave=$W
- Див. metrics_history.jsonl та release/*
M
cat >> CHANGELOG.md <<C
## $D
- Хвиля $W активна: $V (\$$P); оновлено метрики та реліз.
C
git switch -c "$BR"
git add MANIFEST.md CHANGELOG.md
git commit -m "exp: wave$W $V(\$$P) — docs snapshot"
git push -u origin "$BR"
gh pr create -B main -H "$BR" -t "exp: wave$W $V(\$${P}) — docs & metrics" -b "Авто: MANIFEST/CHANGELOG для wave=$W $V(\$${P})." >/dev/null
gh pr checks --watch
gh pr merge --squash --auto
# 3) GitHub Release по останньому файлу
TAG="exp-$(date -u +%Y%m%d_%H%M%S)"
gh release create "$TAG" "$LAST_REL" -t "$TAG" -n "Auto-release for $(basename "$LAST_REL")" >/dev/null
echo "Release tag: $TAG"
