#!/usr/bin/env bash
set -e
while IFS= read -r line; do
  [ -z "$line" ] && continue
  url="${line%%|*}"
  title="${line#*|}"
  url="$(echo "$url" | xargs)"
  title="$(echo "$title" | xargs)"
  tools/web_fetch_and_learn.sh "$url" "$title"
done < data/web_seeds.txt
