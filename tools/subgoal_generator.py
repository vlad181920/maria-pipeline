import os, sys, json, uuid
BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, BASE)
from tools.goals_lib import load_all, append_jsonl, list_paths, now

GOALS, SUBGOALS, PROGRESS = list_paths()

TEMPLATES = [
    "Уточнити формулювання і критерії успіху",
    "Зібрати 3 релевантні джерела/факти",
    "Зробити маленький експеримент/чернетку"
]

def main():
    data=load_all()
    goals=[g for g in data["goals"] if g.get("status")=="new"]
    subs=data["subs"]
    have=set((s.get("goal_id"), s.get("title")) for s in subs)
    created=0
    for g in goals:
        for i,tmpl in enumerate(TEMPLATES, start=1):
            title=f"[{g.get('type')}] {tmpl}: {g.get('title')}"
            key=(g["id"], title)
            if key in have: 
                continue
            sub={
                "id": str(uuid.uuid4()),
                "goal_id": g["id"],
                "title": title,
                "order": i,
                "status": "todo",
                "created_at": now()
            }
            append_jsonl(SUBGOALS, sub)
            created+=1
        # перевести goal у in_progress
        g["status"]="in_progress"
    # перезаписати goals з оновленими статусами
    # (простий перезапис: зчитаємо все й оновимо ті, що змінювались)
    allg=load_all()["goals"]
    gid2=g["id"] if goals else None
    idset=set([g["id"] for g in goals])
    for gi in allg:
        if gi["id"] in idset:
            gi["status"]="in_progress"
    # зберегти
    from tools.goals_lib import _save_jsonl
    _save_jsonl(GOALS, allg)
    print(created)

if __name__=="__main__":
    main()
