#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
export MARIA_HOME="$PWD"

pre_less=$(wc -l < artifacts/lessons.jsonl 2>/dev/null || echo 0)
pre_docs=$(python3 - << 'PY'
import json
try:
    print(json.load(open("artifacts/kb/index.json","r",encoding="utf-8")).get("n_docs",0))
except: print(0)
PY
)

echo "Injecting sample error..."
echo "[ERR] ERROR: demo failure $(date)" >> artifacts/logs/error_demo.log
added_from_logs=$(python3 tools/learn_from_errors.py | tail -n 1)

# очистимо processed, щоб воркер взяв нові learn-думи
rm -f artifacts/learn/processed_ids.txt

# перебудуємо KB тихо
python3 tools/kb_build.py >/dev/null

# додамо 5 УНІКАЛЬНИХ learn-думок у audit-чергу
python3 - << 'PY'
import json,uuid,sys,os
os.makedirs("artifacts/thoughts",exist_ok=True)
with open("artifacts/thoughts/audit_queue.jsonl","a",encoding="utf-8") as f:
    for i in range(5):
        f.write(json.dumps({
            "id": str(uuid.uuid4()),
            "topic": f"Вчитися: базовий урок {i+1}",
            "type": "learn",
            "created_at": "NOW",
            "priority": 0.7,
            "state": "new"
        }, ensure_ascii=False) + "\n")
PY

processed=$(python3 tools/learn_worker.py | tail -n 1)

post_less=$(wc -l < artifacts/lessons.jsonl 2>/dev/null || echo 0)
post_docs=$(python3 - << 'PY'
import json
try:
    print(json.load(open("artifacts/kb/index.json","r",encoding="utf-8")).get("n_docs",0))
except: print(0)
PY
)

echo "from_logs=${added_from_logs} learn_processed=${processed} lessons_delta=$((post_less-pre_less)) kb_docs_delta=$((post_docs-pre_docs))"
