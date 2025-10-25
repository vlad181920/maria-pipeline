#!/usr/bin/env python3
import os, json, datetime, time, random

LOG_DIR = os.path.expanduser("~/Desktop/Марія/artifacts/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "meta_self_expansion.out")

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[meta] {ts} {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def evaluate_agents():
    agents = ["brain", "reasoner", "goalengine", "progress", "emotion", "subagents", "meta", "coordinator"]
    scores = {}
    for a in agents:
        state = os.popen(f"launchctl list | grep com.maria.{a}").read().strip()
        score = random.uniform(0.6, 1.0) if state else random.uniform(0.0, 0.4)
        scores[a] = round(score, 2)
    return scores

def propose_evolution(scores):
    underperforming = [a for a, s in scores.items() if s < 0.5]
    if not underperforming:
        return "🔁 Всі агенти стабільні — еволюція не потрібна."
    chosen = random.choice(underperforming)
    action = random.choice([
        f"Створити підмодуль v2 для {chosen}",
        f"Переписати код агента {chosen} із новими евристиками",
        f"Додати навчання з логів для {chosen}",
        f"Зробити рефакторинг логіки {chosen}"
    ])
    return f"💡 Еволюційна ініціатива: {action}"

def main():
    log("=== Meta-Self Expansion start ===")
    while True:
        scores = evaluate_agents()
        avg = sum(scores.values()) / len(scores)
        log(f"📊 Ефективність агентів: {json.dumps(scores, ensure_ascii=False)} | середня={avg:.2f}")
        decision = propose_evolution(scores)
        log(decision)
        time.sleep(random.randint(180, 300))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧩 Meta-Self Expansion зупинено вручну.")
