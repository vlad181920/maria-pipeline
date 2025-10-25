import os, json, time, uuid, random, hashlib
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
POL=os.path.join(BASE,"policies","thought_policy.json")
QDIR=os.path.join(BASE,"artifacts","thoughts")
QFILE=os.path.join(QDIR,"queue.jsonl")
AUDIT=os.path.join(QDIR,"audit_queue.jsonl")
LOG=os.path.join(BASE,"artifacts","logs","dynamic_thinking.log")
METR=os.path.join(BASE,"artifacts","stats","thought_metrics.json")
os.makedirs(QDIR, exist_ok=True); os.makedirs(os.path.dirname(LOG), exist_ok=True)
def _load_json(p,default):
    try:
        with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except: return default
def _append(path,obj):
    with open(path,"a",encoding="utf-8") as f: f.write(json.dumps(obj,ensure_ascii=False)+"\n")
def _h(x): return hashlib.sha1((x or "").encode("utf-8","ignore")).hexdigest()[:16]
def _seen():
    s=set()
    try:
        with open(QFILE,"r",encoding="utf-8") as f:
            for line in f:
                try: j=json.loads(line); t=j.get("topic",""); 
                except: t=""
                if t: s.add(_h(t))
    except: pass
    return s
def _count_lines(p):
    n=0
    try:
        with open(p,"r",encoding="utf-8") as f:
            for n,_ in enumerate(f,1): pass
    except: pass
    return n
def _choose_type(pol, metr):
    types=pol.get("types",[])
    w=dict(pol.get("weights",{}))
    total=max(1,int(metr.get("total",0)))
    counts=metr.get("counts",{})
    for t in types:
        share=(counts.get(t,0))/total if total else 0.0
        target=1.0/len(types) if types else 0.0
        adj = 1.0 + max(0.0, (target - share))
        w[t]=w.get(t,1.0)*adj
    pool=[]
    for t,wt in w.items():
        k=max(1,int(round(wt*10)))
        pool.extend([t]*k)
    if not pool: pool=types or ["analysis"]
    return random.choice(pool)
def _topic(tt):
    now=time.strftime("%Y-%m-%d %H:%M:%S")
    if tt=="analysis": return f"Аналіз прогалин знань та ринкових сигналів @ {now}"
    if tt=="plan": return f"Побудувати короткий план дій для дослідження заробітку @ {now}"
    if tt=="learn": return f"Вчитися: знайти матеріали для підсилення слабких зон @ {now}"
    if tt=="hypothesis": return f"Гіпотеза: новий підхід до автономного заробітку @ {now}"
    if tt=="action": return f"Дія: підготувати маленький експеримент @ {now}"
    return f"Думка: {tt} @ {now}"
def tick():
    pol=_load_json(POL,{})
    metr=_load_json(METR,{"counts":{},"total":0})
    backlog=_count_lines(QFILE)
    if backlog>=pol.get("backlog_soft_cap",50): 
        with open(LOG,"a",encoding="utf-8") as f: f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] SKIP backlog={backlog}\n")
        return 0
    tt=_choose_type(pol,metr)
    top=_topic(tt)
    obj={"id":str(uuid.uuid4()),"topic":top,"type":tt,"created_at":time.strftime("%Y-%m-%d %H:%M:%S"),"priority":0.75,"state":"new","result_ref":None}
    try:
        if _h(top) in _seen(): return 0
        _append(QFILE,obj); _append(AUDIT,obj)
        m=_load_json(METR,{"counts":{},"total":0})
        m["counts"][tt]=int(m["counts"].get(tt,0))+1
        m["total"]=int(m.get("total",0))+1
        tmp=METR+".tmp"
        with open(tmp,"w",encoding="utf-8") as f: json.dump(m,f,ensure_ascii=False,indent=2)
        os.replace(tmp,METR)
        with open(LOG,"a",encoding="utf-8") as f: f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ADD {tt}: {top}\n")
        return 1
    except Exception as e:
        with open(LOG,"a",encoding="utf-8") as f: f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ERR {e}\n")
        return 0
if __name__=="__main__":
    tick()
