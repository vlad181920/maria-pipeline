#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
python3 tools/kb_build.py
python3 tools/kb_query.py "заробіток автономно" || true
python3 tools/kb_query.py "планування цілей" || true
python3 tools/kb_query.py "веб автопілот" || true
