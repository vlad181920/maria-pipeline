import os, json, glob, time, sys, textwrap

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXP_ROOT = os.path.join(BASE, "artifacts", "earn", "experiments")
DAILY = os.path.join(BASE, f"artifacts/reports/earnings_daily_{time.strftime('%Y-%m-%d')}.json")

def latest_exp():
    exps = sorted([p for p in glob.glob(os.path.join(EXP_ROOT,"*")) if os.path.isdir(p)])
    return exps[-1] if exps else None

def load_json(p, default=None):
    try:
        with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default

def short(s, n=100):
    s = (s or "").strip()
    return s if len(s)<=n else s[:n-1]+"…"

def main():
    exp_dir = latest_exp()
    if not exp_dir:
        print("no experiments found"); sys.exit(0)
    rpath = os.path.join(exp_dir, "result.json")
    res = load_json(rpath, {})
    metrics = res.get("metrics", {})
    probes = res.get("probes", [])
    print(f"=== EXP: {os.path.basename(exp_dir)} ===")
    print(f"status: {res.get('status','')}")
    print(f"archetype: {res.get('archetype','')}")
    print("--- METRICS ---")
    print(f"leads={metrics.get('leads',0)}  conv={metrics.get('conversions',0)}  revenue=${metrics.get('revenue_usd',0.0):.2f}  time_min={metrics.get('time_spent_min',0)}  cost=${metrics.get('cost_usd',0.0):.2f}")
    if metrics.get("notes"):
        print("notes:")
        for n in metrics["notes"][-3:]:
            print(" -", short(n, 120))
    print("--- PROBES ---")
    for i, p in enumerate(probes, 1):
        st = p.get("status","planned")
        print(f"{i}) {p.get('name')}  [{st}]  id={p.get('id')}")
        ev = p.get("events", [])
        if ev:
            last_notes = [e.get("text","") for e in ev if e.get("event")=="note"][-1:]
            for ln in last_notes:
                print("   note:", short(ln, 120))
    print("--- DAILY SUMMARY ---")
    daily = load_json(DAILY, {})
    if daily:
        tot = daily.get("totals", {})
        rec = daily.get("recommendation", "")
        print(f"totals: leads={tot.get('leads',0)} conv={tot.get('conversions',0)} revenue=${tot.get('revenue_usd',0.0):.2f} time_min={tot.get('time_spent_min',0)} cost=${tot.get('cost_usd',0.0):.2f}")
        print("decision:", rec)
    else:
        print("(no daily report yet)")
    print(f"\nfiles:\n - {rpath}\n - {DAILY}")
if __name__ == "__main__":
    main()
