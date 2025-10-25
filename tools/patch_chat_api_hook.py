import re, os
p="tools/chat_api.py"
s=open(p,"r",encoding="utf-8").read()
if "from tools.after_chat_hook import hook" not in s:
    if "from maria_brain import chat" in s:
        s=s.replace("from maria_brain import chat","from maria_brain import chat\nfrom tools.after_chat_hook import hook")
    else:
        s="from tools.after_chat_hook import hook\n"+s
m=re.search(r"@app\.post\([\"']\/api\/chat[\"']\)[\s\S]*?def\s+[A-Za-z_]\w*\s*\([^)]*\):\s*\n", s)
if m and "hook(" not in s:
    ins="    try:\n        _t=\"\"\n        for _k in (\"text\",\"message\",\"q\",\"prompt\"):\n            try:\n                _t = locals().get(_k) or _t\n            except:\n                pass\n        if not _t:\n            try:\n                _t = payload.get(\"text\") if isinstance(payload, dict) else _t\n            except:\n                pass\n        hook(_t)\n    except:\n        pass\n"
    s=s[:m.end()]+ins+s[m.end():]
open(p,"w",encoding="utf-8").write(s)
print("OK")
