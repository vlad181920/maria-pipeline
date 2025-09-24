import os, sys, json, time, uuid, re, hashlib
from tools.metrics_thoughts import incr as metrics_incr
BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
QDIR = os.path.join(BASE, "artifacts", "thoughts")
QFILE = os.path.join(QDIR, "queue.jsonl")
AUDIT = os.path.join(QDIR, "audit_queue.jsonl")
LOG = os.path.join(BASE, "artifacts", "logs", "router.log")
os.makedirs(QDIR, exist_ok=True); os.makedirs(os.path.dirname(LOG), exist_ok=True)
def log(m):
    try:
        with open(LOG,"a",encoding="utf-8") as f: f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {m}\n")
    except: pass
def _h(x): return hashlib.sha1((x or "").encode("utf-8","ignore")).hexdigest()[:16]
def _clean(s): s=re.sub(r"\s+"," ",(s or "")).strip(); return s[:240]
def _dedupe_set():
    seen=set()
    try:
        with open(QFILE,"r",encoding="utf-8") as f:
            for line in f:
                try:
                    j=json.loads(line); t=j.get("topic","")
                    if t: seen.add(_h(t))
                except: pass
    except: pass
    return seen
def _append(path,obj):
    with open(path,"a",encoding="utf-8") as f: f.write(json.dumps(obj,ensure_ascii=False)+"\n")
def _enq(obj):
    try: _append(QFILE,obj)
    except Exception as e: log(f"ENQ_ERROR {e}"); return False
    try: _append(AUDIT,obj)
    except Exception as e: log(f"AUDIT_ERROR {e}")
    try: metrics_incr(obj.get("type",""))
    except Exception as e: log(f"METRICS_ERROR {e}")
    return True
def route_after_chat(text, kb_hits):
    try:
        seen=_dedupe_set(); now=time.strftime("%Y-%m-%d %H:%M:%S")
        base=_clean(text); topics=[]
        if base: topics.append(("plan", f"Сформувати план дослідження: {base}", 0.86))
        for h in (kb_hits or [])[:2]:
            title=_clean((h.get("title") or h.get("preview","")[:80]))
            if title: topics.append(("research", f"Дослідити: {title}", 0.8))
        out=0
        for i,(tt,topic,pr) in enumerate(topics[:2]):
            if _h(topic) in seen: continue
            obj={"id":str(uuid.uuid4()),"topic":topic,"type":tt,"created_at":now,"priority":pr,"state":"new","result_ref":None}
            if _enq(obj): out+=1; log(f"ADDED {tt}: {topic}")
        log(f"ROUTE text_len={len(base)} hits={len(kb_hits or [])} added={out}")
        return out
    except Exception as e:
        log(f"ROUTE_ERROR {e}"); return 0
