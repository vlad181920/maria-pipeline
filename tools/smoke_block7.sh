#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
export MARIA_HOME="$PWD"
pre_done_goals=$(python3 - << 'PY'
import json, os
p="artifacts/goals/goals.jsonl"
d=0
try:
    with open(p,"r",encoding="utf-8") as f:
        for line in f:
            import json as J
            try:
                j=J.loads(line)
                if j.get("status")=="done": d+=1
            except: pass
except: pass
print(d)
PY
)
# 1) плануємо цілі з думок
created_goals=$(python3 tools/goal_planner.py | tail -n 1)
# 2) генеруємо підцілі
created_subs=$(python3 tools/subgoal_generator.py | tail -n 1)
# 3) тикаємо трекер кілька разів, щоб закрити підцілі
closed=0
for i in $(jot 9 1); do
  c=$(python3 tools/goal_progress_tracker.py | tail -n 1)
  closed=$((closed + c))
done
post_done_goals=$(python3 - << 'PY'
import json, os
p="artifacts/goals/goals.jsonl"
d=0
try:
    with open(p,"r",encoding="utf-8") as f:
        for line in f:
            import json as J
            try:
                j=J.loads(line)
                if j.get("status")=="done": d+=1
            except: pass
except: pass
print(d)
PY
)
echo "goals_created=${created_goals} subgoals_created=${created_subs} subgoals_closed=${closed} goals_done_delta=$((post_done_goals-pre_done_goals))"
