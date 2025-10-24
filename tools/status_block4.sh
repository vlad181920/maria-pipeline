#!/bin/zsh
cd "$(dirname "$0")/.."
python3 - << 'PY'
import json, os, glob
BASE=os.environ.get("MARIA_HOME") or os.getcwd()
idx=os.path.join(BASE,"artifacts","kb","index.json")
q=os.path.join(BASE,"artifacts","thoughts","queue.jsonl")
aq=os.path.join(BASE,"artifacts","thoughts","audit_queue.jsonl")
def count_lines(p):
    n=0
    try:
        with open(p,"r",encoding="utf-8") as f:
            for n,_ in enumerate(f,1): pass
    except: pass
    return n
n_docs=0
try:
    with open(idx,"r",encoding="utf-8") as f:
        n_docs=json.load(f).get("n_docs",0)
except: pass
print(f"kb_index: {n_docs} docs")
print(f"queue_lines: {count_lines(q)}")
print(f"audit_lines: {count_lines(aq)}")
logs=sorted(glob.glob(os.path.join(BASE,"artifacts","chat","dialogue_*.jsonl")))
print(f"chat_log: {logs[-1] if logs else 'none'}")
PY
echo "api_health: $(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8765/health || echo 000)"
