import os, json, sys, glob, re
from datetime import datetime

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read_jsonl(p):
    if not os.path.exists(p): return []
    out=[]
    with open(p,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except: pass
    return out

def run_agent(agent_dir: str):
    cfg_path = os.path.join(agent_dir, "config.json")
    if not os.path.exists(cfg_path):
        raise SystemExit(f"no config.json in {agent_dir}")
    with open(cfg_path,"r",encoding="utf-8") as f: cfg=json.load(f)
    title = cfg.get("title","")
    lessons = read_jsonl("artifacts/lessons.jsonl")
    # простий відбір релевантних уроків: останні 10 + ключові слова з назви
    keys = [w.lower() for w in re.findall(r"\w+", title)]
    rel=[]
    for l in reversed(lessons[-200:]):
        txt = (l.get("title","") + " " + l.get("text","")).lower()
        if any(k in txt for k in keys) or len(rel)<10:
            rel.append(l)
        if len(rel)>=20: break
    os.makedirs(os.path.join(agent_dir,"output"), exist_ok=True)
    draft = os.path.join(agent_dir,"output","README.md")
    with open(draft,"w",encoding="utf-8") as f:
        f.write(f"# Драфт артефакту: {title}\n\n")
        f.write("## Коротке резюме інпутів\n")
        for i,l in enumerate(rel[:8],1):
            t=l.get("title",""); src=l.get("source",""); snippet=(l.get("text","")[:280]).replace("\n"," ")
            f.write(f"- [{i}] {t} — {src} — {snippet}...\n")
        f.write("\n## Кроки виконання\n1) Уточнення вимог\n2) Чернетка\n3) Самоперевірка\n4) Вивід артефакту\n")
        f.write("\n## Самоперевірка (порожньо)\n- [ ] Якість\n- [ ] Повнота\n- [ ] Узгодженість\n")
    # оновити статус і залогувати
    cfg["status"]="drafted"; 
    with open(cfg_path,"w",encoding="utf-8") as f: json.dump(cfg,f,ensure_ascii=False,indent=2)
    with open(os.path.join(agent_dir,"log.jsonl"),"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts":now(),"event":"drafted","draft":os.path.relpath(draft)},ensure_ascii=False)+"\n")
    return {"ok":True,"draft":draft,"agent":agent_dir}

if __name__ == "__main__":
    if len(sys.argv)<2:
        # взяти останнього зі списку
        idx = "artifacts/agents/index.jsonl"
        last=None
        for line in open(idx,"r",encoding="utf-8"):
            last=line
        if not last: raise SystemExit("no agents")
        d=json.loads(last)["dir"]
        print(json.dumps(run_agent(d), ensure_ascii=False))
    else:
        print(json.dumps(run_agent(sys.argv[1]), ensure_ascii=False))
