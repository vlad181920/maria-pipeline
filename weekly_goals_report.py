import os, json
from datetime import datetime

SRC = "artifacts/goals/new_from_thoughts.jsonl"
OUT_DIR = "artifacts/reports"
os.makedirs(OUT_DIR, exist_ok=True)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def main():
    goals = read_jsonl(SRC)
    goals = sorted(goals, key=lambda x: (x.get("priority", 0), x.get("time","")), reverse=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(OUT_DIR, f"weekly_goals_{today}.md")
    lines = []
    lines.append(f"# Weekly Goals Report — {today}")
    lines.append("")
    lines.append(f"Generated: {now()}")
    lines.append("")
    if not goals:
        lines.append("- No goals found.")
    else:
        for i, g in enumerate(goals, 1):
            title = g.get("title","")
            reason = g.get("reason","")
            pr = g.get("priority", 0)
            t = g.get("time","")
            lines.append(f"{i}. {title} — priority={pr} — {t}")
            if reason:
                lines.append(f"   reason: {reason}")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(out_path)

if __name__ == "__main__":
    main()
