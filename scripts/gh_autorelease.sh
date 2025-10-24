#!/bin/zsh
set -euo pipefail

EXP="${1:?exp path}"

# Перевірки
command -v gh >/dev/null 2>&1 || { echo "ERR: gh not found" >&2; exit 1; }
gh repo view >/dev/null 2>&1 || { echo "ERR: gh not authenticated or not a git repo" >&2; exit 1; }

REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
DIR="$EXP/release"
[ -d "$DIR" ] || { echo "ERR: no release dir: $DIR" >&2; exit 1; }

LAST="$(ls -t "$DIR"/*.md 2>/dev/null | head -n1 || true)"
[ -n "$LAST" ] || { echo "ERR: no release files in $DIR" >&2; exit 1; }

# Унікальний тег за UTC-часом
TS="$(date -u +%Y%m%d_%H%M%S)"
TAG="exp-${TS}"
TITLE="$TAG"
NOTES="Auto-release for $(basename "$LAST")"

# Створити реліз
gh release create "$TAG" "$LAST" -t "$TITLE" -n "$NOTES" >/dev/null

echo "created: https://github.com/$REPO/releases/tag/$TAG"
