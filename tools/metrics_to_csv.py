import json,sys,os,csv
exp=os.path.abspath(sys.argv[1])
inp=os.path.join(exp,"metrics_history.jsonl")
out=os.path.join(exp,"metrics_history.csv")
rows=[]
with open(inp,encoding="utf-8") as f:
    for line in f:
        j=json.loads(line)
        r={"ts_utc":j["ts_utc"],"price":j.get("price")}
        for v in ("A","B"):
            b=j["by_variant"][v]
            r.update({f"{v}_leads":b["leads"],f"{v}_conv":b["conversions"],f"{v}_cr":b["cr_pct"],f"{v}_rev":b["revenue"]})
        t=j["total"]
        r.update({"total_leads":t["leads"],"total_conv":t["conversions"],"total_rev":t["revenue"]})
        rows.append(r)
with open(out,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,rows[0].keys()); w.writeheader(); w.writerows(rows)
print(out)
