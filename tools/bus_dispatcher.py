#!/usr/bin/env python3
import os, sys, json, datetime, hashlib, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUS_EVENTS = os.path.join(ROOT, "bus", "events.jsonl")
BUS_CMDS   = os.path.join(ROOT, "bus", "commands.jsonl")
EVENT_SCHEMA = os.path.join(ROOT, "schemas", "event.schema.json")
CMD_SCHEMA_OLD = os.path.join(ROOT, "schemas", "command.schema.json")   # може бути з "action" або "cmd"

DEFAULT_EXP = "artifacts/earn/experiments/20250919_211414__micro-service-offer-audit-implementation"

def utcnow():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def validate(schema_path, obj):
    try:
        import jsonschema
    except ImportError:
        return True  # мʼякий режим без залежності
    if os.path.isfile(schema_path):
        schema = load_json(schema_path)
        jsonschema.validate(obj, schema)
    return True

def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def read_jsonl(path):
    if not os.path.isfile(path): return []
    out=[]
    with open(path, encoding="utf-8") as f:
        for line in f:
            s=line.strip()
            if not s: continue
            try: out.append(json.loads(s))
            except: pass
    return out

def dedup_lines(path):
    if not os.path.isfile(path): return
    seen=set(); out=[]
    with open(path, encoding="utf-8") as f:
        for line in f:
            s=line.strip()
            if not s: continue
            h=hashlib.sha1(s.encode("utf-8")).hexdigest()
            if h in seen: continue
            seen.add(h); out.append(s)
    tmp=path+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        for s in out: f.write(s+"\n")
    os.replace(tmp,path)

def sh(*args):
    return subprocess.run(list(args), cwd=ROOT, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True).stdout

# ---- EVENTS ----
def handle_event(ev):
    et = ev.get("type")
    exp = ev.get("exp_path") or DEFAULT_EXP
    exp_abs = os.path.join(ROOT, exp)

    if et in ("lead","conversion","sale","purchase"):
        # маршрутизація подій у events.jsonl експерименту
        p=os.path.join(exp_abs,"events.jsonl")
        append_jsonl(p, ev)
        dedup_lines(p)
        return f"event routed -> {p}"

    if et == "wave_switched":
        out=[]
        out.append(sh("python3","tools/metrics_aggregate.py",exp))
        out.append(sh("scripts/exp_release.sh",exp))
        out.append(sh("scripts/exp_status.sh",exp))
        return "\n".join(out)

    if et == "release_published":
        return "ack release_published"

    if et == "error":
        return "ack error"

    return f"unknown event type: {et}"

# ---- COMMANDS ----
def _cmd_name(cmd_obj):
    """
    Підтримує обидва формати:
    - { "cmd": "switch_wave", ... }
    - { "action": "switch_variant", ... }
    """
    if "cmd" in cmd_obj:
        return cmd_obj["cmd"]
    if "action" in cmd_obj:
        # мапа з нових назв (із твоєї схеми) на внутрішні
        mapping = {
            "switch_variant": "switch_wave",
            "aggregate_metrics": "aggregate_metrics",
            "publish_release": "make_release",
            "generate_report": "status",     # умовно — виводимо статус
            "sync_manifest": "status",       # умовно
            "validate_schema": "status",     # умовно
            "emit_event": "emit_event"
        }
        return mapping.get(cmd_obj["action"], cmd_obj["action"])
    return None

def handle_cmd(cmd):
    name = _cmd_name(cmd)
    args = cmd.get("args") or {}
    exp = args.get("exp_path") or DEFAULT_EXP

    if name == "emit_event":
        ev = args.get("event") or {}
        ev.setdefault("ts_utc", utcnow())
        ev.setdefault("schema_ver","v1")
        validate(EVENT_SCHEMA, ev)
        return handle_event(ev)

    if name in ("switch_wave","switch_variant"):
        var=args.get("variant"); price=args.get("price")
        assert var in ("A","B") and isinstance(price,(int,float))
        sh("python3","tools/exp_next_wave.py","--exp",exp,"--variant",var,"--price",str(price))
        # згенерувати системну подію
        ev={"ts_utc":utcnow(),"type":"wave_switched","variant":var,"exp_path":exp,"schema_ver":"v1"}
        append_jsonl(BUS_EVENTS, ev)
        return handle_event(ev)

    if name == "aggregate_metrics":
        return sh("python3","tools/metrics_aggregate.py",exp)

    if name in ("make_release","publish_release"):
        return sh("scripts/exp_release.sh",exp)

    if name in ("status","generate_report","sync_manifest","validate_schema"):
        return sh("scripts/exp_status.sh",exp)

    return f"unknown cmd/action: {name}"

def process_once():
    out=[]
    # Спочатку команди
    cmds = read_jsonl(BUS_CMDS)
    if cmds:
        open(BUS_CMDS,"w",encoding="utf-8").write("")
    for c in cmds:
        try:
            validate(CMD_SCHEMA_OLD, c)   # валідатор мʼякий, пропустить обидві форми
            out.append(handle_cmd(c))
        except Exception as e:
            out.append(f"[CMD ERROR] {e}")

    # Потім події
    evs = read_jsonl(BUS_EVENTS)
    if evs:
        open(BUS_EVENTS,"w",encoding="utf-8").write("")
    for ev in evs:
        try:
            validate(EVENT_SCHEMA, ev)
            out.append(handle_event(ev))
        except Exception as e:
            out.append(f"[EVENT ERROR] {e}")

    return "\n---\n".join(out) if out else "(no work)"

if __name__ == "__main__":
    print(process_once())
