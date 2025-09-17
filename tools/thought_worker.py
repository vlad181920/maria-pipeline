#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, time, shutil, datetime
MARIA_HOME = os.environ.get("MARIA_HOME", os.path.expanduser("~/Desktop/Марія"))
THOUGHTS_DIR = os.path.join(MARIA_HOME, "artifacts", "thoughts")
QUEUE_FILE   = os.path.join(THOUGHTS_DIR, "queue.jsonl")
PROC_FILE    = os.path.join(THOUGHTS_DIR, "processed.jsonl")
ARCH_FILE    = os.path.join(THOUGHTS_DIR, "archive.jsonl")
INSIGHTS_DIR = os.path.join(MARIA_HOME, "artifacts", "insights")
QA_DIR       = os.path.join(MARIA_HOME, "artifacts", "qa")
LOG_FILE     = os.path.join(MARIA_HOME, "artifacts", "logs", "thought_worker.log")
os.makedirs(THOUGHTS_DIR, exist_ok=True)
os.makedirs(INSIGHTS_DIR, exist_ok=True)
os.makedirs(QA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
VALID_TYPES = {"next_action","insight","hypothesis"}
def ts(): return datetime.datetime.now().isoformat(timespec="seconds")
def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts()}] {msg}\n")
def read_jsonl(path):
    items = []
    if not os.path.exists(path): return items
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try: items.append(json.loads(line))
            except: pass
    return items
def write_jsonl_append(path, rec):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
def write_jsonl_all(path, items):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    shutil.move(tmp, path)
def process_one(th):
    t = th.get("type")
    topic = th.get("topic","")
    now = ts()
    if t == "next_action":
        outcome = {"status":"done", "note":"створено план наступних уточнень"}
        qa_file = os.path.join(QA_DIR, "qa_todos.jsonl")
        q1 = {"ts": now, "type":"question","origin":"next_action","text":f"Які саме деталі потрібні щодо: {topic[:140]}?"}
        q2 = {"ts": now, "type":"question","origin":"next_action","text":f"Який наступний мінімальний крок для теми: {topic[:140]}?"}
        write_jsonl_append(qa_file, q1)
        write_jsonl_append(qa_file, q2)
    elif t == "insight":
        outcome = {"status":"logged", "note":"зафіксовано інсайт для покращення"}
    elif t == "hypothesis":
        outcome = {"status":"queued_test", "note":"додано до списку гіпотез для перевірки"}
    else:
        outcome = {"status":"skipped", "note":"невідомий тип"}
    th2 = dict(th)
    th2["state"] = outcome["status"]
    th2["processed_at"] = now
    th2["outcome"] = outcome
    return th2
def main(sleep_s=0.2, health_every_sec=30):
    import time
    last_health = 0.0
    while True:
        try:
            q = read_jsonl(QUEUE_FILE)
            if not q:
                now = time.time()
                if now - last_health >= health_every_sec:
                    log("[health] alive")
                    last_health = now
                time.sleep(sleep_s)
                continue

            thoughts = [it for it in q if it.get("type") in VALID_TYPES]
            others  = [it for it in q if it.get("type") not in VALID_TYPES]

            take = thoughts[:10]
            rest_thoughts = thoughts[10:]

            processed = []
            for th in take:
                try:
                    th2 = process_one(th)
                    processed.append(th2)
                    log(f"processed {th2.get('id','(no-id)')} -> {th2.get('state')}")
                except Exception as e:
                    log(f"error processing {th.get('id','(no-id)')}: {e}")

            for it in others:
                it2 = dict(it)
                it2["archived_at"] = ts()
                it2["archived_reason"] = "not-a-thought"
                write_jsonl_append(ARCH_FILE, it2)
                log(f"archived non-thought {it2.get('id','(no-id)')} type={it2.get('type')}")

            write_jsonl_all(QUEUE_FILE, rest_thoughts)
            for th2 in processed:
                write_jsonl_append(PROC_FILE, th2)

            now = time.time()
            if now - last_health >= health_every_sec:
                log("[health] alive")
                last_health = now
            time.sleep(sleep_s)
        except Exception as e:
            # ловимо будь-що, щоб не впасти з exit 1
            try:
                log(f"[fatal-iteration] {e}")
            except Exception:
                pass
            time.sleep(1.0)

if __name__ == "__main__":
    main()
