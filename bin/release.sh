#!/usr/bin/env bash
set -euo pipefail
MARIA_HOME="${MARIA_HOME:-$HOME/Desktop/Марія}"

ts="$(date +%F_%H%M)"
tmp="/tmp/maria_release_${ts}.tar.gz"

tar -C "$MARIA_HOME" \
  --exclude='venv' \
  --exclude='artifacts/tmp' \
  -czf "$tmp" .

mkdir -p "$MARIA_HOME/artifacts/releases"
dst="$MARIA_HOME/artifacts/releases/maria_release_${ts}.tar.gz"
mv "$tmp" "$dst"

if command -v manifest_log.sh >/dev/null 2>&1; then
  manifest_log.sh "Release snapshot: ${dst#"$MARIA_HOME/"} (excludes venv/tmp)"
fi

echo "$dst"
