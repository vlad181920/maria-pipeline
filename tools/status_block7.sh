#!/bin/zsh
cd "$(dirname "$0")/.."
export MARIA_HOME="$PWD"
python3 - << 'PY'
import json, os, collections
def count(path, key, val=None):
    c=0
    try:
        with open(path,"r",encoding="utf-8") as f:
            for line in f:
                import json as J
                try:
                    j=J.loads(line)
                    if val is None: c+=1
                    else:
                        if j.get(key)==val: c+=1
                except: pass
    except: pass
    return c
G="artifacts/goals/goals.jsonl"; S="artifacts/goals/subgoals.jsonl"; P="artifacts/goals/progress.jsonl"
print("goals_total:", count(G,""))
print("goals_done:", count(G,"status","done"))
print("subgoals_total:", count(S,""))
print("progress_events:", count(P,""))
PY
