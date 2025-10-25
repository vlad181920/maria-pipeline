#!/bin/zsh
set -e
cd "$(dirname "$0")/../.."
export MARIA_HOME="$PWD"

LOG="artifacts/logs/earn_autonomy_tick.log"
mkdir -p "$(dirname "$LOG")"

echo "[$(date '+%F %T')] === EARN TICK START ===" | tee -a "$LOG"

# 1) Signals
sig_added=$(python3 tools/earn_autonomy/signals_miner.py || echo 0)
echo "[signals] added=${sig_added}" | tee -a "$LOG"

# 2) Strategy
strat_path=$(python3 tools/earn_autonomy/strategy_selector.py)
echo "[strategy] file=${strat_path}" | tee -a "$LOG"

# 2.1 Отримати name/slug НАДІЙНО (через розбиття на рядки у масив)
out=$(
python3 - <<'PY'
import json, re
j=json.load(open("artifacts/earn/strategy.json","r",encoding="utf-8"))
name=j["selected"]["name"]
s=name.lower()
s=re.sub(r"[^a-z0-9]+","-",s)
s=re.sub(r"-+","-",s).strip("-") or "exp"
print(name)
print(s)
PY
)

typeset -a arr
arr=("${(f)out}")          # split by newlines (zsh feature)
sel_name="${arr[1]}"
sel_slug="${arr[2]}"

# страховка: якщо з якоїсь причини slug порожній — обчислити ще раз у Python
if [[ -z "$sel_slug" ]]; then
  sel_slug=$(python3 - <<'PY'
import json, re
j=json.load(open("artifacts/earn/strategy.json","r",encoding="utf-8"))
name=j["selected"]["name"]
s=name.lower()
s=re.sub(r"[^a-z0-9]+","-",s)
s=re.sub(r"-+","-",s).strip("-") or "exp"
print(s)
PY
  )
fi

echo "[selected] name=${sel_name} slug=${sel_slug}" | tee -a "$LOG"

# 3) Create experiment if not exists
exp_glob=(artifacts/earn/experiments/*__${sel_slug}(N))
if (( ${#exp_glob} == 0 )); then
  exp_dir=$(python3 tools/earn_autonomy/experiment_runner.py)
  echo "[experiment] created=${exp_dir}" | tee -a "$LOG"
else
  echo "[experiment] exists=${exp_glob[-1]}" | tee -a "$LOG"
fi

# 4) Metrics report
rep_path=$(python3 tools/earn_autonomy/metrics_report.py)
echo "[report] file=${rep_path}" | tee -a "$LOG"

# Summary
python3 - <<'PY' | tee -a "$LOG"
import json, time
p=f"artifacts/reports/earnings_daily_{time.strftime('%Y-%m-%d')}.json"
j=json.load(open(p,"r",encoding="utf-8"))
tot=j["totals"]; rec=j.get("recommendation","continue")
print(f"[summary] leads={tot['leads']} conv={tot['conversions']} revenue=${tot['revenue_usd']:.2f} time_min={tot['time_spent_min']} decision={rec}")
PY

echo "[$(date '+%F %T')] === EARN TICK END ===" | tee -a "$LOG"
