import os, subprocess, time, datetime

LOG = os.path.expanduser("~/Desktop/Марія/artifacts/logs/self_healing.out")
AGENTS = [
    "com.maria.brain",
    "com.maria.reasoner",
    "com.maria.goalengine",
    "com.maria.progress",
    "com.maria.emotions",
    "com.maria.guard"
]

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[heal] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def is_running(label):
    try:
        out = subprocess.check_output(
            ["launchctl", "print", f"gui/{os.getuid()}/{label}"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8", "ignore")
        return "state = running" in out
    except subprocess.CalledProcessError:
        return False

def restart_agent(label):
    try:
        subprocess.run(
            ["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{label}"],
            check=True
        )
        log(f"♻️  Перезапущено агент: {label}")
    except Exception as e:
        log(f"[ERR] Не вдалося перезапустити {label}: {e}")

def healing_loop():
    log("=== Self-Healing Engine start ===")
    while True:
        for label in AGENTS:
            if not is_running(label):
                log(f"[!] {label} неактивний — спроба відновлення...")
                restart_agent(label)
            else:
                log(f"[ok] {label} активний.")
        time.sleep(300)  # кожні 5 хв

if __name__ == "__main__":
    try:
        healing_loop()
    except KeyboardInterrupt:
        log("🩺 Завершення циклу самовідновлення вручну.")
