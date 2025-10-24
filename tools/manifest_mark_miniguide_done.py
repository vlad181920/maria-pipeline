import io, re, os, sys, datetime

P = "project_manifest.md"
if not os.path.exists(P):
    print("project_manifest.md not found"); sys.exit(1)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
stamp = f"- [{now}] EARN: decision=scale; згенеровано onepager + mini_guide_v1; канал=Owned longform (тип, без платформ); policy=OK.\n"

s = io.open(P, "r", encoding="utf-8").read()

# якщо вже є позначка mini_guide_v1 — не дублюємо
if "mini_guide_v1" in s and "EARN: decision=scale" in s:
    print("Already marked; no changes."); sys.exit(0)

# Додаємо штамп одразу під заголовок журналу змін
pat = r"(## 7\) Журнал змін.*?\n)"
ns, n = re.subn(pat, r"\1" + stamp, s, count=1, flags=re.DOTALL)

# Якщо розділ не знайдено — додаємо в кінець
if n == 0:
    ns = s + "\n## 7) Журнал змін (свіже зверху)\n" + stamp

io.open(P, "w", encoding="utf-8").write(ns)
print("MANIFEST: mini_guide_v1 → залоговано.")
