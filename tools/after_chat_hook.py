import os, sys, time
BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, BASE)
from tools.kb import search
from tools.kb_router import route_after_chat
from tools.dynamic_thinking_tick import tick
LOG = os.path.join(BASE, "artifacts", "logs", "after_hook.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def hook(text):
    try:
        q=text or ""
        hits=search(q, k=3, index_path=os.path.join(BASE,"artifacts","kb","index.json"))
        n = route_after_chat(q, hits)
        try:
            tick()
        except Exception:
            pass
        with open(LOG,"a",encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] hook text_len={len(q)} hits={len(hits)} enqueued={n}\n")
    except Exception as e:
        with open(LOG,"a",encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] hook_error {e}\n")
