#!/usr/bin/env python3
import os, json, datetime

base = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
stats = os.path.join(base,'artifacts','stats')
thoughts_dir = os.path.join(base,'artifacts','thoughts')
os.makedirs(stats, exist_ok=True)
os.makedirs(thoughts_dir, exist_ok=True)

now = datetime.datetime.utcnow()
def ts(offset=0):
    return (now - datetime.timedelta(seconds=offset)).replace(microsecond=0).isoformat()+'Z'

with open(os.path.join(stats,'reflections.jsonl'),'a',encoding='utf-8') as f:
    f.write(json.dumps({"ts":ts(600),"queued":True})+"\n")

with open(os.path.join(stats,'insights_applied.jsonl'),'a',encoding='utf-8') as f:
    for i in range(3):
        f.write(json.dumps({"ts":ts(3600- i*300), "id":f"demo_{i}"})+"\n")

with open(os.path.join(thoughts_dir,'queue.jsonl'),'a',encoding='utf-8') as f:
    for i in range(15):
        f.write(json.dumps({"ts":ts(i*120), "topic":"self_initiated"})+"\n")

print("seeded")
