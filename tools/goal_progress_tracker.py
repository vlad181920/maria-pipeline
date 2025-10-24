import os, sys, json, time
BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, BASE)
from tools.goals_lib import load_all, append_jsonl, list_paths, now
from tools.goals_lib import _save_jsonl as save_jsonl

GOALS, SUBGOALS, PROGRESS = list_paths()

def main():
    data=load_all()
    goals=data["goals"]
    subs=data["subs"]
    progress=data["prog"]
    # знайдемо першу підціль у статусі todo для goal in_progress
    changed_sub=0
    for g in goals:
        if g.get("status") not in ("in_progress","new"):
            continue
        # якщо new — це теж активуємо першу підціль
        gsubs=[s for s in subs if s.get("goal_id")==g["id"]]
        gsubs.sort(key=lambda x: int(x.get("order",99)))
        target=None
        for s in gsubs:
            if s.get("status") in ("todo","in_progress"):
                target=s; break
        if target:
            target["status"]="done"
            target["done_at"]=now()
            append_jsonl(PROGRESS, {
                "ts": now(),
                "goal_id": g["id"],
                "subgoal_id": target["id"],
                "event": "subgoal_done",
                "note": target["title"]
            })
            changed_sub+=1
            # якщо всі підцілі done — закриваємо goal
            if all(x.get("status")=="done" for x in gsubs):
                g["status"]="done"
                g["done_at"]=now()
                append_jsonl(PROGRESS, {
                    "ts": now(),
                    "goal_id": g["id"],
                    "event": "goal_done",
                    "note": g["title"]
                })
            break
    if changed_sub:
        save_jsonl(SUBGOALS, subs)
        save_jsonl(GOALS, goals)
    print(changed_sub)

if __name__=="__main__":
    main()
