#!/usr/bin/env python3
import json, random, time, datetime, os

LOG_DIR = os.path.expanduser("~/Desktop/Марія/artifacts/logs")
STRATEGY_FILE = os.path.expanduser("~/Desktop/Марія/artifacts/strategy/strategic_plan.jsonl")
os.makedirs(os.path.dirname(STRATEGY_FILE), exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg: str):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[strategy] {ts} {msg}", flush=True)
    with open(os.path.join(LOG_DIR, "strategic_planner.out"), "a", encoding="utf-8") as f:
        f.write(f"[strategy] {ts} {msg}\n")

# === Основні стратегічні напрямки ===
DOMAINS = [
    "інтелектуальне зростання",
    "самонавчання",
    "зміцнення підагентів",
    "оптимізація емоційного стану",
    "фінансова еволюція",
    "розширення знань",
    "самоаналіз і рефлексія",
]

def generate_strategy():
    goal = random.choice(DOMAINS)
    horizon = random.choice(["1 день", "1 тиждень", "1 місяць"])
    intent = random.choice([
        "посилити цей напрямок",
        "оптимізувати ресурси",
        "створити нову підстратегію",
        "оцінити результати попередніх рішень",
        "запустити підагентів для цієї сфери",
    ])
    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "goal_domain": goal,
        "time_horizon": horizon,
        "intent": intent,
        "confidence": round(random.uniform(0.7, 0.99), 2),
    }

def main():
    log("=== Autonomous Strategy Layer start ===")
    while True:
        plan = generate_strategy()
        log(f"🎯 Стратегічний фокус: {plan['goal_domain']} | Горизонт: {plan['time_horizon']} | Дія: {plan['intent']} ({plan['confidence']*100:.0f}%)")
        with open(STRATEGY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(plan, ensure_ascii=False) + "\n")
        time.sleep(random.randint(180, 300))  # стратегічний цикл 3–5 хвилин

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧭 Завершення стратегічного циклу вручну.")
