import os, json, time, uuid, hashlib
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
PATH=os.path.join(BASE,"artifacts","lessons.jsonl")
os.makedirs(os.path.dirname(PATH), exist_ok=True)
def _hash(txt): return hashlib.sha1((txt or "").encode("utf-8","ignore")).hexdigest()[:16]
def add_lesson(title, content, tags=None, source="system", related=None, severity="info"):
    tags=tags or []; related=related or []
    obj={"id":str(uuid.uuid4()),"ts":time.strftime("%Y-%m-%d %H:%M:%S"),
         "title":title.strip()[:240],"content":content.strip(),
         "tags":list(tags),"source":source,"related":related,
         "severity":severity,"digest":_hash(title+content)}
    with open(PATH,"a",encoding="utf-8") as f: f.write(json.dumps(obj,ensure_ascii=False)+"\n")
    return obj
