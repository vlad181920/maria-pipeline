import os, json, glob
from datetime import datetime, timedelta

STATE_LOG = "artifacts/self/state.jsonl"
DIALOGUES_DIR = "artifacts/dialogues"
THOUGHT_METRICS = "artifacts/metrics/thoughts.jsonl"

os.makedirs("artifacts/self", exist_ok=True)

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def _last_hrs(items, key, hours):
    limit = datetime.now() - timedelta(hours=hours)
    out = []
    for it in items:
        ts = it.get(key) or it.get("ts") or it.get("time")
        try:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        except:
            continue
        if dt >= limit:
            out.append(it)
    return out

def snapshot():
    dialogues = glob.glob(os.path.join(DIALOGUES_DIR, "*.md"))
    thoughts = _read_jsonl(THOUGHT_METRICS)
    thoughts_24h = _last_hrs(thoughts, "ts", 24)
    mood = "balanced"
    success_ratio = 0.7
    rec = {
        "ts": _now(),
        "mood": mood,
        "dialogues_total": len(dialogues),
        "thoughts_24h": len(thoughts_24h),
        "success_ratio": success_ratio
    }
    with open(STATE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

if __name__ == "__main__":
    out = snapshot()
    print(json.dumps(out, ensure_ascii=False, indent=2))
