#!/usr/bin/env python3
import os, time, datetime, json, random

LOG = os.path.expanduser("~/Desktop/Марія/cloud_node/logs/cloud_daemon.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a") as f:
        f.write(f"[cloud] {ts} {msg}\n")
    print(f"[cloud] {ts} {msg}")

def main():
    log("=== Maria Cloud Node daemon start ===")
    while True:
        metrics = {"cpu": round(random.uniform(0.1,0.9),2),
                   "mem": round(random.uniform(0.1,0.9),2)}
        log(f"status heartbeat → {json.dumps(metrics)}")
        time.sleep(60)

if __name__ == "__main__":
    main()
