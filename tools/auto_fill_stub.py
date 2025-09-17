import os, re, sys

home = os.environ.get("MARIA_HOME", os.path.expanduser("~/Desktop/Марія"))
ins_dir = os.path.join(home, "artifacts", "insights")
os.makedirs(ins_dir, exist_ok=True)

def ensure_block(path):
    try:
        s = open(path, "r", encoding="utf-8").read()
    except:
        return False
    has_rule = "**[Правило]**" in s
    has_step = "**[Крок]**" in s
    has_ex   = "**[Приклад]**" in s
    if has_rule and has_step and has_ex:
        return False
    base = os.path.basename(path)
    topic = re.sub(r"^stub[_-]", "", os.path.splitext(base)[0]).replace("-", " ")
    block = (
        f"**[Правило]** Чернетка для теми: {topic}\n"
        f"**[Крок]** Додай 2–3 речення пояснення і 1 приклад.\n"
        f"**[Приклад]** Після правки онови project_manifest.md через manifest_log.sh.\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        if s.strip() and not s.endswith("\n"):
            f.write("\n")
        f.write(block)
    return True

changed = 0
for fn in sorted(os.listdir(ins_dir)):
    if fn.endswith(".md") and fn.startswith("stub_"):
        if ensure_block(os.path.join(ins_dir, fn)):
            changed += 1

print(f'{{"filled_stubs": {changed}}}')
