import os, sys, json, time, re

ALLOWED_TOP = {"ts_utc","action","args","initiator","schema_ver"}
ALLOWED_ACTIONS = {
    "aggregate_metrics",
    "publish_release",
    "switch_variant",
    "generate_report",
    "sync_manifest",
    "validate_schema",
}
CMD_TO_ACTION = {
    "switch_wave": "switch_variant",
    "switch_variant": "switch_variant",
    "aggregate_metrics": "aggregate_metrics",
    "publish_release": "publish_release",
    "generate_report": "generate_report",
    "sync_manifest": "sync_manifest",
    "validate_schema": "validate_schema",
}
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
VARIANTS = {"A","B"}

def normalize_one(s, bad_sink):
    # parse
    try:
        obj = json.loads(s)
    except Exception:
        bad_sink.write(s + "\n")
        return None, "parse_error"

    o = dict(obj)  # copy

    # move cmd -> action if needed
    if "action" not in o and "cmd" in o:
        mapped = CMD_TO_ACTION.get(str(o["cmd"]))
        if mapped:
            o["action"] = mapped
        o.pop("cmd", None)

    # validate action
    action = o.get("action")
    if action not in ALLOWED_ACTIONS:
        bad_sink.write(s + "\n")
        return None, "bad_action"

    # ts_utc sanity
    ts = o.get("ts_utc")
    if not isinstance(ts, str) or not TS_RE.match(ts or ""):
        bad_sink.write(s + "\n")
        return None, "bad_ts"

    # schema_ver
    if not isinstance(o.get("schema_ver"), str):
        o["schema_ver"] = "v1"

    # args must be object
    args = o.get("args")
    if args is None or not isinstance(args, dict):
        args = {}
    # light normalization for switch_variant
    if action == "switch_variant":
        # exp_path string
        ep = args.get("exp_path")
        if ep is not None and not isinstance(ep, str):
            args.pop("exp_path", None)
        # variant A/B
        v = args.get("variant")
        if v is not None:
            v = str(v).upper()
            if v in VARIANTS:
                args["variant"] = v
            else:
                args.pop("variant", None)
        # price number >=0
        p = args.get("price")
        if p is not None:
            try:
                p = float(p)
                if p < 0: p = 0.0
                args["price"] = p
            except Exception:
                args.pop("price", None)
    o["args"] = args

    # drop unknown top-level keys
    for k in list(o.keys()):
        if k not in ALLOWED_TOP:
            o.pop(k, None)

    return o, None

def main():
    bus_dir = "bus"
    path = os.path.join(bus_dir, "commands.jsonl")
    if not os.path.isfile(path):
        print(f"No commands.jsonl at {path}", file=sys.stderr)
        print(path)
        return 0

    ts = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    bak = path + f".bak_{ts}"
    bad = path + f".bad_{ts}"
    tmp = path + ".tmp"

    kept=fixed=skipped=0

    with open(path, encoding="utf-8") as fin, \
         open(tmp, "w", encoding="utf-8") as fout, \
         open(bad, "w", encoding="utf-8") as fbad:
        for line in fin:
            s=line.strip()
            if not s:
                continue
            norm, err = normalize_one(s, fbad)
            if norm is None:
                skipped += 1
                continue
            # decide fixed vs kept
            try:
                if json.loads(s) == norm:
                    kept += 1
                else:
                    fixed += 1
            except Exception:
                fixed += 1
            fout.write(json.dumps(norm, ensure_ascii=False)+"\n")

    os.replace(path, bak)
    os.replace(tmp, path)

    print(json.dumps({
        "ok": True,
        "path": path,
        "backup": bak,
        "bad_lines": skipped,
        "fixed_lines": fixed,
        "kept_lines": kept
    }, ensure_ascii=False))
    print(path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
