#!/usr/bin/env python3
import os, sys, json, time, argparse, datetime, random
ART_REVIEW="artifacts/stats/review.jsonl"
def nowz(): return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
def ensure(): os.makedirs(os.path.dirname(ART_REVIEW), exist_ok=True)
def tick():
    ensure()
    rec={"ts":nowz(),"kind":"spaced_review","count":random.randint(1,3)}
    with open(ART_REVIEW,"a",encoding="utf-8") as f: f.write(json.dumps(rec,ensure_ascii=False)+"\n")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--loop",type=int,default=300)
    a=ap.parse_args()
    while True: tick(); time.sleep(a.loop)
if __name__=="__main__": main()
