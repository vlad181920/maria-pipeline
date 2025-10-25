#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
subagent_manager.py — Phase 17
Створення, моніторинг і координація автономних підагентів.
"""

import os, json, subprocess, datetime, random, string, time

ROOT = os.path.expanduser("~/Desktop/Марія")
AGENTS_DIR = os.path.join(ROOT, "artifacts/agents")
LOGS = os.path.join(ROOT, "artifacts/logs")
BUS = os.path.join(ROOT, "bus")
os.makedirs(AGENTS_DIR, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)
os.makedirs(BUS, exist_ok=True)

LOG = os.path.join(LOGS, "subagent_manager.out")
EVENTS = os.path.join(BUS, "agents.jsonl")

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[subagent] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def gen_id(n=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def create_subagent(goal:str):
    agent_id = f"a_{gen_id()}"
    agent_dir = os.path.join(AGENTS_DIR, agent_id)
    os.makedirs(agent_dir, exist_ok=True)

    script_path = os.path.join(agent_dir, f"{agent_id}.py")
    memory_path = os.path.join(agent_dir, "memory.jsonl")

    code = f'''#!/usr/bin/env python3
import json, datetime, random, time, os
agent_id = "{agent_id}"
goal = "{goal}"
mem = "{memory_path}"

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{{agent_id}}] {{ts}} {{msg}}", flush=True)

def save(thought, result):
    entry = {{
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "thought": thought,
        "result": result
    }}
    with open(mem, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False)+"\\n")

log(f"start — goal: {{goal}}")
for i in range(random.randint(3,6)):
    thought = random.choice([
        "аналізую дані",
        "генерую ідеї",
        "оцінюю результат",
        "створюю підхід",
        "удосконалююсь"
    ])
    result = random.choice(["успіх","новий інсайт","помилка","висновок"])
    save(thought, result)
    log(f"{{thought}} → {{result}}")
    time.sleep(random.uniform(0.5, 1.2))
log("завершення роботи")
'''
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)
    os.chmod(script_path, 0o755)

    log(f"створено підагент {agent_id} (goal: {goal})")
    subprocess.Popen(["python3", script_path])
    event = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "event": "spawn",
        "agent_id": agent_id,
        "goal": goal,
        "path": script_path
    }
    with open(EVENTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False)+"\n")
    return agent_id

def main():
    log("=== Sub-Agent Manager start ===")
    goals = [
        "знайти нові способи навчання",
        "оптимізувати стратегію заробітку",
        "згенерувати креативний продукт",
        "аналізувати попередні дані",
        "покращити внутрішню ефективність"
    ]
    while True:
        goal = random.choice(goals)
        create_subagent(goal)
        time.sleep(180)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧩 Завершення менеджера підагентів вручну.")
