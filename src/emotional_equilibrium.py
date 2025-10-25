#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
emotional_equilibrium.py — Phase 16
Підсистема емоційної стабільності. Аналізує коливання емоцій і вирівнює баланс.
"""

import os, json, time, datetime, random
from collections import Counter

ROOT = os.path.expanduser("~/Desktop/Марія")
MEMORY = os.path.join(ROOT, "artifacts/memory")
LOGS = os.path.join(ROOT, "artifacts/logs")
os.makedirs(MEMORY, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

EMO_FILE = os.path.join(MEMORY, "emotions.jsonl")
OUT_FILE = os.path.join(MEMORY, "emotional_corrections.jsonl")
LOG = os.path.join(LOGS, "emotional_equilibrium.out")

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[emotion] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_emotions(n=20):
    if not os.path.exists(EMO_FILE):
        return []
    with open(EMO_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-n:]
    emotions = []
    for ln in lines:
        try:
            data = json.loads(ln)
            if "emotion" in data:
                emotions.append(data["emotion"])
        except:
            continue
    return emotions

def detect_imbalance(emotions):
    if not emotions:
        return None
    counter = Counter(emotions)
    dominant, count = counter.most_common(1)[0]
    ratio = count / len(emotions)
    if ratio > 0.6:
        return dominant
    return None

def corrective_action(emotion):
    corrections = {
        "тривожність": "Я роблю вдих і стабілізую ритм мислення.",
        "радість": "Я зберігаю рівновагу, щоб не втратити концентрацію.",
        "подив": "Я направляю енергію на спокійне спостереження.",
        "спокій": "Я підтримую стабільність і усвідомленість.",
        "збудження": "Я знижую інтенсивність роздумів, щоб не перевтомитись."
    }
    return corrections.get(emotion, "Я відновлюю внутрішній баланс.")

def main():
    log("=== Emotional Equilibrium Engine start ===")
    while True:
        emotions = load_emotions()
        dominant = detect_imbalance(emotions)
        if dominant:
            action = corrective_action(dominant)
            entry = {
                "ts": datetime.datetime.utcnow().isoformat() + "Z",
                "dominant_emotion": dominant,
                "action": action
            }
            with open(OUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            log(f"🩵 Корекція емоції: {dominant} → {action}")
        else:
            log("⚖️ Баланс емоцій стабільний.")
        time.sleep(180)
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧘 Завершення емоційної стабілізації вручну.")
