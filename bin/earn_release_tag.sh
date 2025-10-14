#!/bin/zsh
set -e
EXP="${1:?exp path}"
LAST="$(ls -t "$EXP/release" | head -n1)"
TAG="exp-$(date -u +%Y%m%d_%H%M%S)"
gh release create "$TAG" "$EXP/release/$LAST" -t "$TAG" -n "Auto-release for $LAST"
echo "$TAG"
