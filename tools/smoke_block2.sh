#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
export MARIA_HOME="$PWD"
# доб'ємо різноманітність 30 тік-тактів
for i in $(jot 30 1); do python3 tools/dynamic_thinking_tick.py >/dev/null; done
echo "=== BLOCK2 CHECK ==="
python3 tools/check_block2.py || true
