import argparse, json, pathlib, shutil, time

def bump(val_str, cur, as_float=False):
    if val_str is None: return cur
    s = val_str.strip()
    if s.startswith(('+','-')):
        delta = float(s) if as_float else int(s)
        return (float(cur) if as_float else int(cur)) + delta
    # абсолютне значення
    return float(s) if as_float else int(s)

ap = argparse.ArgumentParser()
ap.add_argument("--exp", required=True, help="path to experiment dir")
ap.add_argument("--leads")
ap.add_argument("--conversions")
ap.add_argument("--revenue")      # у $ (float)
ap.add_argument("--time", dest="time_spent_min")
ap.add_argument("--cost")
ap.add_argument("--note")
args = ap.parse_args()

p = pathlib.Path(args.exp)/"result.json"
bk = str(p)+".bak_"+time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(p, bk)

d = json.load(open(p, encoding="utf-8"))
m = d.setdefault("metrics", {})
m["leads"]         = bump(args.leads,         m.get("leads", 0))
m["conversions"]   = bump(args.conversions,   m.get("conversions", 0))
m["revenue_usd"]   = bump(args.revenue,       m.get("revenue_usd", 0.0), as_float=True)
m["time_spent_min"]= bump(args.time_spent_min,m.get("time_spent_min", 0))
m["cost_usd"]      = bump(args.cost,          m.get("cost_usd", 0.0), as_float=True)
if args.note:
    m.setdefault("notes", []).append(args.note)

json.dump(d, open(p,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("updated; backup:", bk)
