import re, io, datetime, os, sys
P = "project_manifest.md"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

if not os.path.exists(P):
    print("project_manifest.md not found"); sys.exit(1)

s = io.open(P, "r", encoding="utf-8").read()

# Замінити чекбокс саме для Policy Check у розділі 5 (Definition of Done)
pattern = r"(Definition of Done[\\s\\S]*?)- \\[ \\] Policy Check:([^\\n]*?)\\n"
repl    = r"\\1- [x] Policy Check:\\2\\n"
ns, n = re.subn(pattern, repl, s, flags=re.IGNORECASE)
if n == 0:
    # fallback: поміняти будь-де рядок з Policy Check невідмічений → відмічений
    ns = re.sub(r"- \\[ \\] Policy Check:", "- [x] Policy Check:", s)

stamp = f"\\n- [{now}] DoD: Policy Check пройдено (active layer без сайт-специфіки).\\n"
ns += stamp

io.open(P, "w", encoding="utf-8").write(ns)
print("MANIFEST: Policy Check → [x] і журнал оновлено.")
