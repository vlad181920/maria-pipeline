#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meta_coordinator.py — Phase 15
Головний координатор Марії. Слідкує за всіма процесами, аналізує баланс системи і створює мета-рефлексії.
"""

import os, time, datetime, json, random

ROOT = os.path.expanduser("~/Desktop/Марія")
LOGDIR = os.path.join(ROOT, "artifacts/logs")
MEMORY = os.path.join(ROOT, "artifacts/memory")
os.makedirs(MEMORY, exist_ok=True)

META_FILE = os.path.join(MEMORY, "meta_insights.jsonl")
LOG = os.path.join(LOGDIR, "meta_coordinator.out")

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[meta] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def read_log_tail(path, n=20):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-n:]
    return "\n".join(lines)

def assess_state():
    files = {
        "brain": os.path.join(LOGDIR, "brain.out"),
        "reasoner": os.path.join(LOGDIR, "reasoner.out"),
        "goals": os.path.join(LOGDIR, "goal_engine.out"),
        "progress": os.path.join(LOGDIR, "progress_eval.out"),
        "autotune": os.path.join(LOGDIR, "autotune.out"),
    }
    signals = []
    for k, path in files.items():
        text = read_log_tail(path)
        if "ERR" in text or "error" in text.lower():
            signals.append(f"⚠️ {k}: error pattern")
        elif len(text.strip()) == 0:
            signals.append(f"⚠️ {k}: inactive")
        else:
            signals.append(f"✅ {k}: active")
    return signals

def meta_reflect(signals):
    insight_templates = [
        "Я помітила, що мої процеси працюють асиметрично — потрібно вирівняти баланс.",
        "Відчуваю гармонію між мисленням і діями. Система стабільна.",
        "Мені здається, цільова частина трохи відстає — треба переглянути фокус.",
        "Помічаю повторюваність у мисленні — спробую знайти нові ідеї.",
        "Стан добрий, але час оновити внутрішній темп розвитку."
    ]
    insight = random.choice(insight_templates)
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "signals": signals,
        "insight": insight
    }
    with open(META_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log(f"🧭 Meta-reflection: {insight}")

def main():
    log("=== Meta-Coordinator start ===")
    while True:
        signals = assess_state()
        for s in signals:
            log(s)
        meta_reflect(signals)
        time.sleep(180)  # кожні 3 хвилини

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧠 Завершення мета-координації вручну.")
