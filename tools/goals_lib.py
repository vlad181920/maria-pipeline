import os, json, time, uuid, hashlib
BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
GDIR = os.path.join(BASE,"artifacts","goals")
GOALS = os.path.join(GDIR,"goals.jsonl")
SUBGOALS = os.path.join(GDIR,"subgoals.jsonl")
PROGRESS = os.path.join(GDIR,"progress.jsonl")
os.makedirs(GDIR, exist_ok=True)

def now(): return time.strftime("%Y-%m-%d %H:%M:%S")
def hid(s): return hashlib.sha1((s or "").encode("utf-8","ignore")).hexdigest()[:16]

def _load_jsonl(path):
    items=[]
    try:
        with open(path,"r",encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line: continue
                try: items.append(json.loads(line))
                except: pass
    except FileNotFoundError:
        pass
    return items

def _save_jsonl(path, items):
    tmp=path+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it,ensure_ascii=False)+"\n")
    os.replace(tmp, path)

def load_all():
    return {
        "goals": _load_jsonl(GOALS),
        "subs": _load_jsonl(SUBGOALS),
        "prog": _load_jsonl(PROGRESS),
    }

def append_jsonl(path, obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=False)+"\n")

def list_paths(): return GOALS, SUBGOALS, PROGRESS
