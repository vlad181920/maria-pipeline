import re,io,sys,os
p="maria_brain.py"
s=open(p,"r",encoding="utf-8").read()
if "from tools.kb import search" not in s:
    s="from tools.kb import search\n"+s
pat=r"(def\s+chat\s*\([^)]*\):\s*\n)"
inject=("    kb_query_text = str(locals().get('user_text') or locals().get('text') or "
        "locals().get('q') or locals().get('prompt') or '')\n"
        "    kb_hits = search(kb_query_text, k=3)\n"
        "    kb_note = '\\n'.join([h.get('preview','')[:280] for h in kb_hits])\n")
if re.search(pat,s) and "kb_hits = search(" not in s:
    s=re.sub(pat, r"\\1"+inject, s, count=1)
elif "kb_hits = search(" in s and "kb_query_text" not in s:
    s=re.sub(r"kb_hits\s*=\s*search\([^\\n]*\)\s*\\n", inject, s, count=1)
open(p,"w",encoding="utf-8").write(s)
print("OK")
