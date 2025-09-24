import json,sys,os,re,glob,datetime
def read_json(p):
    with open(p,encoding="utf-8") as f: return json.load(f)
def safe_load_json(p,default):
    try: return read_json(p)
    except: return default
def which_variant_from_note(s):
    t=s.lower()
    if "(a" in t or " variant a" in t or " a)" in t or " a " in t: return "A"
    if "(b" in t or " variant b" in t or " b)" in t or " b " in t: return "B"
    if "$29" in t or " 29" in t: return "B"
    if "$19" in t or " 19" in t: return "A"
    return None
def aggregate(exp):
    price= safe_load_json(os.path.join(exp,"config.json"),{}).get("price",0.0)
    res={"A":{"leads":0,"conversions":0},"B":{"leads":0,"conversions":0}}
    revenue={"A":0.0,"B":0.0}
    rj=os.path.join(exp,"result.json")
    if os.path.isfile(rj):
        data=safe_load_json(rj,{})
        notes=[str(x) for x in data.get("metrics",{}).get("notes",[])]
        for n in notes:
            v=which_variant_from_note(n)
            if v:
                if "lead" in n.lower(): res[v]["leads"]+=1
                if "conversion" in n.lower() or "sale" in n.lower(): 
                    res[v]["conversions"]+=1
                    revenue[v]+=price
    ej=os.path.join(exp,"events.jsonl")
    if os.path.isfile(ej):
        with open(ej,encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line: continue
                try:
                    e=json.loads(line)
                except:
                    continue
                v=str(e.get("variant","")).upper()
                if v not in ("A","B"): continue
                t=str(e.get("type","")).lower()
                if t=="lead": res[v]["leads"]+=1
                if t in ("conversion","sale","purchase"):
                    res[v]["conversions"]+=1
                    amt=float(e.get("amount",price) or 0.0)
                    revenue[v]+=amt
    out={}
    for v in ("A","B"):
        leads=res[v]["leads"]
        conv=res[v]["conversions"]
        cr= (conv/leads*100.0) if leads>0 else 0.0
        out[v]={"leads":leads,"conversions":conv,"cr_pct":round(cr,2),"revenue":round(revenue[v],2)}
    total={"leads":res["A"]["leads"]+res["B"]["leads"],
           "conversions":res["A"]["conversions"]+res["B"]["conversions"],
           "revenue":round(revenue["A"]+revenue["B"],2)}
    ts=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    summary={"ts_utc":ts,"price":price,"by_variant":out,"total":total}
    metrics_path=os.path.join(exp,"metrics_summary.json")
    with open(metrics_path,"w",encoding="utf-8") as f: json.dump(summary,f,ensure_ascii=False,indent=2)
    hist=os.path.join(exp,"metrics_history.jsonl")
    with open(hist,"a",encoding="utf-8") as f: f.write(json.dumps(summary,ensure_ascii=False)+"\n")
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":
    exp=os.environ.get("EXP") or (sys.argv[1] if len(sys.argv)>1 else "")
    if not exp: 
        print(json.dumps({"ok":False,"error":"no EXP"},ensure_ascii=False)); sys.exit(1)
    aggregate(exp)
