import os, re, json
from lesson_store import add_lesson
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
LOGDIR=os.path.join(BASE,"artifacts","logs")
os.makedirs(LOGDIR,exist_ok=True)
pat = re.compile(r"(ERROR|Traceback[\s\S]+?)(?:\n\n|\Z)", re.MULTILINE)
added=0
for name in sorted(os.listdir(LOGDIR)):
    if not name.endswith(".log"): continue
    p=os.path.join(LOGDIR,name)
    try:
        txt=open(p,"r",encoding="utf-8",errors="ignore").read()
    except: 
        continue
    for m in pat.finditer(txt):
        block=m.group(0).strip()
        if not block: continue
        title=f"Помилка з {name}"
        content=("Причина/trace:\n"+block+"\n\nАнти-урок:\n- Виявляти цей патерн у майбутньому логах\n- Додати ретрай/валідацію в місці виникнення")
        add_lesson(title, content, tags=["error","autolearn"], source=f"log:{name}", severity="warn")
        added+=1
print(added)
