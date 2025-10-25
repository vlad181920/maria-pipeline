import os, json, glob, time, re, pathlib

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXP_ROOT = os.path.join(BASE, "artifacts", "earn", "experiments")
OUT_DIR = os.path.join(BASE, "artifacts", "reports")
os.makedirs(OUT_DIR, exist_ok=True)

def parse_budget_from_readme(path):
    txt = ""
    try:
        txt = open(path, "r", encoding="utf-8").read()
    except FileNotFoundError:
        return None, None
    h = None; cash = None
    m = re.search(r"Час:\s*≤\s*(\d+)\s*год", txt)
    if m: h = int(m.group(1))
    m = re.search(r"Гроші:\s*≤\s*\$([\d\.]+)", txt)
    if m: cash = float(m.group(1))
    return h, cash

def load_result(path):
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except FileNotFoundError:
        return None

def decide(metrics, budget_h):
    leads = int(metrics.get("leads", 0) or 0)
    conv  = int(metrics.get("conversions", 0) or 0)
    rev   = float(metrics.get("revenue_usd", 0) or 0.0)
    spent_min = int(metrics.get("time_spent_min", 0) or 0)
    time_ratio = None
    if budget_h and budget_h > 0:
        time_ratio = spent_min / float(budget_h * 60)

    # правила прийняття рішень (агностичні)
    if conv >= 1 or rev > 0:
        return "scale", time_ratio
    if time_ratio is not None and time_ratio >= 1.0 and conv == 0 and leads == 0:
        return "stop", time_ratio
    if time_ratio is not None and time_ratio >= 0.25 and conv == 0 and leads == 0:
        return "pivot", time_ratio
    return "continue", time_ratio

def main():
    per_exp = []
    totals = {"leads":0, "conversions":0, "revenue_usd":0.0, "time_spent_min":0, "cost_usd":0.0}

    for exp_dir in sorted(glob.glob(os.path.join(EXP_ROOT, "*"))):
        rpath = os.path.join(exp_dir, "result.json")
        r = load_result(rpath)
        if not r: 
            continue
        readme = os.path.join(exp_dir, "README.md")
        bud_h, bud_cash = parse_budget_from_readme(readme)
        m = r.get("metrics", {})
        decision, time_ratio = decide(m, bud_h)

        # агрегати
        totals["leads"] += int(m.get("leads",0) or 0)
        totals["conversions"] += int(m.get("conversions",0) or 0)
        totals["revenue_usd"] += float(m.get("revenue_usd",0) or 0.0)
        totals["time_spent_min"] += int(m.get("time_spent_min",0) or 0)
        totals["cost_usd"] += float(m.get("cost_usd",0) or 0.0)

        per_exp.append({
            "exp_dir": os.path.basename(exp_dir),
            "archetype": r.get("archetype",""),
            "status": r.get("status",""),
            "budget_hours": bud_h,
            "budget_cash_usd": bud_cash,
            "metrics": m,
            "conv_rate": ( (m.get("conversions",0) or 0) / float(m.get("leads",1) or 1) ) if (m.get("leads",0) or 0) > 0 else 0.0,
            "time_ratio": time_ratio,
            "decision": decision
        })

    out = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "experiments": per_exp,
        "totals": totals,
        "recommendation": (
            "scale" if totals["conversions"]>=1 or totals["revenue_usd"]>0
            else "pivot" if (sum(1 for e in per_exp if (e.get('time_ratio') or 0)>=0.25 and e["metrics"].get("leads",0)==0 and e["metrics"].get("conversions",0)==0) >= 1)
            else "continue"
        )
    }
    out_path = os.path.join(OUT_DIR, f"earnings_daily_{time.strftime('%Y-%m-%d')}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(out_path)

if __name__ == "__main__":
    main()
