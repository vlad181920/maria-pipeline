#!/usr/bin/env bash
set -euo pipefail
MARIA_HOME="${MARIA_HOME:-$HOME/Desktop/Марія}"
MSG="${*:-(без опису)}"
printf -- "- **[%s]** %s\n" "$(date '+%Y-%m-%d %H:%M')" "$MSG" >> "$MARIA_HOME/project_manifest.md"
echo "✅ Записано в MANIFEST."
