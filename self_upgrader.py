import os, sys, json, time, difflib
from datetime import datetime

LOG_DIR = "artifacts/logs"
REPORT_DIR = "artifacts/reports/self_upgrade_explanations"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_text(p):
    if not os.path.exists(p):
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def write_text(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)

def summary_stats(old_lines, new_lines):
    added = removed = 0
    for line in difflib.unified_diff(old_lines, new_lines, lineterm=""):
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    changed = sum(1 for a,b in zip(old_lines, new_lines) if a!=b)
    return {"added": added, "removed": removed, "changed_lines_est": changed}

def explain_change(path, old_txt, new_txt, stats):
    lines = []
    lines.append(f"# Self-Upgrader Report")
    lines.append("")
    lines.append(f"- Time: {now()}")
    lines.append(f"- File: `{path}`")
    lines.append(f"- Added lines: {stats['added']}")
    lines.append(f"- Removed lines: {stats['removed']}")
    lines.append(f"- Changed (est): {stats['changed_lines_est']}")
    lines.append("")
    lines.append("## Unified Diff")
    lines.append("")
    diff = "\n".join(difflib.unified_diff(old_txt.splitlines(), new_txt.splitlines(), fromfile="before", tofile="after", lineterm=""))
    if not diff.strip():
        diff = "_No textual changes detected_"
    lines.append("```diff")
    lines.append(diff)
    lines.append("```")
    return "\n".join(lines)

def backup(path):
    b = f"{path}.bak_{ts()}"
    if os.path.exists(path):
        with open(path, "rb") as src, open(b, "wb") as dst:
            dst.write(src.read())
    return b

def upgrade_replace_with(target, source):
    old_txt = read_text(target)
    new_txt = read_text(source)
    stats = summary_stats(old_txt.splitlines(), new_txt.splitlines())
    b = backup(target)
    write_text(target, new_txt)
    report = explain_change(target, old_txt, new_txt, stats)
    rpath = os.path.join(REPORT_DIR, f"report_{ts()}.md")
    write_text(rpath, report)
    logline = {"time": now(), "target": target, "source": source, "backup": b, "report": rpath, "stats": stats}
    with open(os.path.join(LOG_DIR, "self_upgrader.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(logline, ensure_ascii=False) + "\n")
    return logline

def upgrade_append_line(target, line):
    old_txt = read_text(target)
    new_txt = (old_txt + ("\n" if old_txt and not old_txt.endswith("\n") else "")) + line + "\n"
    stats = summary_stats(old_txt.splitlines(), new_txt.splitlines())
    b = backup(target)
    write_text(target, new_txt)
    report = explain_change(target, old_txt, new_txt, stats)
    rpath = os.path.join(REPORT_DIR, f"report_{ts()}.md")
    write_text(rpath, report)
    logline = {"time": now(), "target": target, "source": None, "backup": b, "report": rpath, "stats": stats, "action":"append_line"}
    with open(os.path.join(LOG_DIR, "self_upgrader.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(logline, ensure_ascii=False) + "\n")
    return logline

def usage_and_exit():
    print("usage:")
    print("  python3 self_upgrader.py --replace-with <target_file> <source_file>")
    print("  python3 self_upgrader.py --append-line <target_file> <text_line>")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage_and_exit()
    mode = sys.argv[1]
    if mode == "--replace-with" and len(sys.argv) == 4:
        out = upgrade_replace_with(sys.argv[2], sys.argv[3])
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif mode == "--append-line" and len(sys.argv) >= 4:
        target = sys.argv[2]
        line = " ".join(sys.argv[3:])
        out = upgrade_append_line(target, line)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        usage_and_exit()
