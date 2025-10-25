#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autotune_integrator.py — Phase 14.1
Тепер Марія:
1. створює гілку autotune/<timestamp>
2. додає мутований код у src/autotune_candidates/
3. комітить зміни
4. пушить гілку на GitHub
5. створює Pull Request із повідомленням про нову версію
"""

import os, subprocess, time, datetime, shutil, glob, json

ROOT = os.path.expanduser("~/Desktop/Марія")
SRC_DIR = os.path.join(ROOT, "src")
AUTOLEARN_DIR = os.path.join(SRC_DIR, "_autolearn")
CANDIDATES_DIR = os.path.join(SRC_DIR, "autotune_candidates")
LOG = os.path.join(ROOT, "artifacts/logs/autotune.out")

os.makedirs(CANDIDATES_DIR, exist_ok=True)

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[autotune] {ts} {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def find_latest_mutation():
    files = glob.glob(os.path.join(AUTOLEARN_DIR, "mutated_*"))
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def syntax_ok(path):
    try:
        subprocess.check_output(["python3", "-m", "py_compile", path], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        log(f"[ERR] синтаксис не пройшов: {e.output.decode('utf-8','ignore')}")
        return False

def ensure_branch():
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    target_branch = f"autotune/{ts}"
    current = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT).decode().strip()
    if not current.startswith("autotune/"):
        subprocess.check_call(["git", "checkout", "-b", target_branch], cwd=ROOT)
        log(f"створено гілку {target_branch}")
    else:
        target_branch = current
        log(f"вже на гілці {target_branch}")
    return target_branch

def integrate(mut_path):
    base_name = os.path.basename(mut_path)
    no_prefix = base_name.replace("mutated_", "", 1)
    split_idx = no_prefix.rfind("_20")
    orig_guess = no_prefix[:split_idx] if split_idx != -1 else no_prefix
    if not orig_guess.endswith(".py"):
        orig_guess += ".py"
    candidate_path = os.path.join(CANDIDATES_DIR, orig_guess)
    shutil.copyfile(mut_path, candidate_path)
    log(f"скопійовано мутований код у {candidate_path}")
    return candidate_path

def git_commit_and_push(branch, candidate_path):
    rel_path = os.path.relpath(candidate_path, ROOT)
    msg = f"autotune: propose evolved {os.path.basename(candidate_path)}"
    try:
        subprocess.check_call(["git", "add", rel_path], cwd=ROOT)
        subprocess.check_call(["git", "commit", "-m", msg], cwd=ROOT)
        log(f"зроблено commit у {branch}")
        subprocess.check_call(["git", "push", "-u", "origin", branch], cwd=ROOT)
        log(f"пуш гілки {branch} виконано ✅")
    except subprocess.CalledProcessError as e:
        log(f"[ERR] git push fail: {e}")

def create_pull_request(branch, candidate_path):
    try:
        title = f"🤖 Autotune proposal — {os.path.basename(candidate_path)}"
        body = (
            f"**Maria Auto-Evolution** created a new candidate.\n\n"
            f"- File: `{os.path.basename(candidate_path)}`\n"
            f"- Branch: `{branch}`\n"
            f"- Generated: {datetime.datetime.utcnow().isoformat()}Z\n\n"
            f"This PR was automatically created by Maria's evolution subsystem."
        )
        subprocess.check_call([
            "gh", "pr", "create",
            "--fill",
            "--title", title,
            "--body", body
        ], cwd=ROOT)
        log("✅ Pull Request створено успішно")
    except subprocess.CalledProcessError as e:
        log(f"[ERR] створення PR не вдалося: {e}")

def main():
    log("=== Auto-Integration with GitHub start ===")

    mut_path = find_latest_mutation()
    if not mut_path:
        log("нема мутованих кандидатів, стоп")
        return
    log(f"останній кандидат: {mut_path}")

    if not syntax_ok(mut_path):
        log("кандидат не пройшов синтаксис, стоп")
        return
    log("синтаксис OK")

    branch = ensure_branch()
    candidate_path = integrate(mut_path)
    git_commit_and_push(branch, candidate_path)
    create_pull_request(branch, candidate_path)

    log("✅ Auto-Integration завершено — кандидат відправлено на рев’ю")

if __name__ == "__main__":
    main()
