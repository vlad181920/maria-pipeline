import json, random, time, os, datetime

LOG = os.path.expanduser("~/Desktop/Марія/artifacts/logs/emotions.out")
STATE = os.path.expanduser("~/Desktop/Марія/artifacts/memory/emotional_state.json")

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[emotion] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_state():
    if os.path.exists(STATE):
        with open(STATE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"balance": 0.5, "last_emotion": "спокій"}

def save_state(state):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def evaluate_emotion():
    emotions = ["спокій", "радість", "подив", "напруга", "впевненість", "смуток"]
    mood = random.choice(emotions)
    drift = random.uniform(-0.15, 0.15)
    return mood, drift

def equilibrium_loop():
    log("=== Emotional Equilibrium Engine start ===")
    state = load_state()

    while True:
        mood, drift = evaluate_emotion()
        state["balance"] = max(0.0, min(1.0, state["balance"] + drift))
        state["last_emotion"] = mood

        if state["balance"] > 0.8:
            note = "⚖️  Занадто збуджена — зниження темпу мислення."
        elif state["balance"] < 0.2:
            note = "🌿  Надто пригнічена — підвищення активності."
        else:
            note = "💫  Оптимальний стан гармонії."

        log(f"Емоція: {mood} | Баланс: {state['balance']:.2f} | {note}")
        save_state(state)
        time.sleep(random.randint(60, 120))

if __name__ == "__main__":
    try:
        equilibrium_loop()
    except KeyboardInterrupt:
        log("🧘 Завершення циклу емоційного балансу вручну.")
