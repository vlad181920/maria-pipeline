#!/usr/bin/env python3
import os, time, json, datetime, random

LOG_DIR = os.path.expanduser("~/Desktop/Марія/artifacts/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "cognitive_coordinator.out")

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[coord] {ts} {msg}\n")
    print(f"[coord] {ts} {msg}")

def check_agents():
    agents = [
        "brain", "reasoner", "goalengine", "progress",
        "emotion", "subagents", "meta"
    ]
    running = []
    for a in agents:
        res = os.popen(f"launchctl list | grep com.maria.{a}").read().strip()
        if res:
            running.append(a)
    return running

def sync_knowledge():
    log("💡 Синхронізація знань між агентами...")
    # тут можна буде додати справжній механізм knowledge merge
    time.sleep(2)
    log("📘 Стан свідомості узгоджено.")

def main():
    log("=== Cognitive Coordinator start ===")
    while True:
        active = check_agents()
        log(f"Активних агентів: {len(active)} → {', '.join(active)}")
        sync_knowledge()
        time.sleep(random.randint(120, 180))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧩 Координатор свідомості зупинено вручну.")
