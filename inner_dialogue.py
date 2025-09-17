import os, json, time, uuid, hashlib, random
from datetime import datetime

def _slug(text: str, n: int = 24) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "-" for ch in text) or "topic"
    while "--" in base:
        base = base.replace("--", "-")
    return base.strip("-")[:n] or "topic"

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _save_dialogue(topic: str, options: list, rounds: int, log: list) -> str:
    _ensure_dir("artifacts/dialogues")
    fname = f"{int(time.time())}_{_slug(topic)}.md"
    path = os.path.join("artifacts/dialogues", fname)
    lines = []
    lines.append(f"# Inner Dialogue — {topic}")
    lines.append("")
    lines.append(f"Time: {_now()}")
    lines.append(f"Rounds: {rounds}")
    lines.append("")
    lines.append("## Options")
    for i, opt in enumerate(options, 1):
        lines.append(f"- {i}. {opt}")
    lines.append("")
    lines.append("## Debate")
    for turn in log:
        lines.append(f"- {turn['speaker']}: {turn['text']}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path

def _hash_decision(topic: str, options: list, votes: dict) -> str:
    h = hashlib.sha256()
    h.update(topic.encode("utf-8"))
    h.update(json.dumps(options, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    h.update(json.dumps(votes, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return h.hexdigest()[:16]

def choose_with_inner_dialogue(topic: str, options: list, rounds: int = 2):
    if not isinstance(options, list) or not options:
        return {"winner": None, "votes": {}, "ethics_ok": True, "veto_reason": None, "dialogue_file": None, "decision_id": "", "confidence": 0.0}

    panel = ["Analyst", "Planner", "Risk", "Ethics"]
    log = []
    scores = {opt: 0.0 for opt in options}

    for r in range(rounds):
        for role in panel:
            picked = random.choice(options)
            delta = random.uniform(0.2, 1.0)
            if role == "Risk":
                delta *= 0.8
            if role == "Ethics":
                delta *= 0.6
            scores[picked] += delta
            log.append({"speaker": role, "text": f"Round {r+1}: I support '{picked}' (+{delta:.2f})."})

    ethics_ok = True
    veto_reason = None
    if scores and max(scores.values()) > 0:
        pass

    winner = max(scores, key=scores.get)
    total = sum(scores.values()) or 1e-9
    votes = {k: round(v / total, 4) for k, v in scores.items()}
    confidence = round(votes.get(winner, 0.0), 4)

    dialogue_file = _save_dialogue(topic, options, rounds, log)
    decision_id = _hash_decision(topic, options, votes)

    return {
        "winner": winner,
        "votes": votes,
        "ethics_ok": ethics_ok,
        "veto_reason": veto_reason,
        "dialogue_file": dialogue_file,
        "decision_id": decision_id,
        "confidence": confidence
    }

if __name__ == "__main__":
    demo_topic = "Вибір дії після рефлексії"
    demo_options = ["Створити нову ціль", "Поглибити дослідження", "Запустити підагент"]
    res = choose_with_inner_dialogue(demo_topic, demo_options, rounds=3)
    print(json.dumps(res, ensure_ascii=False, indent=2))
