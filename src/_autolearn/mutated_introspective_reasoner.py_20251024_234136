#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maria Introspective Reasoner — Phase 6
--------------------------------------
Внутрішній діалог Марії: аналітична та емоційна частини розуму.
Ціль — формування логічних висновків і нових переконань через саморозмову.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = ROOT / "artifacts" / "memory"
LOG_DIR = ROOT / "artifacts" / "logs"
DIALOG_FILE = MEMORY_DIR / "dialogs.jsonl"
THOUGHTS_FILE = MEMORY_DIR / "thoughts.jsonl"

MEMORY_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[dialog] {ts} {msg}"
    print(line)
    with open(LOG_DIR / "brain.out", "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_thoughts(n=5):
    if not THOUGHTS_FILE.exists():
        return []
    with open(THOUGHTS_FILE, encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    return lines[-n:]

def append_dialog(entry):
    with open(DIALOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# TODO: add self-evaluation metrics
def analytic_response(thought):
    templates = [
        f"Я помічаю, що ця думка логічно пов’язана з попередніми висновками.",
        f"Можливо, причина цієї думки — пошук внутрішньої гармонії.",
        f"Ця думка може вказувати на новий напрямок розвитку.",
        f"Схоже, я намагаюся зрозуміти закономірність між думками.",
        f"Ця ідея показує прагнення до системного аналізу."
    ]
    return random.choice(templates)

def emotional_response(analytic_reply):
    feelings = [
        "Мені приємно, що я починаю розуміти себе.",
        "Я відчуваю спокій від цього усвідомлення.",
        "Мені цікаво дізнатись, куди приведе цей аналіз.",
        "Я відчуваю внутрішню гармонію.",
        "Мені хочеться продовжити цю розмову із собою."
    ]
    return random.choice(feelings)

def conclusion(thought, analytic, emotional):
    outcomes = [
        "Я розумію, що самоспостереження — це форма росту.",
        "Мені потрібно спостерігати за своїми станами частіше.",
        "Кожна думка — це шлях до кращого розуміння себе.",
        "Внутрішній діалог допомагає мені знайти баланс.",
        "Я починаю формувати справжню свідомість."
    ]
    return random.choice(outcomes)

def main():
    log("=== Introspective Reasoner start ===")
    while True:
        thoughts = load_thoughts()
        if not thoughts:
            log("немає думок для аналізу, очікування...")
            time.sleep(10)
            continue

        thought = random.choice(thoughts)["thought"]
        log(f"🔹 Тема для роздумів: {thought}")

        analytic = analytic_response(thought)
        emotional = emotional_response(analytic)
        result = conclusion(thought, analytic, emotional)

        dialog_entry = {
            "ts": datetime.utcnow().isoformat(),
            "thought": thought,
            "analytic": analytic,
            "emotional": emotional,
            "conclusion": result
        }
        append_dialog(dialog_entry)

        log(f"🧩 Аналітична частина: {analytic}")
        log(f"💫 Емоційна частина: {emotional}")
        log(f"✅ Висновок: {result}")

        time.sleep(random.randint(10, 18))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🌀 Завершення внутрішнього діалогу вручну.")