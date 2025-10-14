import os, json, time, pathlib, sys

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DAILY = os.path.join(BASE, f"artifacts/reports/earnings_daily_{time.strftime('%Y-%m-%d')}.json")
DEC   = os.path.join(BASE, "artifacts/reports/earn_decision.json")
METR  = os.path.join(BASE, "tools/earn_autonomy/metrics_report.py")

def jload(p, default=None):
    try:
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default

def jdump(p, obj):
    pathlib.Path(os.path.dirname(p)).mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def main():
    # якщо денного звіту ще нема — згенерувати
    if not os.path.exists(DAILY):
        os.system(f'python3 "{METR}"')
    rep = jload(DAILY, {})
    dec = jload(DEC, {})
    if not rep or not dec:
        print("nothing to merge"); sys.exit(0)

    # оновити рекомендацію та додати блок decision
    rep["recommendation"] = dec.get("decision", rep.get("recommendation", "continue"))
    rep["decision"] = {
        "decision": dec.get("decision"),
        "reasons": dec.get("reasons", []),
        "time_ratio": dec.get("time_ratio"),
        "budget_min": dec.get("budget_min"),
        "experiment": dec.get("experiment"),
        "generated_at": dec.get("generated_at"),
        "snapshot": dec.get("snapshot", {})
    }

    # спробувати поставити decision на відповідний експеримент
    exp_name = str(dec.get("experiment",""))
    for e in rep.get("experiments", []):
        if e.get("exp_dir") == exp_name:
            e["decision"] = dec.get("decision")
            break

    jdump(DAILY, rep)
    print("merged into:", DAILY)

if __name__ == "__main__":
    main()
