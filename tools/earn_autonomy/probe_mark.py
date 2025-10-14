import os, json, glob, argparse, shutil, time, sys

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXP_ROOT = os.path.join(BASE, "artifacts", "earn", "experiments")
REPORT = os.path.join(BASE, "tools", "earn_autonomy", "metrics_report.py")

def latest_experiment_dir():
    exps = sorted([p for p in glob.glob(os.path.join(EXP_ROOT, "*")) if os.path.isdir(p)])
    return exps[-1] if exps else None

def load_json(p):
    with open(p,"r",encoding="utf-8") as f: return json.load(f)

def dump_json(p, obj):
    with open(p,"w",encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def backup(p):
    ts = time.strftime("%Y%m%d_%H%M%S")
    bp = p + f".bak_{ts}"
    shutil.copy2(p, bp)
    return bp

def parse_delta(s, current, cast=float):
    if s is None: return current
    s = str(s).strip()
    if s.startswith(("+","-")) and s not in ("+0","-0"):
        try:
            return cast(current + cast(s))
        except Exception:
            return current
    try:
        return cast(s)
    except Exception:
        return current

def find_probe(data, pid=None, idx=None):
    probes = data.get("probes") or []
    if pid:
        for p in probes:
            if p.get("id")==pid: return p
        return None
    if idx is not None and 1 <= idx <= len(probes):
        return probes[idx-1]
    return None

def mark_status(probe, status):
    if not status: return
    status = status.lower()
    allowed = {"planned","doing","done","stopped"}
    if status not in allowed: return
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    probe["status"] = status
    evs = probe.setdefault("events", [])
    evs.append({"ts": now, "event": f"status:{status}"})
    if status == "doing" and not probe.get("started_at"):
        probe["started_at"] = now
    if status in ("done","stopped"):
        probe["finished_at"] = now

def main():
    ap = argparse.ArgumentParser(description="Позначити прогрес по мікро-пробі та оновити метрики експерименту.")
    ap.add_argument("--exp", help="Каталог експерименту (якщо не вказано — останній).")
    sel = ap.add_mutually_exclusive_group(required=False)
    sel.add_argument("--id", help="ID проби (з probes.md/result.json).")
    sel.add_argument("--idx", type=int, help="Номер проби 1|2|3.")

    ap.add_argument("--status", help="planned|doing|done|stopped")
    ap.add_argument("--note", action="append", default=[], help="Додати примітку (можна кілька разів).")

    ap.add_argument("--time", help="Мінут часу: '30' або '+15'")
    ap.add_argument("--leads", help="Ліди: '1' або '+1'")
    ap.add_argument("--conversions", help="Конверсії: '0' або '+1'")
    ap.add_argument("--revenue", help="Дохід USD: '19' або '+19'")
    ap.add_argument("--cost", help="Витрати USD: '0' або '+2.5'")

    ap.add_argument("--report", action="store_true", help="Після оновлення — згенерувати денний звіт.")
    args = ap.parse_args()

    exp_dir = args.exp or latest_experiment_dir()
    if not exp_dir or not os.path.isdir(exp_dir):
        print("no experiment directory found", file=sys.stderr); sys.exit(1)

    rpath = os.path.join(exp_dir, "result.json")
    if not os.path.exists(rpath):
        print(f"result.json not found in {exp_dir}", file=sys.stderr); sys.exit(1)

    data = load_json(rpath)
    data.setdefault("metrics", {})
    data.setdefault("probes", [])

    probe = find_probe(data, pid=args.id, idx=args.idx)
    if not probe:
        print("probe not found (use --id або --idx 1|2|3)", file=sys.stderr); sys.exit(1)

    # статус
    mark_status(probe, args.status)

    # примітки (локально на пробі і в загальних метриках)
    if args.note:
        pev = probe.setdefault("events", [])
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        for n in args.note:
            if n and n.strip():
                pev.append({"ts": now, "event": "note", "text": n.strip()})
        mnotes = data["metrics"].setdefault("notes", [])
        mnotes.extend([n.strip() for n in args.note if n and n.strip()])

    # агреговані метрики
    m = data["metrics"]
    leads       = parse_delta(args.leads,       int(m.get("leads",0)),       int)
    conv        = parse_delta(args.conversions, int(m.get("conversions",0)), int)
    revenue     = parse_delta(args.revenue,     float(m.get("revenue_usd",0.0)), float)
    time_min    = parse_delta(args.time,        int(m.get("time_spent_min",0)), int)
    cost_usd    = parse_delta(args.cost,        float(m.get("cost_usd",0.0)), float)
    m.update({
        "leads": int(leads),
        "conversions": int(conv),
        "revenue_usd": float(revenue),
        "time_spent_min": int(time_min),
        "cost_usd": float(cost_usd),
    })

    # авто-перехід статусу експерименту
    if data.get("status") in ("initialized","prepared","planned"):
        if (args.status and args.status.lower()=="doing") or leads>0 or conv>0 or time_min>0:
            data["status"] = "running"

    bp = backup(rpath)
    dump_json(rpath, data)

    print("updated:", rpath)
    print("backup :", bp)
    print(json.dumps({
        "probe": probe.get("id"),
        "status": probe.get("status",""),
        "metrics": {
            "leads": leads, "conversions": conv,
            "revenue_usd": revenue, "time_spent_min": time_min, "cost_usd": cost_usd
        }}, ensure_ascii=False))

    if args.report:
        os.system(f'python3 "{REPORT}"')
