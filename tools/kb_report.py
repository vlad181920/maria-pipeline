import os, json, re

home = os.environ.get("MARIA_HOME", os.path.expanduser("~/Desktop/Марія"))
ins_dir = os.path.join(home, "artifacts", "insights")
data = {
    "total_md": 0,
    "stub_files": 0,
    "full_files": 0,
    "coverage_full_ratio": 0.0,
    "stub_list": [],
    "full_list": []
}

if os.path.isdir(ins_dir):
    for fn in sorted(os.listdir(ins_dir)):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(ins_dir, fn)
        try:
            s = open(p, "r", encoding="utf-8").read()
        except:
            continue
        data["total_md"] += 1
        is_stub_name = fn.startswith("stub_")
        mentions_stub = re.search(r"\*\*\[Правило\]\*\*\s*Чернетка", s, flags=re.I)
        looks_full = all(k in s for k in ["**[Правило]**", "**[Крок]**", "**[Приклад]**"]) and not mentions_stub
        if is_stub_name or mentions_stub:
            data["stub_files"] += 1
            data["stub_list"].append(fn)
        elif looks_full:
            data["full_files"] += 1
            data["full_list"].append(fn)
        else:
            data["stub_files"] += 1
            data["stub_list"].append(fn)

if data["total_md"] > 0:
    data["coverage_full_ratio"] = round(data["full_files"] / data["total_md"], 2)

print(json.dumps(data, ensure_ascii=False, indent=2))
