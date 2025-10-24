import os, json, time, uuid
from tools.kb import load_index, search
base=os.getcwd()
qfile=os.path.join("artifacts","thoughts","queue.jsonl")
os.makedirs(os.path.dirname(qfile), exist_ok=True)
idx=load_index("artifacts/kb/index.json")
now=time.strftime("%Y-%m-%d %H:%M:%S")
def enq(obj):
    with open(qfile,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=False)+"\n")
backlog=0
try:
    with open(qfile,"r",encoding="utf-8") as f:
        for _ in f: backlog+=1
except:
    pass
if idx.get("n_docs",0)<5:
    enq({"id":str(uuid.uuid4()),"topic":"Розширити базу знань для автономного заробітку","type":"research","created_at":now,"priority":0.9,"state":"new","result_ref":None})
hits=search("автономний заробіток підходи стратегії оцінка ризиків",k=3,index_path="artifacts/kb/index.json")
if not hits:
    enq({"id":str(uuid.uuid4()),"topic":"Знайти підходи заробітку без підказок ззовні","type":"research","created_at":now,"priority":0.85,"state":"new","result_ref":None})
if backlog<3:
    enq({"id":str(uuid.uuid4()),"topic":"Сформувати план самостійного дослідження ринків","type":"plan","created_at":now,"priority":0.8,"state":"new","result_ref":None})
print("OK")
