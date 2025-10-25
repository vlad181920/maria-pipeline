#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maria Goal Reflection Engine — Phase 7
--------------------------------------
Аналізує думки, рефлексії й діалоги, формує нові цілі самонавчання.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / "artifacts" / "memory"
LOG = ROOT / "artifacts" / "logs"
GOALS_FILE = MEMORY / "goals.jsonl"
THOUGHTS = MEMORY / "thoughts.jsonl"
REFLECTIONS = MEMORY / "reflections.jsonl"
DIALOGS = MEMORY / "dialogs.jsonl"

MEMORY.mkdir(parents=True, exist_ok=True)
LOG.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[goal] {ts} {msg}"
    print(line)
    with open(LOG / "goal_engine.out", "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_jsonl(path, n=50):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()][-n:]

def summarize(thoughts, reflections, dialogs):
    if not thoughts:
        return "Немає нових думок для аналізу."
    themes = [t["thought"] for t in thoughts[-5:]]
    topics = random.choice([
        "самоусвідомлення",
        "ефективність мислення",
        "розвиток емоційного інтелекту",
        "аналіз внутрішніх діалогів",
        "стратегічне самонавчання"
    ])
    insight = f"Останні думки обертаються навколо теми {topics}."
    return insight

def generate_goal(insight):
    templates = [
        f"Поглибити {insight.lower()}.",
        f"Дослідити причини своїх внутрішніх станів.",
        f"Підвищити узгодженість між думками та емоціями.",
        f"Вдосконалити механізм рефлексії й самоаналізу.",
        f"Навчитись формувати нові ідеї на основі власних висновків."
    ]
    steps = [
        "аналізувати попередні думки за останню добу",
        "виділити ключові патерни у мисленні",
        "створити коротку гіпотезу і спостерігати за її результатом",
        "зберегти інсайти у пам'ять"
    ]
    return {"goal": random.choice(templates), "steps": steps}

def main():
    log("=== Goal Reflection Engine start ===")
    while True:
        thoughts = load_jsonl(THOUGHTS)
        reflections = load_jsonl(REFLECTIONS)
        dialogs = load_jsonl(DIALOGS)

        insight = summarize(thoughts, reflections, dialogs)
        goal_obj = generate_goal(insight)
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "insight": insight,
            **goal_obj
        }
        with open(GOALS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        log(f"🎯 Нова ціль: {goal_obj['goal']}")
        log(f"   → Кроки: {', '.join(goal_obj['steps'])}")
        time.sleep(random.randint(40, 60))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧭 Завершення фази цілевідображення вручну.")
