#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
pre=0
[ -f artifacts/thoughts/queue.jsonl ] && pre=$(wc -l < artifacts/thoughts/queue.jsonl)
python3 tools/kb_build.py
~/maria/bin/maria "Як будеш шукати способи автономного заробітку?"
~/maria/bin/maria "Опиши перші кроки дослідження ринків."
~/maria/bin/maria "Які метрики ефективності будемо відстежувати?"
pgrep -f "uvicorn.*tools.chat_api:app" >/dev/null 2>&1 || nohup python3 -m uvicorn tools.chat_api:app --host 127.0.0.1 --port 8765 > artifacts/logs/chat_api.out 2>&1 &
sleep 2
for i in $(jot 5 1); do curl -s -X POST http://127.0.0.1:8765/api/chat -H 'Content-Type: application/json' -d '{"text":"Кроки пошуку можливостей заробітку"}' >/dev/null; done
post=$(wc -l < artifacts/thoughts/queue.jsonl)
echo "new_thoughts=$((post-pre))"
echo "kb_index=artifacts/kb/index.json"
last_chat=$(ls -1 artifacts/chat/dialogue_*.jsonl 2>/dev/null | tail -1)
[ -n "$last_chat" ] && echo "chat_log=$last_chat" || true
