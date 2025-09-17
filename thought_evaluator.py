import os, json, time
from datetime import datetime

METRICS_DIR = "artifacts/metrics"
THOUGHT_LOG = os.path.join(METRICS_DIR, "thoughts.jsonl")

def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def evaluate_thought(thought: dict) -> dict:
    impact = float(thought.get("impact", 0.0))
    effort = float(thought.get("effort", 1.0)) or 1.0
    risk = float(thought.get("risk", 0.0))
    novelty = float(thought.get("novelty", 0.0))
    score = (impact * 0.5 + novelty * 0.3) - (effort * 0.1 + risk * 0.1)
    return {
        "score": round(score, 4),
        "recommended": score >= 0.25
    }

def log_evaluation(thought: dict, eval_res: dict) -> None:
    _ensure_dir(METRICS_DIR)
    rec = {
        "ts": _now(),
        "thought": thought,
        "evaluation": eval_res
    }
    with open(THOUGHT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def evaluate_and_log(thought: dict) -> dict:
    res = evaluate_thought(thought)
    log_evaluation(thought, res)
    return res

if __name__ == "__main__":
    sample = {
        "id": "t-" + str(int(time.time())),
        "topic": "Продовжити розробку внутрішнього монологу",
        "impact": 0.9,
        "effort": 0.6,
        "risk": 0.1,
        "novelty": 0.7
    }
    out = evaluate_and_log(sample)
    print(json.dumps(out, ensure_ascii=False, indent=2))
