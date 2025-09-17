#!/usr/bin/env bash
set -euo pipefail
python3 -m py_compile "$MARIA_HOME/maria_brain.py"
bash "$MARIA_HOME/bin/kb_report.sh" >/dev/null
bash "$MARIA_HOME/bin/make_qa.sh"   >/dev/null
echo "OK: compile + KB + QA"
