#!/usr/bin/env python3
import os, json, datetime, sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ART = os.path.join(BASE, "artifacts")
STATS_DIR = os.path.join(ART, "stats")
THOUGHTS_Q = os.path.join(ART, "thoughts", "queue.jsonl")
REFLECTIONS = os.path.join(STATS_DIR, "reflections.jsonl")
INSIGHTS_APPLIED = os.path.join(STATS_DIR, "insights_applied.jsonl")
DAILY = os.path.join(STATS_DIR, f"daily_report_{datetime.datetime.utcnow().date().isoformat()}.md")

def now_utc():
    return datetime.datetime.utcnow()

def parse_ts(ts):
    try:
        return datetime.datetime.fromisoformat(str(ts).replace("Z",""))
    except:
        return None

def within(ts, seconds, ref=None):
    if not ref: ref = now_utc()
    t = parse_ts(ts)
    if not t: return False
    return (ref - t).total_seconds() <= seconds

def iter_jsonl(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln: continue
            try:
                yield json.loads(ln)
            except:
                pass

def ensure_dirs():
    os.makedirs(STATS_DIR, exist_ok=True)

def compute_windows():
    ref = now_utc()
    win = {"10m":600, "1h":3600, "24h":86400}
    lessons = actions = 0
    for o in iter_jsonl(REFLECTIONS):
        if within(o.get("ts"), win["24h"], ref):
            lessons += 1
            actions += 1 if o.get("queued") else 0
    thoughts = {"10m":0,"1h":0,"24h":0}
    for o in iter_jsonl(THOUGHTS_Q):
        ts = o.get("ts")
        for k,sec in win.items():
            if within(ts, sec, ref): thoughts[k]+=1
    insights_applied = sum(1 for _ in iter_jsonl(INSIGHTS_APPLIED))
    return {
        "lessons": lessons,
        "actions_from_lessons": actions,
        "lesson_to_action_ratio": (actions/lessons) if lessons else 0.0,
        "insights_applied": insights_applied,
        "thoughts_10m": thoughts["10m"],
        "thoughts_1h": thoughts["1h"],
        "thoughts_24h": thoughts["24h"],
    }

def write_md(data):
    lines=[]
    lines.append(f"# Daily KPI — {datetime.datetime.utcnow().date().isoformat()} (generated {now_utc().replace(microsecond=0).isoformat()}Z)")
    lines.append("## Summary")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| lessons_24h | {data['lessons']} |")
    lines.append(f"| actions_from_lessons_24h | {data['actions_from_lessons']} |")
    lines.append(f"| lesson_to_action_ratio | {round(data['lesson_to_action_ratio'],3)} |")
    lines.append(f"| insights_applied_24h | {data['insights_applied']} |")
    lines.append(f"| thoughts_10m | {data['thoughts_10m']} |")
    lines.append(f"| thoughts_1h | {data['thoughts_1h']} |")
    lines.append(f"| thoughts_24h | {data['thoughts_24h']} |")
    with open(DAILY, "w", encoding="utf-8") as f:
        f.write("\n".join(lines)+"\n")
    print(DAILY)

def main():
    ensure_dirs()
    data = compute_windows()
    write_md(data)

if __name__ == "__main__":
    sys.exit(main())
