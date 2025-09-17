#!/usr/bin/env bash
set -e
f="$1"
title="$2"
ext="${f##*.}"
case "$ext" in
  html|htm)
    python3 - <<PY
from insight_saver import import_html
print(import_html("$f", "$title"))
PY
    ;;
  srt|vtt)
    python3 - <<PY
from insight_saver import import_subtitles
print(import_subtitles("$f", "$title"))
PY
    ;;
  *)
    echo "unsupported file type: $ext"; exit 2;;
esac
python3 tools/todo_tick.py >/dev/null 2>&1 || true
