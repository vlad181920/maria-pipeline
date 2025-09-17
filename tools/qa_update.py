import os, json, datetime
from collections import Counter
now=datetime.datetime.now()
today=now.date()
since=today-datetime.timedelta(days=7)
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
pipe=read_jsonl("artifacts/logs/pipeline.log")
def ts_date(s):
    try: return datetime.datetime.strptime(s[:10],"%Y-%m-%d").date()
    except: return None
recent=[r for r in pipe if ts_date(r.get("ts","")) and ts_date(r.get("ts",""))>=since]
quality_events=sum(1 for r in recent if (r.get("eval") or {}).get("recommended"))
lessons=read_jsonl("artifacts/lessons.jsonl")
total_l=len(lessons)
kb_l=sum(1 for l in lessons if l.get("tags") and len(l.get("tags"))>0)
has_kb=round((kb_l/(total_l or 1)),2)
backlog=read_jsonl("artifacts/goals/backlog.jsonl")
next_step=bool(len(backlog)>0)
line=f"[{now.strftime('%Y-%m-%d %H:%M')}] QA: quality_events={quality_events}, has_kb={has_kb}, next_step={'true' if next_step else 'false'}\n"
with open("project_manifest.md","a",encoding="utf-8") as f:
    f.write(line)
print(json.dumps({"quality_events":quality_events,"has_kb":has_kb,"next_step":next_step,"wrote":"project_manifest.md"}, ensure_ascii=False))
