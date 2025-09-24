import os, re, sys
p="maria_brain.py"
s=open(p,"r",encoding="utf-8").read()
if "from tools.kb import search" not in s:
    s="from tools.kb import search\n"+s
pat=r"(def\s+chat\([^)]*\):\s*\n)"
if re.search(pat,s):
    if "kb_hits = search(" not in s:
        s=re.sub(pat, r"\1    kb_hits = search(user_text, k=3)\n    kb_note = '\\n'.join([h.get('preview','')[:280] for h in kb_hits])\n", s, count=1)
open(p,"w",encoding="utf-8").write(s)
print("OK")
