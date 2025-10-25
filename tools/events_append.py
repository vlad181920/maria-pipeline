import sys,os,json,datetime
exp=os.path.abspath(sys.argv[1])
variant=sys.argv[2].upper()
etype=sys.argv[3].lower()
amount=float(sys.argv[4]) if len(sys.argv)>4 else None
os.makedirs(exp,exist_ok=True)
p=os.path.join(exp,"events.jsonl")
rec={"ts_utc":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
     "variant":variant,"type":etype}
if amount is not None: rec["amount"]=amount
with open(p,"a",encoding="utf-8") as f: f.write(json.dumps(rec,ensure_ascii=False)+"\n")
print(p)
