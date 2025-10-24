import os, json, collections, sys, time
BASE=os.environ.get("MARIA_HOME") or os.getcwd()
aq=os.path.join(BASE,"artifacts","thoughts","audit_queue.jsonl")
counts=collections.Counter(); total=0
try:
    with open(aq,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                j=json.loads(line)
                t=j.get("type","").strip() or "unknown"
                counts[t]+=1; total+=1
            except: pass
except FileNotFoundError:
    pass
types_ge3=[t for t,c in counts.items() if c>=3]
pass_cond = len(types_ge3)>=4
summary={"total":total,"counts":dict(counts),"types_ge3":types_ge3,"pass":pass_cond}
print(json.dumps(summary,ensure_ascii=False,indent=2))
sys.exit(0 if pass_cond else 1)
