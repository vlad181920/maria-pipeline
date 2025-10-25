import os, json, uuid, time, sys
BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, BASE)
from tools.goals_lib import load_all, append_jsonl, list_paths, now, hid

THOUGHTS = os.path.join(BASE,"artifacts","thoughts","audit_queue.jsonl")
GOALS, SUBGOALS, PROGRESS = list_paths()

ALLOW = {"plan":0.9,"research":0.8,"analysis":0.75,"hypothesis":0.7,"action":0.85,"learn":0.7}

def existing_digests(goals):
    return set(g.get("digest") for g in goals if g.get("digest"))

def main():
    data = load_all()
    goals = data["goals"]
    seen = existing_digests(goals)
    created = 0
    try:
        with open(THOUGHTS,"r",encoding="utf-8") as f:
            lines=f.readlines()[-200:]  # останні 200 на випадок великого логу
    except FileNotFoundError:
        lines=[]
    for line in lines:
        try:
            j=json.loads(line)
        except: 
            continue
        ttype=(j.get("type") or "").strip()
        topic=(j.get("topic") or "").strip()
        if not topic or ttype not in ALLOW: 
            continue
        dig = hid(ttype+"|"+topic)
        if dig in seen:
            continue
        goal = {
            "id": str(uuid.uuid4()),
            "title": topic,
            "type": ttype,
            "priority": ALLOW[ttype],
            "status": "new",
            "created_at": now(),
            "digest": dig,
            "source": "thoughts:audit_queue"
        }
        append_jsonl(GOALS, goal)
        seen.add(dig)
        created += 1
        if created >= 5:  # не засмічуємо — максимум 5 за запуск
            break
    print(created)

if __name__=="__main__":
    main()
