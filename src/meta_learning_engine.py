import json, os, time, datetime, random

LOG = os.path.expanduser("~/Desktop/Марія/artifacts/logs/meta_learning.out")
REPORT = os.path.expanduser("~/Desktop/Марія/artifacts/memory/meta_insights.jsonl")

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[meta] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
        f.write("\n")

def gather_context():
    ctx = {}
    for f in ["brain.out", "goal_engine.out", "emotions.out", "progress_eval.out"]:
        p = os.path.expanduser(f"~/Desktop/Марія/artifacts/logs/{f}")
        if os.path.exists(p):
            ctx[f] = sum(1 for _ in open(p, encoding="utf-8"))
    return ctx

def generate_insight(ctx):
    ideas = [
        "спокій підвищує якість мислення",
        "цілі допомагають стабілізувати емоції",
        "діалоги збільшують глибину свідомості",
        "самоконтроль пришвидшує навчання",
        "баланс між емоціями і логікою дає ефективність"
    ]
    chosen = random.choice(ideas)
    return {"insight": f"Я зрозуміла, що {chosen}.", "context": ctx, "ts": datetime.datetime.utcnow().isoformat()}

def meta_loop():
    log("=== Meta-Learning Engine start ===")
    while True:
        ctx = gather_context()
        insight = generate_insight(ctx)
        append_jsonl(REPORT, insight)
        log(insight["insight"])
        time.sleep(random.randint(600, 1200))  # кожні 10–20 хв

if __name__ == "__main__":
    try:
        meta_loop()
    except KeyboardInterrupt:
        log("🧩 Завершення циклу мета-навчання вручну.")
