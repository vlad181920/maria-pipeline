#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p artifacts/logs
PORT=$(python3 - <<'PY'
import socket, sys
for p in range(8765, 8800):
    with socket.socket() as s:
        try:
            s.bind(("127.0.0.1", p))
            print(p); sys.exit(0)
        except OSError:
            pass
print(0)
PY
)
[ "$PORT" != "0" ]
echo "$PORT" > artifacts/logs/web_learn.port
export PYTHONUNBUFFERED=1
export PYTHONPATH="."
nohup python3 tools/web_learn_server.py "$PORT" > artifacts/logs/web_learn_server.out 2> artifacts/logs/web_learn_server.err &
PID=$!
echo $PID > artifacts/logs/web_learn.pid
sleep 0.7
if ! ps -p "$PID" >/dev/null 2>&1; then
  echo "[err] server died"
  tail -n +1 artifacts/logs/web_learn_server.err || true
  exit 1
fi
python3 - "$PORT" <<'PY'
import urllib.request, sys, time
port=int(sys.argv[1])
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
ok=False
for _ in range(20):
    try:
        opener.open(f"http://127.0.0.1:{port}/status", timeout=1).read()
        ok=True; break
    except Exception:
        time.sleep(0.2)
print(f"[health] ok={ok} port={port}")
PY
echo "[ok] web_learn pid=$PID port=$PORT"
