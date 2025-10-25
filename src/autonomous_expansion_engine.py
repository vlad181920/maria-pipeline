import os, json, random, datetime, subprocess

ROOT = os.path.expanduser("~/Desktop/Марія")
AGENTS_DIR = os.path.join(ROOT, "subagents")
LOG = os.path.join(ROOT, "artifacts/logs/expansion.out")

os.makedirs(AGENTS_DIR, exist_ok=True)

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[expand] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

ROLES = [
    "дослідник ринку",
    "аналітик мислення",
    "емоційний спостерігач",
    "тестовий експериментатор",
    "виконавчий асистент"
]

def create_subagent():
    role = random.choice(ROLES)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = f"agent_{ts}_{role.replace(' ', '_')}"
    path = os.path.join(AGENTS_DIR, name)
    os.makedirs(path, exist_ok=True)

    agent_code = f"""# Автогенерований підаґент
import time, datetime, random

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{name}] {{ts}} {{msg}}")

def main():
    log("🧠 Підаґент активовано — роль: {role}")
    while True:
        thought = random.choice([
            "спостерігаю тенденції у системі",
            "аналізую емоційний стан Марії",
            "оцінюю цілі та поведінку",
            "генерую внутрішні гіпотези"
        ])
        log(f"нова дія: {{thought}}")
        time.sleep(random.randint(15, 40))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🌀 Завершення циклу підаґента вручну.")
"""
    with open(os.path.join(path, "agent.py"), "w", encoding="utf-8") as f:
        f.write(agent_code)

    log(f"створено нового підаґента: {name}")
    return name, path

def run_agent(name, path):
    proc = subprocess.Popen(
        ["python3", os.path.join(path, "agent.py")],
        stdout=open(os.path.join(path, "out.log"), "a"),
        stderr=open(os.path.join(path, "err.log"), "a")
    )
    log(f"підаґент {name} запущено (pid={proc.pid})")

def main():
    log("=== Autonomous Expansion Engine start ===")
    name, path = create_subagent()
    run_agent(name, path)
    log(f"✅ Активний підаґент: {name}")

if __name__ == "__main__":
    main()
