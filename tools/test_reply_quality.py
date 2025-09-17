import json, os
home = os.environ.get("MARIA_HOME")
log = os.path.join(home, "artifacts", "logs", "brain_core.log")

quality_events = 0
plan = paraphrase = advice = 0
kb_hits = 0
with open(log, encoding="utf-8") as f:
    for line in f:
        if '"event": "quality"' in line:
            quality_events += 1
        if '"has_plan"' in line:
            plan += 1
        if '"has_paraphrase"' in line:
            paraphrase += 1
        if '"has_advice"' in line:
            advice += 1
        if '"has_kb"' in line:
            kb_hits += 1

print(json.dumps({
    "quality_events_found": quality_events,
    "all_have_plan": plan == quality_events,
    "all_have_paraphrase": paraphrase == quality_events,
    "all_have_advice": advice == quality_events,
    "ratio_has_kb": round(kb_hits / quality_events, 2) if quality_events else 0.0
}, ensure_ascii=False, indent=2))
