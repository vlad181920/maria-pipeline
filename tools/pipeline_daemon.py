import os, sys, time, json, subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "thought_pipeline.py")
LOG_DIR = os.path.join(ROOT, "artifacts", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

OUT_LOG = os.path.join(LOG_DIR, "pipeline_daemon.out")
ERR_LOG = os.path.join(LOG_DIR, "pipeline_daemon.err")
STAT_LOG = os.path.join(LOG_DIR, "pipeline_daemon.log")

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run_once():
    if not os.path.exists(SCRIPT):
        msg = {"ts": now(), "ok": False, "err": f"missing {SCRIPT}"}
        with open(STAT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        return
    p = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True)
    if p.returncode == 0:
        out = p.stdout.strip()
        with open(OUT_LOG, "a", encoding="utf-8") as f:
            f.write(out + ("\n" if not out.endswith("\n") else ""))
        try:
            rec = json.loads(out)
        except Exception:
            rec = {"raw": out}
        with open(STAT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": now(), "ok": True, "rec": rec}, ensure_ascii=False) + "\n")
    else:
        err = p.stderr.strip()
        with open(ERR_LOG, "a", encoding="utf-8") as f:
            f.write(err + ("\n" if not err.endswith("\n") else ""))
        with open(STAT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": now(), "ok": False, "err": err}, ensure_ascii=False) + "\n")

def main():
    interval = 45
    while True:
        run_once()
        time.sleep(interval)

if __name__ == "__main__":
    main()
