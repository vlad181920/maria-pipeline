#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
pre=$(python3 - << 'PY'
n=0
try:
    with open("artifacts/thoughts/audit_queue.jsonl","r",encoding="utf-8") as f:
        for n,_ in enumerate(f,1): pass
except: pass
print(n)
PY
)
python3 tools/kb_build.py
for i in $(jot 5 1); do ~/maria/bin/maria "Як знайти нові можливості заробітку? $i"; done
pgrep -f "uvicorn.*tools.chat_api:app" >/dev/null 2>&1 || MARIA_HOME="$PWD" nohup python3 -m uvicorn tools.chat_api:app --host 127.0.0.1 --port 8765 > artifacts/logs/chat_api.out 2>&1 &
sleep 2
for i in $(jot 5 1); do curl -s -X POST http://127.0.0.1:8765/api/chat -H 'Content-Type: application/json' -d '{"text":"Кроки пошуку можливостей заробітку"}' >/dev/null; done
post=$(python3 - << 'PY'
n=0
try:
    with open("artifacts/thoughts/audit_queue.jsonl","r",encoding="utf-8") as f:
        for n,_ in enumerate(f,1): pass
except: pass
print(n)
PY
)
echo "new_thoughts_audit=$((post-pre))"
