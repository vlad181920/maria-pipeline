import re, os, sys, io
p="maria_brain.py"
s=open(p,"r",encoding="utf-8").read()

# 1) переконаймося, що імпорт є
if "from tools.kb import search" not in s:
    s="from tools.kb import search\n"+s

# 2) визначимо ім'я параметра chat(...)
m=re.search(r"def\s+chat\s*\((.*?)\)\s*:", s, flags=re.S)
param="text"
if m:
    params=[x.strip() for x in m.group(1).replace("\n"," ").split(",") if x.strip()]
    cand=[]
    for a in params:
        a=a.split("=")[0].strip()
        a=a.replace("*","").replace("/","").strip()
        if a and a!="self":
            cand.append(a)
    if cand:
        param=cand[0]

# 3) замінимо всі згадки user_text на фактичний параметр
s=re.sub(r"\buser_text\b", param, s)

# 4) якщо є kb_hits = search(...), але немає kb_note — додамо kb_note відразу після першого виклику
if "kb_hits = search(" in s and "kb_note" not in s:
    lines=s.splitlines(True)
    for i,l in enumerate(lines):
        if "kb_hits = search(" in l:
            indent = l[:len(l)-len(l.lstrip())]
            note = indent + "kb_note = '\\n'.join([h.get('preview','')[:280] for h in kb_hits])\n"
            lines.insert(i+1, note)
            s="".join(lines)
            break

open(p,"w",encoding="utf-8").write(s)
print(f"OK param={param}")
