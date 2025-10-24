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
    """Підтримує:
       - абсолютні значення: '12', '3.5'
       - інкременти: '+2', '+0.5'
       - декременти: '-1'
    """
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

def main():
    ap = argparse.ArgumentParser(description="Оновити метрики для активного експерименту (агностично до платформ).")
    ap.add_argument("--exp", help="Шлях до експерименту (каталог з result.json). Якщо не задано — візьмемо останній.", default=None)

    ap.add_argument("--leads",       help="Ліди (напр. '3' або '+2')", default=None)
    ap.add_argument("--conversions", help="Конверсії (напр. '1' або '+1')", default=None)
    ap.add_argument("--revenue",     help="Дохід у USD (напр. '19' або '+9.99')", default=None)
    ap.add_argument("--time",        help="Витрачений час у хвилинах (напр. '30' або '+15')", default=None)
    ap.add_argument("--cost",        help="Грошові витрати у USD (напр. '0' або '+2.5')", default=None)
    ap.add_argument("--note",        help="Додати примітку (можна передавати кілька разів)", action="append", default=[])

    ap.add_argument("--report",      help="Після оновлення згенерувати денний звіт", action="store_true")
    args = ap.parse_args()

    exp_dir = args.exp
    if not exp_dir:
        exp_dir = latest_experiment_dir()
    if not exp_dir or not os.path.isdir(exp_dir):
        print("no experiment directory found", file=sys.stderr); sys.exit(1)

    rpath = os.path.join(exp_dir, "result.json")
    if not os.path.exists(rpath):
        print(f"result.json not found in {exp_dir}", file=sys.stderr); sys.exit(1)

    data = load_json(rpath)
    metrics = data.setdefault("metrics", {})
    # ініціалізувати поля, якщо їх нема
    leads        = int(metrics.get("leads", 0) or 0)
    conversions  = int(metrics.get("conversions", 0) or 0)
    revenue      = float(metrics.get("revenue_usd", 0.0) or 0.0)
    time_min     = int(metrics.get("time_spent_min", 0) or 0)
    cost_usd     = float(metrics.get("cost_usd", 0.0) or 0.0)
    notes        = list(metrics.get("notes", []) or [])

    # застосувати оновлення
    leads       = parse_delta(args.leads,       leads,       int)
    conversions = parse_delta(args.conversions, conversions, int)
    revenue     = parse_delta(args.revenue,     revenue,     float)
    time_min    = parse_delta(args.time,        time_min,    int)
    cost_usd    = parse_delta(args.cost,        cost_usd,    float)
    if args.note:
        for n in args.note:
            if n and n.strip():
                notes.append(n.strip())

    metrics.update({
        "leads": int(leads),
        "conversions": int(conversions),
        "revenue_usd": float(revenue),
        "time_spent_min": int(time_min),
        "cost_usd": float(cost_usd),
        "notes": notes
    })

    # auto-status
    if data.get("status","") in ("initialized","prepared"):
        if conversions > 0 or leads > 0 or time_min > 0:
            data["status"] = "running"

    # бекап + запис
    bp = backup(rpath)
    dump_json(rpath, data)

    print("updated:", rpath)
    print("backup :", bp)
    print(json.dumps({"leads":leads,"conversions":conversions,"revenue_usd":revenue,"time_spent_min":time_min,"cost_usd":cost_usd}, ensure_ascii=False))

    if args.report:
        # генеруємо денний звіт
        os.system(f'python3 "{REPORT}"')
