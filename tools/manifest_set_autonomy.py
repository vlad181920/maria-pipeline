import re, io, datetime, sys, os
P = "project_manifest.md"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

ACTIVE = """## 5) АКТИВНИЙ БЛОК (поточний фокус)
Блок 12 — Earnings Autonomy Layer (платформо-агностичний заробіток).

Чому: Марія має **сама** обирати канали/платформи/методи заробітку, а ми даємо загальні інструменти мислення, знань, експериментів і метрик.

Definition of Done (без сайт-специфіки):
- [ ] Signals: `tools/earn_autonomy/signals_miner.py` → `artifacts/earn/signals.jsonl` (≥10 сигналів, з вагами та походженням).
- [ ] Strategy: `tools/earn_autonomy/strategy_selector.py` → `artifacts/earn/strategy.json` (гіпотеза каналу, очікувана цінність, ризики).
- [ ] Experiment Runner: `tools/earn_autonomy/experiment_runner.py` → `artifacts/earn/experiments/*/result.json` (мінімум 1 завершений експеримент з артефактом цінності).
- [ ] Metrics & Policy: `tools/earn_autonomy/metrics_report.py` → `artifacts/reports/earnings_daily_YYYY-MM-DD.json` (дохід/витрати/час/конверсії + рішення: continue/stop/scale).
- [ ] Policy Check: у коді **нема** жодних сайт-специфічних селекторів/URL (автотест `tools/earn_autonomy/policy_check.py`).
"""

NEXT = """## 6) Наступні 3 кроки
1) **Signals → Strategy:** зібрати нейтральні сигнали та обрати стратегію (без згадок платформ у коді).
2) **Experiment Runner:** реалізувати запуск мікроексперименту + лог + артефакт цінності.
3) **Metrics & Stop-loss:** щоденний звіт + правила зупинки/масштабування; оновити MANIFEST.
"""

def replace_section(s, header, new_block, next_header_regex):
    pat = rf"(##\s*{re.escape(header)}[\s\S]*?)(?=##\s*{next_header_regex})"
    if re.search(pat, s):
        return re.sub(pat, new_block + "\n", s)
    # якщо секція не знайдена — додаємо перед наступною
    return s + "\n" + new_block + "\n"

def main():
    if not os.path.exists(P):
        print("project_manifest.md not found"); sys.exit(1)
    s = io.open(P, "r", encoding="utf-8").read()

    s = replace_section(s, "5\\) АКТИВНИЙ БЛОК", ACTIVE, "6\\)")
    s = replace_section(s, "6\\) Наступні 3 кроки", NEXT, "7\\)")

    # додамо запис у кінець як штамп
    stamp = f"\n- [{now}] Активовано 'Earnings Autonomy Layer'; прибрано сайт-специфічні згадки з DoD (розд. 5–6).\n"
    s += stamp

    io.open(P, "w", encoding="utf-8").write(s)
    print("MANIFEST updated: sections 5–6 set to Earnings Autonomy Layer.")

if __name__ == "__main__":
    main()
