import os, re, json, math, glob, time, hashlib
from collections import Counter, defaultdict
def _read_text(p):
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return ""
def _read_jsonl_text(p):
    out=[]
    try:
        with open(p,"r",encoding="utf-8",errors="ignore") as f:
            for line in f:
                line=line.strip()
                if not line: continue
                try:
                    j=json.loads(line)
                    if isinstance(j,dict):
                        for k in ["text","content","message","body"]:
                            v=j.get(k)
                            if isinstance(v,str): out.append(v)
                        if "role" in j and "content" in j and isinstance(j["content"],str):
                            out.append(j["content"])
                except:
                    pass
    except:
        pass
    return "\n".join(out)
def _is_jsonl(p):
    return p.lower().endswith(".jsonl")
def _is_text_like(p):
    p=p.lower()
    return p.endswith(".md") or p.endswith(".txt") or p.endswith(".log")
def _normalize(s):
    s=s.lower()
    s=re.sub(r"[^\w\s]+"," ",s,flags=re.UNICODE)
    s=re.sub(r"\s+"," ",s).strip()
    return s
def _tokenize(s, stop):
    s=_normalize(s)
    toks=s.split(" ")
    return [t for t in toks if t and t not in stop and not t.isdigit()]
def _title_from_text(s):
    s=s.strip().splitlines()
    if not s: return ""
    t=s[0].strip()
    return t[:120]
def _hash_path(p):
    return hashlib.sha1(p.encode("utf-8")).hexdigest()[:12]
def build_index(base_dir, globs, out_path="artifacts/kb/index.json"):
    stop=set(["the","and","or","a","an","to","of","in","on","for","with","as","at","by","is","are","be","was","were","it","this","that","these","those","from","into","about","over","under","between","within","without","you","your","yours","me","my","mine","we","our","ours","he","she","they","them","their","i","u","та","і","або","що","це","ця","цей","ці","ті","той","таки","будь","для","про","від","над","під","між","у","в","не","як","є","до"])
    paths=[]
    for g in globs:
        p=os.path.join(base_dir,g)
        paths+=glob.glob(p, recursive=True)
    seen=set()
    docs=[]
    for p in sorted(paths):
        if not os.path.isfile(p): continue
        if p in seen: continue
        seen.add(p)
        if _is_jsonl(p):
            txt=_read_jsonl_text(p)
        elif _is_text_like(p) or os.path.basename(p)=="project_manifest.md":
            txt=_read_text(p)
        else:
            continue
        if not txt: continue
        txt=txt if len(txt)<=200000 else txt[:200000]
        title=_title_from_text(txt)
        tokens=_tokenize(txt, stop)
        if not tokens: continue
        docs.append({"path":os.path.relpath(p, base_dir),"title":title,"tokens":tokens,"preview":txt[:1200]})
    N=len(docs)
    if N==0:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path,"w",encoding="utf-8") as f: json.dump({"version":1,"built_at":time.strftime("%Y-%m-%d %H:%M:%S"),"n_docs":0,"idf":{},"docs":[]},f,ensure_ascii=False)
        return out_path
    df=Counter()
    for d in docs:
        df.update(set(d["tokens"]))
    idf={}
    for term,c in df.items():
        idf[term]=math.log((N+1)/(c+1))+1.0
    for d in docs:
        tf=Counter(d["tokens"])
        vec={}
        for term,c in tf.items():
            vec[term]=(1.0+math.log(c))*idf.get(term,0.0)
        norm=math.sqrt(sum(v*v for v in vec.values())) or 1.0
        d["vec"]=vec
        d["norm"]=norm
        del d["tokens"]
    out={"version":1,"built_at":time.strftime("%Y-%m-%d %H:%M:%S"),"n_docs":N,"idf":idf,"docs":docs}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp=out_path+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False)
    os.replace(tmp,out_path)
    return out_path
def load_index(path="artifacts/kb/index.json"):
    try:
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"version":1,"built_at":"","n_docs":0,"idf":{},"docs":[]}
def _qvec(query, idf):
    stop=set(["the","and","or","a","an","to","of","in","on","for","with","as","at","by","is","are","be","was","were","it","this","that","these","those","from","into","about","over","under","between","within","without","you","your","yours","me","my","mine","we","our","ours","he","she","they","them","their","i","u","та","і","або","що","це","ця","цей","ці","ті","той","таки","будь","для","про","від","над","під","між","у","в","не","як","є","до"])
    toks=_tokenize(query, stop)
    tf=Counter(toks)
    vec={}
    for term,c in tf.items():
        idfv=idf.get(term,0.0)
        if idfv>0.0:
            vec[term]=(1.0+math.log(c))*idfv
    norm=math.sqrt(sum(v*v for v in vec.values())) or 1.0
    return vec,norm
def search(query, k=5, index_path="artifacts/kb/index.json"):
    idx=load_index(index_path)
    if idx.get("n_docs",0)==0:
        return []
    qv,qn=_qvec(query, idx["idf"])
    scores=[]
    for d in idx["docs"]:
        s=0.0
        dv=d["vec"]
        for t,w in qv.items():
            vw=dv.get(t)
            if vw: s+=w*vw
        s/= (qn*d["norm"])
        if s>0.0:
            scores.append((s,d))
    scores.sort(key=lambda x: x[0], reverse=True)
    out=[]
    for s,d in scores[:k]:
        out.append({"score":round(float(s),6),"path":d["path"],"title":d.get("title",""),"preview":d.get("preview","")})
    return out
