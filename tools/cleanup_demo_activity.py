#!/usr/bin/env python3
import os, json, datetime, shutil, tempfile

base = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
stats = os.path.join(base,'artifacts','stats')
thoughts_dir = os.path.join(base,'artifacts','thoughts')
paths = {
    "reflections": os.path.join(stats,'reflections.jsonl'),
    "insights_applied": os.path.join(stats,'insights_applied.jsonl'),
    "thoughts_queue": os.path.join(thoughts_dir,'queue.jsonl'),
}
now = datetime.datetime.utcnow()
cutoff = now - datetime.timedelta(hours=2)

def parse_ts(s):
    try: 
        return datetime.datetime.fromisoformat(str(s).replace('Z',''))
    except:
        return None

def clean_file(path, keep_fn):
    if not os.path.exists(path): return 0,0
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    os.close(fd)
    kept = removed = 0
    with open(path,'r',encoding='utf-8') as fin, open(tmp,'w',encoding='utf-8') as fout:
        for ln in fin:
            t = ln.strip()
            if not t:
                continue
            try:
                obj = json.loads(t)
            except:
                continue
            if keep_fn(obj):
                fout.write(json.dumps(obj, ensure_ascii=False)+"\n")
                kept += 1
            else:
                removed += 1
    shutil.move(tmp, path)
    return kept, removed

def keep_reflection(o):
    t = parse_ts(o.get("ts"))
    if t and t >= cutoff and o.get("queued") and not o.get("goal"):
        return False
    return True

def keep_insight_applied(o):
    i = str(o.get("id",""))
    if i.startswith("demo_"):
        return False
    return True

def keep_thought(o):
    t = parse_ts(o.get("ts"))
    if t and t >= cutoff and not o.get("source"):
        return False
    return True

def main():
    os.makedirs(stats, exist_ok=True)
    os.makedirs(thoughts_dir, exist_ok=True)
    results = {}
    k,r = clean_file(paths["reflections"], keep_reflection); results["reflections_kept"]=k; results["reflections_removed"]=r
    k,r = clean_file(paths["insights_applied"], keep_insight_applied); results["ins_applied_kept"]=k; results["ins_applied_removed"]=r
    k,r = clean_file(paths["thoughts_queue"], keep_thought); results["thoughts_kept"]=k; results["thoughts_removed"]=r
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
