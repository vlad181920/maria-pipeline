import os, json, sys
from datetime import datetime

QUEUE = "artifacts/goals/new_from_thoughts.jsonl"

def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def enqueue_goal(title: str, reason: str, priority: float):
    _ensure_dir(os.path.dirname(QUEUE))
    rec = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "reason": reason,
        "priority": round(float(priority), 3),
        "source": "thought_evaluator"
    }
    with open(QUEUE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: python3 link_thoughts_to_goals.py <title> <reason> <priority>")
        sys.exit(1)
    rec = enqueue_goal(sys.argv[1], sys.argv[2], float(sys.argv[3]))
    print(json.dumps(rec, ensure_ascii=False, indent=2))
