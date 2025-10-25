import os, json, random, datetime

ROOT = os.path.expanduser("~/Desktop/Марія")
SRC_DIR = os.path.join(ROOT, "src")
AUTOLEARN_DIR = os.path.join(SRC_DIR, "_autolearn")
LOG = os.path.join(ROOT, "artifacts/logs/code_evolution.out")

os.makedirs(AUTOLEARN_DIR, exist_ok=True)

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[evolve] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def pick_target_file():
    files = [f for f in os.listdir(SRC_DIR) if f.endswith(".py") and not f.startswith("_")]
    return random.choice(files) if files else None

def read_code(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def mutate_code(code):
    patterns = [
        "# TODO: optimize thought generation",
        "# TODO: improve emotional model",
        "# TODO: refactor reflection logic",
        "# TODO: add self-evaluation metrics"
    ]
    insertion = random.choice(patterns)
    lines = code.splitlines()
    idx = random.randint(0, len(lines)-1)
    lines.insert(idx, insertion)
    return "\n".join(lines)

def evolve():
    log("=== Code Evolution Engine start ===")
    target = pick_target_file()
    if not target:
        log("[ERR] Немає файлів для еволюції.")
        return

    src_path = os.path.join(SRC_DIR, target)
    code = read_code(src_path)
    mutated = mutate_code(code)

    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(AUTOLEARN_DIR, f"mutated_{target}_{ts}")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(mutated)

    log(f"🔬 Згенеровано оновлену версію: {out_path}")
    log("✅ Еволюційний цикл завершено (у безпечному режимі).")

if __name__ == "__main__":
    try:
        evolve()
    except KeyboardInterrupt:
        log("🧩 Завершення еволюційного циклу вручну.")
