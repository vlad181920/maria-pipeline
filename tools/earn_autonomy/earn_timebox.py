#!/usr/bin/env python3
import os, sys, json, glob, argparse, datetime as dt

BASE = os.environ.get("MARIA_HOME") or os.getcwd()

def latest_exp_dir():
    paths = sorted(
        glob.glob(os.path.join(BASE, "artifacts/earn/experiments", "*__micro-service-offer-audit-implementation")),
        reverse=True
    )
    return paths[0] if paths else None

def load_json(p, default=None):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {} if default is None else default

def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_ts(s):
    # expected "YYYY-MM-DD HH:MM:SS"
    try:
        return dt.datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def minutes_between(t1, t2):
    return int(round((t2 - t1).total_seconds() / 60.0))

def main():
    ap = argparse.ArgumentParser(description="Timebox checker for probes (platform-agnostic).")
    ap.add_argument("--exp", help="Path to experiment dir", default=None)
    ap.add_argument("--idx", type=int, help="Probe index (1-based) to check only", default=None)
    ap.add_argument("--timebox", type=int, help="Override timebox minutes", default=None)
    ap.add_argument("--dry-run", action="store_true", help="Don't modify files, just print")
    args = ap.parse_args()

    exp = args.exp or latest_exp_dir()
    if not exp or not os.path.isdir(exp):
        print("No experiment dir found.", file=sys.stderr); sys.exit(2)

    res_p = os.path.join(exp, "result.json")
    data = load_json(res_p, default={})
    probes = data.get("probes", [])
    if not probes:
        print("No probes in result.json"); sys.exit(0)

    now = dt.datetime.now()
    changed = False
    reviews = []

    # overall metrics snapshot for heuristic
    m = data.get("metrics", {}) or {}
    leads = int(m.get("leads", 0) or 0)
    convs = int(m.get("conversions", 0) or 0)

    def should_scale():
        return (leads + convs) > 0

    indices = range(1, len(probes)+1)
    if args.idx:
        if 1 <= args.idx <= len(probes):
            indices = [args.idx]
        else:
            print(f"--idx out of range (1..{len(probes)})", file=sys.stderr); sys.exit(2)

    for i in indices:
        pr = probes[i-1]
        name = pr.get("name", f"probe-{i}")
        status = pr.get("status", "planned")
        if status != "doing":
            print(f"[skip] {i}) {name}: status={status}")
            continue

        started = parse_ts(pr.get("started_at","") or "")
        if not started:
            print(f"[warn] {i}) {name}: missing started_at; set doing->review manually if needed")
            continue

        tb = args.timebox or int(pr.get("timebox_min", 90) or 90)
        elapsed = minutes_between(started, now)

        if elapsed >= tb:
            # move to review
            pr["status"] = "review"
            pr["finished_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
            ev = pr.setdefault("events", [])
            ev.append({
                "ts": now.strftime("%Y-%m-%d %H:%M:%S"),
                "event": "timebox_reached",
                "elapsed_min": elapsed,
                "timebox_min": tb
            })

            rec = "scale" if should_scale() else "stop_or_pivot"
            reviews.append({
                "index": i, "name": name, "elapsed_min": elapsed,
                "timebox_min": tb, "recommendation": rec
            })
            changed = True
            print(f"[review] {i}) {name}: elapsed {elapsed} ≥ {tb} → recommendation: {rec}")
        else:
            left = tb - elapsed
            print(f"[remain] {i}) {name}: {elapsed}/{tb} min (left {left})")

    # write review file and notes
    if reviews:
        report_name = f"timebox_review_{now.strftime('%Y%m%d_%H%M%S')}.md"
        report_p = os.path.join(exp, report_name)
        lines = [
            f"# Timebox review — {now.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"Experiment: {os.path.basename(exp)}",
            f"Metrics snapshot: leads={leads} conv={convs}",
            "",
            "## Probes reaching timebox",
        ]
        for r in reviews:
            lines += [
                f"- {r['index']}) **{r['name']}** — elapsed {r['elapsed_min']} min / {r['timebox_min']} min",
                f"  - recommendation: **{r['recommendation']}** (heuristic: conversions_or_leads>0 → scale)",
            ]
        lines += [
            "",
            "Policy: no platform lock-in; decisions remain human/agent final."
        ]
        if not args.dry_run:
            with open(report_p, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

        # attach meta to result.json
        notes = data.setdefault("metrics", {}).setdefault("notes", [])
        notes.append(f"timebox_review file: {report_name}")

    if changed and not args.dry_run:
        save_json(res_p, data)

    # tiny stdout footer
    if reviews:
        print(f"[report] {len(reviews)} probe(s) → review. See: {os.path.join(exp, report_name)}")
    else:
        print("[report] no reviews; timebox not reached.")

if __name__ == "__main__":
    main()
