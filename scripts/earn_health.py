#!/usr/bin/env python3
import os, sys, json, glob, subprocess, time, pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
EARN_ROOT = ROOT / "artifacts" / "earn"
EXPERIMENTS_DIR = EARN_ROOT / "experiments"

def _read_json(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return {"error": f"bad json in {p}"}

def _latest_experiment_dir():
    c=[]
    for d in glob.glob(str(EXPERIMENTS_DIR / "*")):
        if os.path.isdir(d):
            c.append((os.path.getmtime(d), d))
    if not c:
        return None
    c.sort(key=lambda x:x[0], reverse=True)
    return pathlib.Path(c[0][1])

def _check_launchd_service(label):
    try:
        user_id=str(os.getuid())
        cmd=["launchctl","print",f"gui/{user_id}/{label}"]
        proc=subprocess.run(cmd,capture_output=True,text=True)
        if proc.returncode!=0:
            return{"label":label,"loaded":False,"running":False,"detail":(proc.stderr.strip() or proc.stdout.strip())[:500]}
        out=proc.stdout
        running=("state = running" in out) or ("state = active" in out)
        return{
            "label":label,
            "loaded":True,
            "running":running,
            "detail":out.strip()[:500],
        }
    except Exception as e:
        return{"label":label,"error":str(e)}

def collect():
    exp_dir=_latest_experiment_dir()
    if exp_dir is None:
        exp_info={"error":"no experiment dirs"}
        metrics=None
        config=None
    else:
        metrics=_read_json(exp_dir/"metrics_summary.json")
        config=_read_json(exp_dir/"config.json")
        exp_info={
            "path":str(exp_dir),
            "dir_name":exp_dir.name,
            "mtime":os.path.getmtime(exp_dir),
            "mtime_iso":datetime.fromtimestamp(os.path.getmtime(exp_dir)).isoformat(timespec="seconds"),
        }

    loop_state=_check_launchd_service("com.maria.earn.loop")
    guard_state=_check_launchd_service("com.maria.guard")

    leads=None
    conversions=None
    revenue_total=None
    conversion_rate=None
    if isinstance(metrics,dict):
        leads=metrics.get("leads")
        conversions=metrics.get("conversions")
        revenue_total=metrics.get("revenue_total")
        conversion_rate=metrics.get("conversion_rate")

    active_variant=None
    active_price=None
    wave=None
    if isinstance(config,dict):
        active_variant=config.get("active_variant")
        active_price=config.get("active_price_usd") or config.get("active_price")
        wave=config.get("wave")

    machine={
        "ts_unix":time.time(),
        "ts_iso":datetime.now().isoformat(timespec="seconds"),
        "experiment":exp_info,
        "business":{
            "active_variant":active_variant,
            "active_price_usd":active_price,
            "wave":wave,
            "leads":leads,
            "conversions":conversions,
            "revenue_total_usd":revenue_total,
            "conversion_rate":conversion_rate,
        },
        "process":{
            "loop":loop_state,
            "guard":guard_state,
        },
        "logs":{
            "loop":str(EARN_ROOT/"logs"),
            "guard.out":str(EARN_ROOT/"logs"/"guard.out"),
            "guard.err":str(EARN_ROOT/"logs"/"guard.err"),
        },
    }

    human=[]
    human.append("# Maria Earn Health Report")
    human.append(f"- generated: {machine['ts_iso']}")
    human.append("")
    human.append("## Experiment")
    if "error" in exp_info:
        human.append(f"- experiment: {exp_info['error']}")
    else:
        human.append(f"- dir: {exp_info['dir_name']}")
        human.append(f"- last update: {exp_info['mtime_iso']}")
    human.append("")
    human.append("## Business")
    human.append(f"- active variant: {active_variant or '??'}")
    human.append(f"- active price (USD): {active_price if active_price is not None else '??'}")
    human.append(f"- wave: {wave if wave is not None else '??'}")
    human.append(f"- leads: {leads if leads is not None else '??'}")
    human.append(f"- conversions: {conversions if conversions is not None else '??'}")
    human.append(f"- revenue_total_usd: {revenue_total if revenue_total is not None else '??'}")
    human.append(f"- conversion_rate: {conversion_rate if conversion_rate is not None else '??'}")
    human.append("")
    human.append("## Process")
    for lbl,st in (("loop",loop_state),("guard",guard_state)):
        if st is None:
            human.append(f"- {lbl}: no data")
        elif st.get("error"):
            human.append(f"- {lbl}: ERROR {st['error']}")
        else:
            human.append(f"- {lbl}: loaded={st.get('loaded')} running={st.get('running')} label={st.get('label')}")
    human.append("")
    human.append("## Logs")
    human.append(f"- {machine['logs']['loop']}")
    human.append(f"- {machine['logs']['guard.out']}")
    human.append(f"- {machine['logs']['guard.err']}")
    human.append("")

    return machine,"\n".join(human)

if __name__=="__main__":
    machine,human=collect()
    print(json.dumps(machine,ensure_ascii=False,indent=2))
    print("\n---\n")
    print(human)
