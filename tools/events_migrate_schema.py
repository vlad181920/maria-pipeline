import os, sys, json, time, re

ALLOWED_KEYS = {
    "ts_utc","type","variant","amount","exp_path","file","dup_key",
    "source","session_id","order_id","meta","schema_ver"
}
VARIANTS = {"A","B"}
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

def main(exp_path):
    events_path = os.path.join(os.path.abspath(exp_path), "events.jsonl")
    if not os.path.isfile(events_path):
        print(f"No events.jsonl at {events_path}", file=sys.stderr)
        print(events_path)  # for consistency with other tools
        return 0

    ts = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    bak_path = events_path + f".bak_{ts}"
    bad_path = events_path + f".bad_{ts}"
    tmp_path = events_path + ".tmp"

    fixed = 0
    kept = 0
    bad = 0

    with open(events_path, encoding="utf-8") as fin, \
         open(tmp_path, "w", encoding="utf-8") as fout, \
         open(bad_path, "w", encoding="utf-8") as fbad:
        for line in fin:
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                bad += 1
                fbad.write(s + "\n")
                continue

            # ensure required fields minimally
            out = {}
            for k in list(obj.keys()):
                if k in ALLOWED_KEYS:
                    out[k] = obj[k]
                # ignore unknown keys to satisfy additionalProperties:false

            # ts_utc sanity (if missing or invalid, skip line into bad)
            ts_utc = out.get("ts_utc")
            if not isinstance(ts_utc, str) or not TS_RE.match(ts_utc or ""):
                bad += 1
                fbad.write(s + "\n")
                continue

            # type sanity (leave as-is; schema will validate the enum later)
            t = out.get("type")
            if not isinstance(t, str):
                bad += 1
                fbad.write(s + "\n")
                continue

            # normalize variant
            if "variant" in out:
                v = str(out.get("variant","")).upper()
                if v in VARIANTS:
                    out["variant"] = v
                else:
                    # drop invalid variant to avoid schema failure
                    out.pop("variant", None)

            # amount non-negative if present
            if "amount" in out:
                try:
                    amt = float(out["amount"])
                    if amt < 0: amt = 0.0
                    out["amount"] = amt
                except Exception:
                    out.pop("amount", None)

            # ensure schema_ver
            if "schema_ver" not in out or not isinstance(out["schema_ver"], str):
                out["schema_ver"] = "v1"

            # meta must be object if present
            if "meta" in out and not isinstance(out["meta"], dict):
                out.pop("meta", None)

            # success line
            fout.write(json.dumps(out, ensure_ascii=False) + "\n")
            if out.keys() == obj.keys():
                kept += 1
            else:
                fixed += 1

    # rotate files
    os.replace(events_path, bak_path)
    os.replace(tmp_path, events_path)

    # print short summary to stdout
    print(json.dumps({
        "ok": True,
        "path": events_path,
        "backup": bak_path,
        "bad_lines": bad,
        "fixed_lines": fixed,
        "kept_lines": kept
    }, ensure_ascii=False))
    # and echo for shell pipelines
    print(events_path)
    return 0

if __name__ == "__main__":
    exp = os.environ.get("EXP") or (sys.argv[1] if len(sys.argv)>1 else "")
    if not exp:
        print(json.dumps({"ok": False, "error": "no EXP"}, ensure_ascii=False))
        sys.exit(1)
    sys.exit(main(exp))
