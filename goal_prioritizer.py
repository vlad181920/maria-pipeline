import os, json, time
from datetime import datetime

INBOX = "artifacts/goals/new_from_thoughts.jsonl"
BACKLOG = "artifacts/goals/backlog.jsonl"
REPORT = "artifacts/reports/backlog_top.md"

def read_jsonl(p):
    if not os.path.exists(p): return []
    out=[]
    with open(p,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except: pass
    return out

def write_jsonl(p, items):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p,"w",encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False)+"\n")

def normalize_time(t):
    try:
        return datetime.strptime(t,"%Y-%m-%d %H:%M:%S")
    except:
        return datetime.fromtimestamp(0)

def prioritize():
    inbox = read_jsonl(INBOX)
    backlog = read_jsonl(BACKLOG)
    pool = backlog + inbox
    if not pool:
        return {"count":0,"top":[]}

    pool = [dict(x) for x in pool]
    for x in pool:
        x.setdefault("priority", 0.0)
        x.setdefault("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    pool.sort(key=lambda x: normalize_time(x.get("time","")), reverse=True)
    last_time = None
    dedup={}
    for it in pool:
        title = it.get("title","").strip()
        if not title: continue
        dedup[title]=it
        if last_time is None or normalize_time(it["time"])>last_time:
            last_time = normalize_time(it["time"])

    items = list(dedup.values())
    items.sort(key=lambda x: normalize_time(x.get("time","")), reverse=True)
    if items:
        newest = normalize_time(items[0]["time"])
        oldest = normalize_time(items[-1]["time"])
        span = max((newest - oldest).total_seconds(), 1.0)
        for it in items:
            rec = (normalize_time(it["time"]) - oldest).total_seconds()/span
            w = 0.7*float(it.get("priority",0.0)) + 0.3*rec
            it["_weight"]=round(w,4)
    items.sort(key=lambda x: x.get("_weight",0.0), reverse=True)

    write_jsonl(BACKLOG, items)
    if os.path.exists(INBOX):
        open(INBOX,"w").close()

    lines = []
    today = datetime.now().strftime("%Y-%m-%d")
    lines.append(f"# Backlog Top — {today}")
    lines.append("")
    for i,it in enumerate(items[:20],1):
        lines.append(f"{i}. {it.get('title','')} — w={it.get('_weight',0.0)} pr={it.get('priority',0.0)} — {it.get('time','')}")
        if it.get("reason"):
            lines.append(f"   reason: {it['reason']}")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {"count":len(items),"top":[it.get('title') for it in items[:5]]}

if __name__=="__main__":
    print(json.dumps(prioritize(), ensure_ascii=False))
