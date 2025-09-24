import re, os
p="maria_brain.py"
s=open(p,"r",encoding="utf-8").read()

if "from tools.after_chat_hook import hook as after_hook" not in s:
    s="from tools.after_chat_hook import hook as after_hook\n"+s

m=re.search(r"def\s+chat\s*\((.*?)\)\s*:\s*\n", s, flags=re.S)
if not m:
    open(p,"w",encoding="utf-8").write(s); print("NO_CHAT_DEF"); raise SystemExit(0)

params=[x.strip().split("=")[0].replace("*","").replace("/","").strip() for x in m.group(1).replace("\n"," ").split(",") if x.strip()]
param="text"
for a in params:
    if a and a!="self":
        param=a; break

start=m.end()
inject=f"    try:\n        after_hook({param})\n    except Exception:\n        pass\n"
body=s[start:]
if "after_hook(" not in body:
    s=s[:start]+inject+s[start:]

open(p,"w",encoding="utf-8").write(s)
print(f"OK param={param}")
