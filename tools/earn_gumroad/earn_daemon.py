import os, time, json, glob, subprocess, pathlib
BASE=os.environ.get("MARIA_HOME") or os.getcwd()
LOG=pathlib.Path(BASE)/"artifacts/logs/earn_daemon.log"
ROOT=pathlib.Path(BASE)/"artifacts/gumroad"
PLAN=ROOT/"plans"/"upload_plan.json"
FLAG="uploaded.flag"

def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG,"a",encoding="utf-8") as f: f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ")+msg+"\n")
    print(msg)

def have_creds():
    env_path=ROOT/".env"
    if not env_path.exists(): return False
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("GUMROAD_EMAIL=") or line.startswith("GUMROAD_SESSION_COOKIE="):
            return True
    return False

def product_dirs():
    for d in sorted(ROOT.glob("*")):
        if d.is_dir() and (d/"listing.json").exists():
            yield d

def make_plan():
    subprocess.run(["python3","tools/earn_gumroad/make_upload_plan.py"],cwd=BASE, check=False)

def upload():
    out=subprocess.run(["python3","tools/earn_gumroad/gumroad_uploader.py"],cwd=BASE, capture_output=True, text=True)
    log("uploader_out: "+(out.stdout.strip() or "(empty)"))
    if out.stderr.strip(): log("uploader_err: "+out.stderr.strip())
    rep_path=(ROOT/"upload_report.json")
    if not rep_path.exists(): return []
    try: 
        rep=json.loads(rep_path.read_text(encoding="utf-8"))
        return rep.get("items",[])
    except: return []

def mark_uploaded(items):
    ok_slugs=set([i["slug"] for i in items if i.get("ok")])
    for d in product_dirs():
        lj=json.loads((d/"listing.json").read_text(encoding="utf-8"))
        if lj["slug"] in ok_slugs:
            (d/FLAG).write_text("ok", encoding="utf-8")

def cycle():
    # 1) якщо нема ідей — згенерувати
    ideas=ROOT/"ideas.jsonl"
    if not ideas.exists() or len(ideas.read_text(encoding="utf-8").strip())<10:
        subprocess.run(["python3","tools/earn_gumroad/idea_miner.py"],cwd=BASE, check=False)
    # 2) збудувати 1 продукт, якщо нема нових без прапорця
    need=[d for d in product_dirs() if not (d/FLAG).exists()]
    if not need:
        subprocess.run(["python3","tools/earn_gumroad/product_builder.py"],cwd=BASE, check=False)
        need=[d for d in product_dirs() if not (d/FLAG).exists()]
    # 3) запакувати все, де немає zip/listing
    subprocess.run(["python3","tools/earn_gumroad/package_product.py"],cwd=BASE, check=False)
    # 4) якщо немає облікових даних — чекаємо
    if not have_creds():
        log("no creds yet (.env), waiting…"); return
    # 5) сформувати план і завантажити
    make_plan()
    items=upload()
    mark_uploaded(items)
    log("uploaded_ok="+str([i['slug'] for i in items if i.get('ok')]))

if __name__=="__main__":
    log("earn_daemon started")
    while True:
        try:
            cycle()
        except Exception as e:
            log("ERROR: "+str(e))
        time.sleep(3600)  # раз на годину
