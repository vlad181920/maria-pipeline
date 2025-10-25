import os, json, datetime, collections

TODAY = datetime.date.today().isoformat()
REPORT = f"artifacts/reports/daily_summary_{TODAY}.md"
os.makedirs("artifacts/reports", exist_ok=True)

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

pipe = read_jsonl("artifacts/logs/pipeline.log")
today_pipe = [r for r in pipe if r.get("ts","").startswith(TODAY)]
wins = collections.Counter([r.get("winner","") for r in today_pipe])
avg_score = round(sum((r.get("eval",{}).get("score",0) for r in today_pipe))/max(1,len(today_pipe)),3)
backlog = read_jsonl("artifacts/goals/backlog.jsonl")
lessons = read_jsonl("artifacts/lessons.jsonl")
tags = collections.Counter()
for l in lessons:
    for t in l.get("tags") or []:
        tags[t]+=1
state = read_jsonl("artifacts/self/state.jsonl")
last_mood = state[-1].get("mood") if state else "n/a"

lines=[]
lines.append(f"# Зведення за {TODAY}")
lines.append("")
lines.append(f"- Думок/ітерацій сьогодні: {len(today_pipe)}")
lines.append(f"- Середній score думок: {avg_score}")
if wins:
    lines.append("- Топ-наміри:")
    for k,v in wins.most_common(5):
        lines.append(f"  - {k}: {v}")
lines.append(f"- Цілей у backlog: {len(backlog)}")
lines.append(f"- Уроків у lessons.jsonl: {len(lessons)} (по тегам: {dict(tags)})")
lines.append(f"- Настрій: {last_mood}")
with open(REPORT,"w",encoding="utf-8") as f:
    f.write("\n".join(lines)+"\n")
print(REPORT)
