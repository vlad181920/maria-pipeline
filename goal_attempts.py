import os, json, time
from datetime import datetime, timedelta

ATTEMPTS = "artifacts/goals/attempts.jsonl"
BACKLOG  = "artifacts/goals/backlog.jsonl"
PARKING  = "artifacts/goals/parking.jsonl"

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _read_jsonl(p):
    if not os.path.exists(p): return []
    out=[]
    with open(p,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except: pass
    return out

def _write_jsonl(p, items):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p,"w",encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False)+"\n")

def log_attempt(title: str, success: bool, note: str=""):
    rec = {"ts": _now(), "title": title, "success": bool(success), "note": note}
    os.makedirs(os.path.dirname(ATTEMPTS), exist_ok=True)
    with open(ATTEMPTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False)+"\n")
    return rec

def prune_backlog():
    back = _read_jsonl(BACKLOG)
    atts = _read_jsonl(ATTEMPTS)
    week_ago = datetime.now() - timedelta(days=7)

    moved=[]
    for it in back:
        title = it.get("title","")
        fails = 0
        for a in atts:
            if a.get("title")==title and not a.get("success"):
                try:
                    ts = datetime.strptime(a.get("ts",""), "%Y-%m-%d %H:%M:%S")
                except:
                    continue
                if ts >= week_ago:
                    fails += 1
        if fails >= 5:
            moved.append(it)
            it["_drop"]=True
        elif fails >= 3:
            it["_weight"]=0.1
            tags = it.get("tags") or []
            if "stale" not in tags: tags.append("stale")
            it["tags"]=tags

    kept=[x for x in back if not x.get("_drop")]
    _write_jsonl(BACKLOG, kept)
    if moved:
        park = _read_jsonl(PARKING)+moved
        _write_jsonl(PARKING, park)
    return {"kept":len(kept), "parked":len(moved)}

if __name__=="__main__":
    import sys
    if len(sys.argv)>=3 and sys.argv[1]=="log":
        print(json.dumps(log_attempt(sys.argv[2], sys.argv[3].lower()=="true", " ".join(sys.argv[4:])), ensure_ascii=False))
    else:
        print(json.dumps(prune_backlog(), ensure_ascii=False))
