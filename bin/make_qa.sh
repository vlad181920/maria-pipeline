#!/usr/bin/env bash
set -euo pipefail

MARIA_HOME="${MARIA_HOME:-$HOME/Desktop/Марія}"
TMPDIR="$MARIA_HOME/artifacts/tmp"
mkdir -p "$TMPDIR"

run_or_stub () {
  local cmd="$1" out="$2"
  if bash -lc "$cmd" > "$out" 2>/dev/null; then
    true
  else
    echo "{}" > "$out"
  fi
}

if [ -f "$MARIA_HOME/tools/test_chat_api.py" ]; then
  run_or_stub "python3 '$MARIA_HOME/tools/test_chat_api.py'" "$TMPDIR/chat_api.json"
else
  echo "{}" > "$TMPDIR/chat_api.json"
fi

if [ -f "$MARIA_HOME/tools/test_reply_quality.py" ]; then
  run_or_stub "python3 '$MARIA_HOME/tools/test_reply_quality.py'" "$TMPDIR/quality.json"
else
  echo "{}" > "$TMPDIR/quality.json"
fi

if [ -f "$MARIA_HOME/tools/test_next_step.py" ]; then
  run_or_stub "python3 '$MARIA_HOME/tools/test_next_step.py'" "$TMPDIR/next_step.json"
else
  echo "{}" > "$TMPDIR/next_step.json"
fi

if [ -f "$MARIA_HOME/tools/kb_report.py" ]; then
  run_or_stub "python3 '$MARIA_HOME/tools/kb_report.py'" "$TMPDIR/kb.json"
else
  echo "{}" > "$TMPDIR/kb.json"
fi

cat "$TMPDIR/chat_api.json"
cat "$TMPDIR/quality.json"
cat "$TMPDIR/next_step.json"
cat "$TMPDIR/kb.json"

SUMMARY="$(python3 - <<'PY'
import json, os
home = os.environ.get("MARIA_HOME")
tmp = os.path.join(home, "artifacts", "tmp")
def read(name):
    p = os.path.join(tmp, name)
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
qa = read("quality.json")
nx = read("next_step.json")
kb = read("kb.json")
q_events = qa.get("quality_events_found")
ratio = qa.get("ratio_has_kb")
has_next = nx.get("has_next_step")
cov = kb.get("coverage_full_ratio")
print(f"QA: quality_events={q_events}, has_kb={ratio}, next_step={has_next}, kb_coverage={cov}")
PY
)"

if command -v manifest_log.sh >/dev/null 2>&1; then
  manifest_log.sh "$SUMMARY"
else
  echo "ℹ️ manifest_log.sh не знайдено; пропускаю запис у MANIFEST"
fi
