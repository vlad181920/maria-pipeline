import os, json, glob, time, pathlib

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EARN = os.path.join(BASE, "artifacts", "earn")
DEC_PATH = os.path.join(EARN, "channel_decision.json")
EXP_ROOT = os.path.join(EARN, "experiments")
REPORT_OUT = os.path.join(BASE, "artifacts", "reports", "earn_decision.json")

def latest_exp():
    exps = sorted([p for p in glob.glob(os.path.join(EXP_ROOT, "*")) if os.path.isdir(p)])
    return exps[-1] if exps else None

def jload(p, default=None):
    try:
        with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default

def jdump(p, obj):
    pathlib.Path(os.path.dirname(p)).mkdir(parents=True, exist_ok=True)
    with open(p,"w",encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def write_text(p, s):
    pathlib.Path(os.path.dirname(p)).mkdir(parents=True, exist_ok=True)
    with open(p,"w",encoding="utf-8") as f: f.write(s)

def decide(metrics, policy):
    leads = int(metrics.get("leads",0))
    conv  = int(metrics.get("conversions",0))
    rev   = float(metrics.get("revenue_usd",0.0))
    tmin  = int(metrics.get("time_spent_min",0))
    max_h = int((policy or {}).get("max_hours", 6) or 6)
    cap   = max(1, max_h*60)
    ratio = round(tmin / cap, 3)

    # Просте дерево рішень (агностичне)
    reasons=[]
    if conv > 0 or rev > 0:
        decision="scale"; reasons.append("conversion_or_revenue")
    elif leads > 0:
        decision="scale"; reasons.append("lead_signal")
    elif tmin >= cap and leads==0 and conv==0:
        decision="stop"; reasons.append("time_budget_exhausted_no_signal")
    elif ratio >= 0.8 and leads==0 and conv==0:
        decision="pivot"; reasons.append("80pct_budget_no_signal")
    else:
        decision="continue"; reasons.append("collect_more_data")

    return {
        "decision": decision,
        "reasons": reasons,
        "time_ratio": ratio,
        "budget_min": cap,
        "snapshot": {"leads":leads,"conversions":conv,"revenue_usd":rev,"time_spent_min":tmin}
    }

def main():
    exp = latest_exp()
    if not exp:
        print("no experiment found"); return
    rpath = os.path.join(exp, "result.json")
    res = jload(rpath, {}) or {}
    metrics = res.get("metrics", {})
    policy = (jload(DEC_PATH, {}) or {}).get("policy", {"max_hours":6, "site_lockin":False})

    out = decide(metrics, policy)
    out["experiment"] = os.path.basename(exp)
    out["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    jdump(REPORT_OUT, out)

    # оновити result.json (decision + нотатка)
    notes = res.setdefault("metrics", {}).setdefault("notes", [])
    notes.append(f"[auto] decision={out['decision']} reasons={','.join(out['reasons'])} time_ratio={out['time_ratio']}")
    res["decision"] = out["decision"]
    # статус не чіпаємо, але можемо віддзеркалити next_action
    res["next_action"] = {"scale":"prepare_scale_plan","pivot":"adjust_message","stop":"close_experiment","continue":"collect_more_signals"}[out["decision"]]

    # якщо scale — створити агностичний scale_plan.md
    if out["decision"] == "scale":
        spath = os.path.join(exp, "scale_plan.md")
        scale_md = f"""# Scale plan (агностичний)
Згенеровано: {out['generated_at']}

## Причини
- {', '.join(out['reasons'])}
- метрики: leads={metrics.get('leads',0)}, conv={metrics.get('conversions',0)}, revenue=${metrics.get('revenue_usd',0.0)}

## Кроки (без платформ)
1) Розширити **one-pager → mini-guide v1** (додати приклад, інструкції, чеклист на 2 тижні).
2) Підготувати **2–3 варіанти меседжів** під ICP (зміна заголовка/перших 150 слів).
3) **Дистрибуція типу** обраного каналу (owned longform): 
   - зібрати прев’ю-сніпети з deliverables/snippets.md,
   - доставити їх у відповідні **типи носіїв** (конкретний вибір — автономно).
4) Виміряти: +ліди/+конверсії, час, нотатки → `result.json` → `metrics_report.py`.

## Умови
- Не фіксуватись на конкретній платформі.
- Дотримуватись бюджету часу: ≤ {policy.get('max_hours',6)} год (залишок ≈ {max(0, int(policy.get('max_hours',6)*60 - int(metrics.get('time_spent_min',0))))} хв).
"""
        write_text(spath, scale_md)

    jdump(rpath, res)
    print(REPORT_OUT)

if __name__ == "__main__":
    main()
