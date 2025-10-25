# Автогенерований підаґент
import time, datetime, random

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[agent_20251024_233931_виконавчий_асистент] {ts} {msg}")

def main():
    log("🧠 Підаґент активовано — роль: виконавчий асистент")
    while True:
        thought = random.choice([
            "спостерігаю тенденції у системі",
            "аналізую емоційний стан Марії",
            "оцінюю цілі та поведінку",
            "генерую внутрішні гіпотези"
        ])
        log(f"нова дія: {thought}")
        time.sleep(random.randint(15, 40))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🌀 Завершення циклу підаґента вручну.")
