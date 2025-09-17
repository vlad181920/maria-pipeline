import os, sys, json, glob, re, time, argparse
from datetime import datetime

AGENTS_DIR = os.path.join("artifacts","agents")
os.makedirs(AGENTS_DIR, exist_ok=True)
LOCK_STALE_SEC = 600

def safe_slug(s):
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'[^A-Za-z0-9\-_А-Яа-яЁёІіЇїЄєҐґ]+', '-', s)
    s = s.strip('-')
    return s or "agent"

def lock_path_for(title):
    slug = safe_slug(title)
    return os.path.join(AGENTS_DIR, f".launch.{slug}.lock")

def acquire_lock(title):
    path = lock_path_for(title)
    try:
        if os.path.exists(path):
            age = time.time() - os.path.getmtime(path)
            if age > LOCK_STALE_SEC:
                os.remove(path)
    except Exception:
        pass
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except FileExistsError:
        return False

def release_lock(title):
    path = lock_path_for(title)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

def find_existing(title):
    items = []
    for cfg in glob.glob(os.path.join(AGENTS_DIR, "*", "config.json")):
        try:
            with open(cfg,"r",encoding="utf-8") as f:
                j = json.load(f)
            if j.get("title") == title and os.path.isdir(os.path.dirname(cfg)):
                created = j.get("created") or ""
                items.append((created, os.path.dirname(cfg), j))
        except Exception:
            pass
    if not items:
        return None
    items.sort(reverse=True)
    return items[0]

def create_new(title, reason):
    ts_dir = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = safe_slug(title)
    dname = f"{ts_dir}_{slug}"
    dpath = os.path.join(AGENTS_DIR, dname)
    os.makedirs(os.path.join(dpath, "output"), exist_ok=True)
    created_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cfg = {"created": created_ts, "title": title, "reason": reason, "status": "created", "dir": dpath}
    with open(os.path.join(dpath, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    with open(os.path.join(dpath, "log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": created_ts, "event": "created", "reason": reason}, ensure_ascii=False) + "\n")
    with open(os.path.join(dpath, "output", "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\nReason: {reason}\n")
    with open(os.path.join(AGENTS_DIR, "index.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"created": created_ts, "title": title, "dir": dpath}, ensure_ascii=False) + "\n")
    return cfg

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("title")
    p.add_argument("-r","--reason", default="")
    p.add_argument("--hold-secs", type=float, default=0.0)
    return p.parse_args()

def main():
    args = parse_args()
    title = args.title
    reason = args.reason
    if not acquire_lock(title):
        print(json.dumps({"ok": False, "status": "busy", "err": "another launch is in progress for this title"}, ensure_ascii=False))
        sys.exit(2)
    try:
        if args.hold_secs > 0:
            time.sleep(args.hold_secs)
        existing = find_existing(title)
        if existing:
            created, path, j = existing
            print(json.dumps({"created": created, "title": title, "reason": reason, "status": "exists", "dir": path}, ensure_ascii=False, indent=2))
            return
        cfg = create_new(title, reason)
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
    finally:
        release_lock(title)

if __name__ == "__main__":
    main()
def launch_subagent(title, reason="", hold_secs=0, timeout=60):
    import os, sys, json, subprocess
    script = os.path.abspath(__file__)
    cmd = [sys.executable, script, title]
    if reason:
        cmd += ["-r", reason]
    if hold_secs:
        cmd += ["--hold-secs", str(int(hold_secs))]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    out = (p.stdout or "").strip()
    last = out.splitlines()[-1] if out else ""
    try:
        return json.loads(last)
    except Exception:
        return {"ok": False, "returncode": p.returncode, "stdout": out, "stderr": p.stderr}
