import sys, json
from kb import search
q=" ".join(sys.argv[1:]).strip()
if not q:
    print("")
    sys.exit(0)
res=search(q, k=5, index_path="artifacts/kb/index.json")
for r in res:
    line=f"{r['score']}\t{r['path']}\t{r['title']}".strip()
    print(line)
    p=r.get("preview","")
    if p:
        print(p[:240].replace("\n"," ").strip())
        print("---")
