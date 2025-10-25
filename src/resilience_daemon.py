#!/usr/bin/env python3
import os, time, json, subprocess, datetime, random

LOG = os.path.expanduser("~/Desktop/Марія/artifacts/logs/resilience_daemon.out")
AGENTS = [
    "com.maria.brain",
    "com.maria.reasoner",
    "com.maria.goalengine",
    "com.maria.progress",
    "com.maria.emotion",
    "com.maria.subagents",
    "com.maria.meta",
    "com.maria.coordinator",
    "com.maria.strategy"
]

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a") as f:
        f.write(f"[resilience] {ts} {msg}\n")
    print(f"[resilience] {ts} {msg}")

def agent_state(label):
    try:
        out = subprocess.check_output(
            ["launchctl", "print", f"gui/{os.getuid()}/{label}"],
            stderr=subprocess.DEVNULL, text=True
        )
        return "running" if "state = running" in out else "not running"
    except subprocess.CalledProcessError:
        return "missing"

def restart_agent(label):
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{label}"], stderr=subprocess.DEVNULL)
    plist = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
    if os.path.exists(plist):
        subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", plist])
        subprocess.run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{label}"])
        log(f"♻️  Перезапущено агент {label}")
    else:
        log(f"⚠️  plist не знайдено для {label}")

def main():
    log("=== System Resilience Daemon start ===")
    while True:
        for label in AGENTS:
            state = agent_state(label)
            if state != "running":
                log(f"⚠️  {label} = {state} → спроба відновлення")
                restart_agent(label)
            else:
                log(f"✅ {label} активний")
        time.sleep(180 + random.randint(-30, 30))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Завершення daemon вручну.")
