#!/usr/bin/env bash
set -euo pipefail
FILE="$1"; RULE="$2"; STEP="$3"; EX="$4"
BLOCK="**[Правило]** $RULE
**[Крок]** $STEP
**[Приклад]** $EX"
grep -Fq "$BLOCK" "$FILE" 2>/dev/null && { echo "↩️ Вже є у $FILE"; exit 0; }
printf "%s\n" "$BLOCK" >> "$FILE"
echo "✅ Записано в $FILE"
