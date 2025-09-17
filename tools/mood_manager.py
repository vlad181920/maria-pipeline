#!/usr/bin/env python3
import os, json, argparse, datetime, random

STORE = "artifacts/mood.json"

def nowz():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"

def clamp01(x):
    return max(0.0, min(1.0, float(x)))

def load_mood():
    try:
        with open(STORE, "r", encoding="utf-8") as f:
            m = json.load(f)
            m["valence"] = clamp01(m.get("valence", 0.15))
            m["arousal"] = clamp01(m.get("arousal", 0.6))
            m["focus"]  = clamp01(m.get("focus", 0.7))
            if "updated" not in m: m["updated"] = nowz()
            return m
    except Exception:
        return {"valence": 0.15, "arousal": 0.6, "focus": 0.7, "updated": nowz()}

def save_mood(m):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    m["updated"] = nowz()
    tmp = STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False)
    os.replace(tmp, STORE)
    return m

EVENT_DELTAS = {
    "success":  {"valence": +0.06, "arousal": -0.02, "focus": +0.03},
    "progress": {"valence": +0.03, "arousal": -0.01, "focus": +0.02},
    "failure":  {"valence": -0.08, "arousal": +0.05, "focus": -0.03},
    "blocker":  {"valence": -0.05, "arousal": +0.08, "focus": -0.4/10},
    "deadline": {"valence": +0.00, "arousal": +0.10, "focus": +0.02},
    "routine":  {"valence": -0.01, "arousal": -0.02, "focus": -0.05},
    "novelty":  {"valence": +0.02, "arousal": +0.03, "focus": +0.04},
}

def apply_event(mood, event, weight):
    d = EVENT_DELTAS.get(event)
    if not d: return mood
    mood["valence"] = clamp01(mood["valence"] + d["valence"]*weight)
    mood["arousal"] = clamp01(mood["arousal"] + d["arousal"]*weight)
    mood["focus"]   = clamp01(mood["focus"]  + d["focus"]  *weight)
    return mood

def set_values(mood, valence, arousal, focus):
    if valence is not None: mood["valence"] = clamp01(valence)
    if arousal is not None: mood["arousal"] = clamp01(arousal)
    if focus  is not None:  mood["focus"]   = clamp01(focus)
    return mood

def initiative_factors(m):
    v,a,f = m["valence"], m["arousal"], m["focus"]
    min_per_hour_mult = 0.8 + 0.6*a + 0.2*v
    batch = 1 + int((v+f+a) > 2.1)
    period_secs_mult = max(0.5, 1.2 - 0.4*a)
    return {
        "min_per_hour_mult": round(min_per_hour_mult,3),
        "period_secs_mult": round(period_secs_mult,3),
        "batch": batch
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--get", action="store_true")
    ap.add_argument("--event", choices=sorted(EVENT_DELTAS.keys()))
    ap.add_argument("--weight", type=float, default=1.0)
    ap.add_argument("--valence", type=float)
    ap.add_argument("--arousal", type=float)
    ap.add_argument("--focus", type=float)
    ap.add_argument("--compute-initiative", dest="compute_initiative", action="store_true")
    args = ap.parse_args()

    mood = load_mood()
    changed = False
    if args.event:
        mood = apply_event(mood, args.event, args.weight)
        changed = True
    if any(x is not None for x in (args.valence, args.arousal, args.focus)):
        mood = set_values(mood, args.valence, args.arousal, args.focus)
        changed = True
    if changed:
        mood = save_mood(mood)

    out = {"mood": mood}
    if args.compute_initiative:
        out["initiative_factors"] = initiative_factors(mood)
    print(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    main()
