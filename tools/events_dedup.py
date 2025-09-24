import sys, os, json, hashlib, time
exp=os.path.abspath(sys.argv[1])
p=os.path.join(exp,"events.jsonl")
if not os.path.isfile(p): 
    print(p); sys.exit(0)
seen=set(); out=[]
with open(p,encoding="utf-8") as f:
    for line in f:
        s=line.strip()
        if not s: continue
        h=hashlib.sha1(s.encode("utf-8")).hexdigest()
        if h in seen: continue
        seen.add(h); out.append(s)
tmp=p+".tmp"+str(int(time.time()))
with open(tmp,"w",encoding="utf-8") as f:
    for s in out: f.write(s+"\n")
os.replace(tmp,p)
print(p)
