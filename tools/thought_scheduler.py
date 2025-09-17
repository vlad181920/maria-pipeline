#!/usr/bin/env python3
import os, sys, json, argparse, random, datetime
ART_THOUGHTS="artifacts/thoughts/queue.jsonl"
def nowz(): return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
def ensure(): os.makedirs(os.path.dirname(ART_THOUGHTS), exist_ok=True)
def append(path, obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False)+"\n")
def inject(kind, topic, batch, source):
    ensure()
    n=0
    for _ in range(max(1,int(batch))):
        obj={"ts":nowz(),"type":"action","subtype":kind,"title":f"{topic} #{random.randint(1000,9999)}","content":"auto","priority":round(random.uniform(0.5,0.9),2),"topic":topic,"source":source}
        append(ART_THOUGHTS,obj); n+=1
    print(json.dumps({"injected":n},ensure_ascii=False))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--kind",default="initiative")
    p.add_argument("--topic",required=True)
    p.add_argument("--batch",type=int,default=1)
    args=p.parse_args()
    inject(args.kind,args.topic,args.batch,"thought_scheduler")
if __name__=="__main__": main()
