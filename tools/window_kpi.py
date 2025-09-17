import os, json, datetime
def now(): return datetime.datetime.utcnow()
def within(ts,sec,ref):
    try: t=datetime.datetime.fromisoformat(str(ts).replace('Z',''))
    except: return False
    return (ref-t).total_seconds()<=sec
def it(p):
    if not os.path.exists(p): return []
    return [json.loads(x) for x in open(p,encoding='utf-8') if x.strip()]
def main():
    ref=now()
    q=it('artifacts/thoughts/queue.jsonl')
    log=it('artifacts/logs/initiative_daemon.log')
    tph=sum(1 for o in q if within(o.get('ts'),1800,ref))*2
    inj=[o for o in log if o.get('event')=='injected' and within(o.get('ts'),1800,ref)]
    idle=(sum(1 for o in inj if int(o.get('count',0))==0)/len(inj)) if inj else 0.0
    topics=sorted({o.get('topic') for o in q if within(o.get('ts'),86400,ref) and o.get('topic')})
    print(json.dumps({"thoughts_per_hour_30m":tph,"idle_cycle_ratio_30m":round(idle,3),"distinct_topics_24h":len(topics),"topics_24h":topics},ensure_ascii=False))
if __name__=="__main__": main()
