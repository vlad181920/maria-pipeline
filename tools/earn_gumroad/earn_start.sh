#!/bin/zsh
set -e
cd "$(dirname "$0")/../.."
export MARIA_HOME="$PWD"
mkdir -p artifacts/logs
# зупинимо старі екземпляри, якщо були
pkill -f "tools/earn_gumroad/earn_daemon.py" >/dev/null 2>&1 || true
# стартуємо
nohup python3 tools/earn_gumroad/earn_daemon.py > artifacts/logs/earn_daemon.out 2>&1 &
echo $! > artifacts/logs/earn_daemon.pid
sleep 2
echo "PID=$(cat artifacts/logs/earn_daemon.pid)"
echo "--- out ---"
tail -n 20 artifacts/logs/earn_daemon.out || true
echo "--- log ---"
tail -n 20 artifacts/logs/earn_daemon.log || true
