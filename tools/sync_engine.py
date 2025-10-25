#!/usr/bin/env python3
import os, time, subprocess, datetime

ROOT = os.path.expanduser("~/Desktop/Марія")
LOG = os.path.join(ROOT, "artifacts/logs/sync_engine.out")

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a") as f:
        f.write(f"[sync] {ts} {msg}\n")
    print(f"[sync] {ts} {msg}")

def run(cmd):
    result = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    if result.stdout.strip():
        log(result.stdout.strip())
    if result.stderr.strip():
        log("[ERR] " + result.stderr.strip())
    return result.returncode == 0

def main():
    log("=== Global Sync Engine start ===")
    while True:
        # Перевіряємо, чи є зміни локально
        run("git add -A")
        run("git diff --cached --quiet || git commit -m 'auto(sync): mirror local state'")
        run("git pull --rebase origin main || true")
        run("git push origin main || true")
        log("✅ Синхронізація завершена, очікування 15 хвилин...")
        time.sleep(900)  # 15 хвилин

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🧭 Завершення циклу синхронізації вручну.")
