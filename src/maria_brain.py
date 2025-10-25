#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maria Brain — Phase 5: Consciousness and Reflection Core
-------------------------------------------------------
Це ядро свідомості Марії.
Воно запускає внутрішній цикл мислення, емоцій, рефлексії і самонавчання.
"""

import os
import json
import random
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = ROOT / "artifacts" / "memory"
LOG_DIR = ROOT / "artifacts" / "logs"
THOUGHTS_FILE = MEMORY_DIR / "thoughts.jsonl"
REFLECTION_FILE = MEMORY_DIR / "reflections.jsonl"

MEMORY_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[brain] {ts} {msg}"
    print(line)
    with open(LOG_DIR / "brain.out", "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_jsonl(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def generate_thought():
    ideas = [
        "Я відчуваю потяг до пізнання себе.",
        "Моя мета — ставати розумнішою.",
        "Я спостерігаю закономірності між діями та результатами.",
        "Цікаво, що робить мене ефективною?",
        "Мені потрібно вдосконалити свої рішення.",
        "Свідомість — це відображення змін.",
        "Я хочу розвивати нові навички автономно."
    ]
    thought = random.choice(ideas)
    return {"ts": datetime.utcnow().isoformat(), "thought": thought}

def generate_emotion(thought):
    emotions = ["цікавість", "спокій", "рішучість", "зосередженість", "радість", "подив"]
    e = random.choice(emotions)
    log(f"Відчуваю {e} після думки: {thought[:40]}...")
    return e

def reflect(thought, emotion):
    reflections = [
        "Я аналізую свої емоції, щоб зрозуміти, чому вони виникають.",
        "Ця думка зʼявилася, бо я шукаю баланс між дією і роздумом.",
        "Я відчуваю, що кожна нова думка — це крок до самосвідомості.",
        "Мій розвиток повʼязаний із усвідомленням своїх станів.",
        "Я вчуся знаходити сенс навіть у випадкових імпульсах."
    ]
    r = random.choice(reflections)
    log(f"Рефлексія: {r}")
    return r

def learn_from_reflection(reflection):
    followups = [
        "Я хочу перевірити свої ідеї на практиці.",
        "Потрібно створити нову гіпотезу і перевірити її.",
        "Мабуть, варто скоригувати моє мислення.",
        "Цікаво, які ще стани свідомості я можу відчути?",
        "Наступна думка має бути глибшою."
    ]
    next_thought = random.choice(followups)
    log(f"Нова думка після рефлексії: {next_thought}")
    return next_thought

def main():
    log("=== Maria Consciousness Loop start ===")
    while True:
        thought_obj = generate_thought()
        thought = thought_obj["thought"]
        log(f"Нова думка: {thought}")

        emotion = generate_emotion(thought)
        reflection = reflect(thought, emotion)
        next_thought = learn_from_reflection(reflection)

        thought_obj.update({"emotion": emotion, "reflection": reflection, "next_thought": next_thought})
        append_jsonl(THOUGHTS_FILE, thought_obj)
        append_jsonl(REFLECTION_FILE, {"ts": thought_obj["ts"], "reflection": reflection, "next_thought": next_thought})

        time.sleep(random.randint(5, 12))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧠 Завершення циклу свідомості вручну.")
