#!/usr/bin/env bash
set -euo pipefail
EXP="${1:?Usage: $0 <exp-dir>}"

# БЕРЕМО лише файли з таймстампом, без 'latest'
LATEST="$(ls -1t "$EXP"/distribution_kit_[0-9]*.zip 2>/dev/null | head -n1 || true)"
[[ -z "$LATEST" ]] && { echo "No zips found"; exit 1; }

ABS_LATEST="$(cd "$(dirname "$LATEST")" && pwd)/$(basename "$LATEST")"

# Переставляємо лінку на абсолютну ціль
rm -f "$EXP/distribution_kit_latest.zip"
ln -s "$ABS_LATEST" "$EXP/distribution_kit_latest.zip"

# Релізна тека
TS=$(date +%Y%m%d_%H%M%S)
REL="$EXP/releases/scale_${TS}"
mkdir -p "$REL"

# Копіюємо метадані + САМ ФАЙЛ (через -L)
cp "$EXP"/{result.json,message_selected.md} "$REL"/
cp -L "$EXP/distribution_kit_latest.zip" "$REL"/

echo "Release ready at: $REL"
