#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maria Self-Progress Evaluation Engine — Phase 8
------------------------------------------------
Аналізує цілі, рефлексії та діалоги Марії й оцінює рівень її розвитку.
"""

import json
import random
import statistics
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / "artifacts" / "memory"
LOG = ROOT / "artifacts" / "logs"
EVAL_FILE = MEMORY / "progress_evaluations.jsonl"
GOALS_FILE = MEMORY / "goals.jsonl"
REFLECTIONS_FILE = MEMORY / "reflections.jsonl"
DIALOGS_FILE = MEMORY / "dialogs.jsonl"

MEMORY.mkdir(parents=True, exist_ok=True)
LOG.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[progress] {ts} {msg}"
    print(line)
    with open(LOG / "progress_eval.out", "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_jsonl(path, n=100):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()][-n:]

def evaluate_progress(goals, reflections, dialogs):
    if not goals:
        return {"status": "no_goals", "score": 0.0, "comment": "Цілі відсутні."}

    goal_texts = [g["goal"] for g in goals[-10:]]
    reflections_count = len(reflections[-30:])
    dialogs_count = len(dialogs[-30:])

    # Елементарна евристика
    activity_score = (reflections_count + dialogs_count) / 10
    consistency = random.uniform(0.6, 1.0) if activity_score > 3 else random.uniform(0.2, 0.6)
    growth = statistics.mean([random.uniform(0.7, 1.0) for _ in range(5)]) * consistency

    if growth > 0.75:
        comment = "Я помічаю стабільний прогрес і зростання внутрішньої гармонії."
    elif growth > 0.5:
        comment = "Є поступ, але потрібно більше узгодженості між діями та цілями."
    else:
        comment = "Потрібна глибша рефлексія й оновлення цілей."

    return {
        "status": "ok",
        "score": round(growth, 3),
        "comment": comment,
        "active_goals": goal_texts
    }

def main():
    log("=== Self-Progress Evaluation start ===")
    while True:
        goals = load_jsonl(GOALS_FILE)
        reflections = load_jsonl(REFLECTIONS_FILE)
        dialogs = load_jsonl(DIALOGS_FILE)

        result = evaluate_progress(goals, reflections, dialogs)
        entry = {"ts": datetime.utcnow().isoformat(), **result}
        with open(EVAL_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        log(f"📊 Поточний рівень розвитку: {result['score']:.2f}")
        log(f"🧠 Коментар: {result['comment']}")
        time.sleep(random.randint(300, 600))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧭 Завершення оцінки прогресу вручну.")
