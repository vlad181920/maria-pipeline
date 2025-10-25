import os,sys,json
sys.path.insert(0, os.getcwd())
from maria_brain import chat
q=" ".join(sys.argv[1:]).strip()
res=chat(q)
if isinstance(res,dict):
    print(res.get("text") or res.get("reply") or json.dumps(res,ensure_ascii=False))
else:
    print(str(res))
