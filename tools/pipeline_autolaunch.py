import os, json, time, subprocess, io
LOG="artifacts/logs/pipeline.log"
STATE="artifacts/agents/autolaunch.offset"
HIST="artifacts/agents/autolaunch.log"
os.makedirs(os.path.dirname(STATE), exist_ok=True)
def read_offset():
    try:
        return int(open(STATE,"r",encoding="utf-8").read().strip())
    except:
        return 0
def write_offset(v):
    with open(STATE,"w",encoding="utf-8") as f:
        f.write(str(v))
def handle(rec):
    winner=str(rec.get("winner",""))
    rec_eval=rec.get("eval") or {}
    recommended=bool(rec_eval.get("recommended"))
    goal=(rec.get("goal") or {})
    title=goal.get("title") or "Автоген: Запустити підагент"
    if "Запустити підагент" in winner and recommended:
        reason=f"auto ts={rec.get('ts','')} score={rec_eval.get('score','')} conf={rec.get('confidence','')}"
        cmd=["python3","subagent_launcher.py",title,"-r",reason]
        out=subprocess.run(cmd,capture_output=True,text=True)
        with open(HIST,"a",encoding="utf-8") as h:
            h.write((out.stdout or "").strip()+"\n")
def run_once():
    if not os.path.exists(LOG):
        return
    off=read_offset()
    with open(LOG,"rb") as f:
        f.seek(off)
        data=f.read()
        new_off=f.tell()
    if not data:
        return
    buff=io.StringIO(data.decode("utf-8","ignore"))
    for line in buff:
        line=line.strip()
        if not line: continue
        try:
            rec=json.loads(line)
            handle(rec)
        except:
            pass
    write_offset(off+len(data))
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--watch",action="store_true")
    ap.add_argument("--interval",type=float,default=2.0)
    args=ap.parse_args()
    if args.watch:
        while True:
            run_once()
            time.sleep(args.interval)
    else:
        run_once()
