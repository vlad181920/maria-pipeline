#!/usr/bin/env bash
set -e
echo "[pipeline]"
tools/pipeline_status.sh || true
echo
echo "[autolaunch]"
if [ -f artifacts/logs/autolaunch.pid ] && ps -p "$(cat artifacts/logs/autolaunch.pid)" >/dev/null 2>&1; then
  echo "running pid=$(cat artifacts/logs/autolaunch.pid)"
else
  echo "stopped"
fi
test -f artifacts/agents/autolaunch.log && tail -n 3 artifacts/agents/autolaunch.log || true
echo
echo "[web_learn]"
tools/web_learn_status.sh || true
echo
echo "[nightly]"
tools/nightly_status.sh || true
echo
echo "[recent]"
test -f artifacts/logs/pipeline.log && tail -n 3 artifacts/logs/pipeline.log || true
test -f artifacts/lessons.jsonl && tail -n 2 artifacts/lessons.jsonl || true
tools/agents_list.py || true
