import os, json, time
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
PATH=os.path.join(BASE,"artifacts","stats","thought_metrics.json")
os.makedirs(os.path.dirname(PATH), exist_ok=True)
def _load():
    try:
        with open(PATH,"r",encoding="utf-8") as f: return json.load(f)
    except: return {"counts":{}, "total":0, "updated_at":""}
def _save(d):
    d["updated_at"]=time.strftime("%Y-%m-%d %H:%M:%S")
    tmp=PATH+".tmp"
    with open(tmp,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)
    os.replace(tmp,PATH)
def incr(ttype):
    d=_load()
    d["counts"][ttype]=int(d["counts"].get(ttype,0))+1
    d["total"]=int(d.get("total",0))+1
    _save(d)
def read():
    return _load()
