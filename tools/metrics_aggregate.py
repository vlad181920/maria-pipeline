#!/usr/bin/env python3
import sys, os, json, datetime, math

def read_json(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def aggregate(exp_path: str):
    exp = os.path.abspath(exp_path)
    cfg_path = os.path.join(exp, "config.json")
    cfg = read_json(cfg_path, {})
    price = float(cfg.get("price") or 0.0)

    res = {"A":{"leads":0,"conversions":0},"B":{"leads":0,"conversions":0}}
    revenue = {"A":0.0,"B":0.0}

    # collect from events.jsonl
    ej = os.path.join(exp,"events.jsonl")
    if os.path.isfile(ej):
        with open(ej, encoding="utf-8") as f:
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
                if t=="lead":
                    res[v]["leads"]+=1
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

    # --- z-test for two proportions A vs B ---
    a_leads, a_conv = res["A"]["leads"], res["A"]["conversions"]
    b_leads, b_conv = res["B"]["leads"], res["B"]["conversions"]

    def ztest(a_s,a_n,b_s,b_n):
        if a_n==0 or b_n==0: return None, None
        p1=a_s/a_n; p2=b_s/b_n; p_pool=(a_s+b_s)/(a_n+b_n)
        se=math.sqrt(p_pool*(1-p_pool)*(1/a_n+1/b_n))
        if se==0: return None,None
        z=(p1-p2)/se
        # approx two-tailed p-value via error function
        try:
            from math import erf, sqrt
            p = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
        except Exception:
            p = None
        return z, p

    def cr_rate(leads,conv): return (conv/leads) if leads>0 else 0.0

    z, p = ztest(a_conv, a_leads, b_conv, b_leads)
    a_cr = cr_rate(a_leads, a_conv)
    b_cr = cr_rate(b_leads, b_conv)
    better = "A" if a_cr>b_cr else ("B" if b_cr>a_cr else None)
    sig = {"z": z, "p_value": p, "min_sample_ok": bool(a_leads>=10 and b_leads>=10)}
    should_switch = bool(sig["min_sample_ok"] and p is not None and p<0.05 and better is not None)

    ts=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    summary={"ts_utc":ts,"price":price,"by_variant":out,"total":total,
             "significance":sig,"better_variant":better,"should_switch":should_switch}

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
