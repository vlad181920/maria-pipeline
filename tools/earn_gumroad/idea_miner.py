import os, json, time, uuid, hashlib, re
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
OUT=os.path.join(BASE,"artifacts","gumroad","ideas.jsonl")
KB=os.path.join(BASE,"artifacts","kb","index.json")
THOUGHTS=os.path.join(BASE,"artifacts","thoughts","audit_queue.jsonl")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def slugify(s):
    s=re.sub(r"[^a-zA-Z0-9]+","-", s.strip(), flags=re.U).strip("-").lower()
    return s[:80] or "product"
def dig(x): return hashlib.sha1((x or "").encode("utf-8","ignore")).hexdigest()[:12]

def kb_topics():
    try:
        J=json.load(open(KB,"r",encoding="utf-8"))
        for d in J.get("docs",[])[:50]:
            t=(d.get("title") or d.get("path") or "").strip()
            if t: yield t
    except: pass

def thought_topics():
    try:
        with open(THOUGHTS,"r",encoding="utf-8") as f:
            for line in f:
                try:
                    j=json.loads(line)
                    t=(j.get("topic") or "").strip()
                    if t: yield t
                except: pass
    except: pass

TEMPLATES=[
    "Міні-гайд: {topic} — покрокова інструкція",
    "Шаблони/пресети: {topic} (zip + README)",
    "Чит-лист: {topic} — 20 пунктів контролю",
]

def mine(n=10):
    seen=set(); out=0
    seeds=list(dict.fromkeys(list(thought_topics())+list(kb_topics())))
    if not seeds:
        seeds=["Самостійний заробіток онлайн","Автономні агенти","Продуктивність засобами ШІ"]
    for s in seeds:
        base=s.split(" — ")[0].split(":")[0].strip()
        for tpl in TEMPLATES:
            title=tpl.format(topic=base)[:120]
            if title in seen: continue
            idea={
                "id":str(uuid.uuid4()),
                "title":title,
                "slug":slugify(title),
                "created_at":time.strftime("%Y-%m-%d %H:%M:%S"),
                "source":"idea_miner",
                "digest":dig(title)
            }
            with open(OUT,"a",encoding="utf-8") as f: f.write(json.dumps(idea,ensure_ascii=False)+"\n")
            seen.add(title); out+=1
            if out>=n: return out
    return out

if __name__=="__main__":
    print(mine(15))
