#!/usr/bin/env python3
import os, subprocess, time, datetime

LOG = os.path.expanduser("~/Desktop/Марія/cloud_node/logs/cloud_sync.log")
REPO_DIR = os.path.expanduser("~/Desktop/Марія")

os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[sync] {ts} {msg}"
    print(line)
    with open(LOG, "a") as f: f.write(line + "\n")

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def main():
    log("=== Cloud Mirror Sync start ===")
    while True:
        os.chdir(REPO_DIR)
        pull = run("git pull origin main")
        log(pull.stdout.strip() or pull.stderr.strip())
        log("✅ Mirror sync complete, sleeping 10 min...")
        time.sleep(600)

if __name__ == "__main__":
    main()
