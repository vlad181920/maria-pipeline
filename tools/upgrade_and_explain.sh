#!/usr/bin/env bash
set -e
mode="$1"
if [ "$mode" = "replace" ]; then
  tgt="$2"
  src="$3"
  python3 self_upgrader.py --replace-with "$tgt" "$src"
elif [ "$mode" = "append" ]; then
  tgt="$2"
  shift 2
  python3 self_upgrader.py --append-line "$tgt" "$*"
else
  echo "usage: tools/upgrade_and_explain.sh replace <target> <source> | append <target> <line>"
  exit 1
fi
python3 tools/todo_tick.py >/dev/null 2>&1 || true
