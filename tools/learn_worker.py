import os, json, time, hashlib, sys
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, BASE)

Q=os.path.join(BASE,"artifacts","thoughts","audit_queue.jsonl")
PROCESSED=os.path.join(BASE,"artifacts","learn","processed_ids.txt")
INS=os.path.join(BASE,"insights","learn",f"learn_{time.strftime('%Y-%m-%d_%H%M%S')}.md")
os.makedirs(os.path.dirname(PROCESSED),exist_ok=True)
os.makedirs(os.path.dirname(INS),exist_ok=True)

from tools.lesson_store import add_lesson
from tools.kb import build_index

def _h(x): return hashlib.sha1((x or "").encode("utf-8","ignore")).hexdigest()[:16]

seen=set()
try:
    with open(PROCESSED,"r",encoding="utf-8") as f:
        for line in f: seen.add(line.strip())
except: pass

done=0
try:
    with open(Q,"r",encoding="utf-8") as f:
        for line in f:
            try:
                j=json.loads(line)
            except:
                continue
            if j.get("type")!="learn": continue
            dig=_h((j.get("id","")+j.get("topic","")))
            if dig in seen: continue
            topic=(j.get("topic") or "Вчитися").strip()
            add_lesson("Урок: "+topic, "Зробити короткий ресерч і зафіксувати факти/правила по темі.\nДжерело: self-learn", tags=["learn","autolearn"], source="thought")
            with open(INS,"a",encoding="utf-8") as md:
                md.write(f"- {time.strftime('%H:%M:%S')} {topic}\n")
            with open(PROCESSED,"a",encoding="utf-8") as f2:
                f2.write(dig+"\n")
            done+=1
except FileNotFoundError:
    pass

# тихий rebuild KB (без друку у stdout)
globs=[
    "insights/**/*.md",
    "insights/**/*.jsonl",
    "artifacts/reports/**/*.md",
    "artifacts/chat/*.jsonl",
    "artifacts/lessons.jsonl",
    "project_manifest.md"
]
build_index(BASE, globs, os.path.join(BASE,"artifacts","kb","index.json"))

print(done)
