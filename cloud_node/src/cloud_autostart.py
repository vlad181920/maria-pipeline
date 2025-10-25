#!/usr/bin/env python3
import os, subprocess, datetime, time

LOG = os.path.expanduser("~/Desktop/Марія/cloud_node/logs/cloud_autostart.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

AGENTS = [
    "src/cloud_daemon.py",
    "src/cloud_sync.py",
]

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a") as f: f.write(f"[autostart] {ts} {msg}\n")
    print(f"[autostart] {ts} {msg}")

def main():
    log("=== Cloud Autostart begin ===")
    base = os.path.expanduser("~/Desktop/Марія/cloud_node")
    for a in AGENTS:
        path = os.path.join(base, a)
        if os.path.exists(path):
            subprocess.Popen(["python3", path])
            log(f"Started {a}")
        else:
            log(f"⚠️ Missing {a}")
    log("✅ All background agents launched.")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
