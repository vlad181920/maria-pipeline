import io, os, re, datetime, sys
P="project_manifest.md"
now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

if not os.path.exists(P):
    print("project_manifest.md not found"); sys.exit(1)

s=io.open(P,"r",encoding="utf-8").read()

# знайти межі розділу 5
m=re.search(r"(##\s*5\)[^\n]*\n)", s)
if m:
    start=m.start(1)
    # кінець — перед наступним "## "
    m2=re.search(r"\n##\s*\d+\)", s[m.end(1):])
    end = m.end(1)+ (m2.start(0) if m2 else 0)
else:
    # якщо не знайшли — додамо розділ в кінець
    start=len(s); end=len(s)
    s += "\n\n## 5) АКТИВНИЙ БЛОК\n"

section=s[start:end]
title="### DoD — Шар автономного заробітку (агностичний)"
checklist = [
    "- [x] Signals → artifacts/earn/signals.jsonl",
    "- [x] Strategy → artifacts/earn/strategy.json",
    "- [x] Experiment scaffold → artifacts/earn/experiments/*",
    "- [x] Metrics report → artifacts/reports/earnings_daily_YYYY-MM-DD.json",
]

if title in section:
    # позначити пункти як виконані (на випадок, якщо були [ ])
    for item in checklist:
        section=re.sub(re.escape(item.replace("[x]","[ ]")), item, section)
else:
    block = "\n" + title + "\n" + "\n".join(checklist) + "\n"
    section += block

# замінити секцію в тексті
ns = s[:start] + section + s[end:]

# штамп у журнал змін (розділ 7)
stamp=f"\n- [{now}] DoD (EARN layer): Signals→Strategy→Experiment→Metrics — мінімальний E2E готовий.\n"
m7=re.search(r"(##\s*7\)\s*Журнал змін[^\n]*\n)", ns)
if m7:
    insert_at=m7.end(1)
    ns = ns[:insert_at] + stamp + ns[insert_at:]
else:
    ns += "\n\n## 7) Журнал змін\n" + stamp

io.open(P,"w",encoding="utf-8").write(ns)
print("MANIFEST: EARN layer DoD (мінімальний) позначено та залоговано.")
