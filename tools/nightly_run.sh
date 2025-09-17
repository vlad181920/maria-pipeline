#!/usr/bin/env bash
set -e
tools/web_learn_seeded.sh
python3 make_summary.py
python3 tools/qa_update.py
python3 goal_prioritizer.py >/dev/null 2>&1 || true
python3 tools/todo_tick.py >/dev/null 2>&1 || true
