#!/usr/bin/env python3
import os, json, glob, collections
items=[]
for cfg in glob.glob("artifacts/agents/*/config.json"):
    try:
        with open(cfg,"r",encoding="utf-8") as f:
            j=json.load(f)
        items.append({
            "created": j.get("created",""),
            "title": j.get("title",""),
            "status": j.get("status",""),
            "dir": os.path.dirname(cfg)
        })
    except: pass

items.sort(key=lambda x: x["created"], reverse=True)
by_title=collections.defaultdict(list)
for it in items: by_title[it["title"]].append(it)

i=1
for title, arr in sorted(by_title.items(), key=lambda kv: kv[1][0]["created"], reverse=True):
    active=arr[0]
    print(f"{i}. {active['created']} | {active['status'] or 'created'} | {title} | {active['dir']} (total: {len(arr)})")
    i+=1
