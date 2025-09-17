import os, sys, json, time, argparse, random, datetime
ART_THOUGHTS="artifacts/thoughts/queue.jsonl"
ART_LOG="artifacts/logs/initiative_daemon.log"
MOOD_PATH="artifacts/mood.json"
TOPICS=["self_initiated","curiosity_probe","hypothesis","maintenance","earning_probe","learning_application","reflection_next_action"]
def nowz(): return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
def ensure():
    os.makedirs(os.path.dirname(ART_THOUGHTS), exist_ok=True)
    os.makedirs(os.path.dirname(ART_LOG), exist_ok=True)
def append(path,obj):
    with open(path,"a",encoding="utf-8") as f: f.write(json.dumps(obj,ensure_ascii=False)+"\n")
def read_mood():
    if not os.path.exists(MOOD_PATH): return {"valence":0.15,"arousal":0.6,"focus":0.7,"updated":nowz()}
    try:
        with open(MOOD_PATH,"r",encoding="utf-8") as f:
            m=json.load(f)
            for k in ("valence","arousal","focus"):
                v=float(m.get(k,0.0)); m[k]=0.0 if v<0 else (1.0 if v>1 else v)
            return m
    except:
        return {"valence":0.15,"arousal":0.6,"focus":0.7,"updated":nowz()}
def factors(m):
    v,a,f=m["valence"],m["arousal"],m["focus"]
    min_per_hour_mult=0.8+0.6*a+0.2*v
    period_secs_mult=max(0.5,1.2-0.4*a)
    batch=1+int((v+f+a)>2.1)
    return {"min_per_hour_mult":round(min_per_hour_mult,3),"period_secs_mult":round(period_secs_mult,3),"batch":batch}
def inject(batch):
    n=0
    for _ in range(batch):
        topic=random.choice(TOPICS)
        obj={"ts":nowz(),"type":"action","subtype":"initiative","title":f"{topic} #{random.randint(1000,9999)}","content":"auto","priority":round(random.uniform(0.5,0.9),2),"topic":topic,"source":"initiative_autoadapt"}
        append(ART_THOUGHTS,obj); n+=1
    return n
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-sleep",type=int,default=120)
    ap.add_argument("--min-batch",type=int,default=1)
    a=ap.parse_args()
    ensure()
    while True:
        m=read_mood()
        fac=factors(m)
        sleep_secs=max(30,int(a.base_sleep*fac["period_secs_mult"]))
        batch=max(a.min_batch, fac["batch"])
        cnt=inject(batch)
        append(ART_LOG,{"ts":nowz(),"event":"injected","count":cnt,"batch":batch,"params":{"sleep":sleep_secs,"base_sleep":a.base_sleep,"mood":m,"factors":fac}})
        time.sleep(sleep_secs)
if __name__=="__main__": main()
