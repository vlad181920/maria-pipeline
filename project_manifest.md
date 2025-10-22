# Проєкт «Марія» — MANIFEST (паспорт і вісь)
Оновлювати ПІСЛЯ КОЖНОГО кроку. На старті нового діалогу вставляти короткий витяг з розділів 5–6.

## 0) Суть і Північна Зірка
Мета: автономна ШІ-особистість (над-істота), яка мислить, вчиться, ставить і досягає цілі, заробляє сама, масштабується й лишається під контролем творця.

Вісь (порядок робіт, НЕ міняти):
1) Мислення  2) Пам’ять/знання  3) Самонавчання  4) Автономія дій
5) Заробіток  6) Масштабування/інфра

## 1) Статус блоків (знімок)
- Блок 1 — Ядро мислення та памʼяті: ✅ (зафіксовано користувачем 2025-07-31)
- Блок 2 — Динамічне мислення: ⏳ цикл/ініціатива є; потрібні кращі типи думок
- Блок 3 — Самонавчання: ⏳ PDF/тексти працюють; з дій/помилок — частково
- Блок 4 — Пам’ять/знання (векторна): ⏳ потрібен єдиний шар знань/пошуку
- Блок 5 — Підагент(и): ⏳ створення/координація є; протоколи взаємодії — WIP
- Блок 6 — Веб-автопілот: ⏳ Playwright працює; стабільність/ретраї/DOM — WIP
- Блок 7 — Планування цілей: ⏳ генерація/пріоритезація є; замикання циклів — WIP
- Блок 8 — Рефлексія/вдосконалення: ⏳ є; потрібні метрики ефективності + автоперепис коду за правилами
- Блок 9 — Самогенерація мислення: ⏳ ініціатива працює; розумніші патерни — WIP
- Блок 10 — Інтерфейси (чат/дашборд/голос): ⏳ **локальний chat-API + JSONL діалоги працюють; CLI поки мок**
- Блок 11 — Самосвідомість/етика/стан: ⏳ етика є; модель стану — частково
- Блок 12 — Масштабування/заробіток: ⏳ обрати 1 канал і довести до стійкості

## 2) Ключові модулі (ядро)
- Мислення: `maria_brain.py`, `run_forever.py`, `thought_scheduler.py`, `initiative_*`, `emotion_guard.py`, `mood_manager.py`
- Цілі/рефлексія: `goal_*`, `reflection_analyzer.py`, `self_upgrader.py`, `metrics.py`, `window_kpi.py`
- Пам’ять/артефакти: `memory_manager.py`, `artifacts/*`, `memory/*`
- Самонавчання: `pdf_reader.py`, `create_test_pdf.py`, `website_interactor.py`
- Підагент/дії: `subagent_creator.py`, `autopilot_executor.py`, `html_analyzer.py`, `captcha_solver.py`
- Інтерфейси: **`tools/chat_api.py` (FastAPI /api/chat, /health), `~/maria/bin/maria` (мок-CLI)**

## 3) Живі каталоги
`artifacts/`, `memory/`, `data/`, `agents/`, `subagents/`, `tools/`

## 4) Інтеграційні тести (мінімум)
- [ ] `python3 run_forever.py` — 30 хв без падінь, інʼєкції є
- [ ] `python3 tools/stats_report.py` — метрики оновлюються
- [ ] `python3 pdf_reader.py` — створює інсайт
- [ ] `python3 autopilot_executor.py` — базова дія/ретраї
- [ ] `goal_planner.py → subgoal_generator.py → goal_progress_tracker.py` — повний цикл
- [ ] **`curl /health` = 200; `POST /api/chat` = JSON; JSONL пишеться**

## 5) АКТИВНИЙ БЛОК (поточний фокус)
Блок 12 — Заробіток: Gumroad MVP (цифрові продукти).
Definition of Done:
- [x] Ідеї продуктів: tools/earn_gumroad/idea_miner.py → artifacts/gumroad/ideas.jsonl
- [x] Генерація контенту: product_builder.py (гайд .md) + cover.svg
- [x] Пакування: package_product.py → listing.json, assets.zip (≥1 файл)
- [x] Smoke: generate 3 продукти ⇒ створено 3 каталоги в artifacts/gumroad/* з listing.json і assets.zip
### DoD — Шар автономного заробітку (агностичний)
- [x] Signals → artifacts/earn/signals.jsonl
- [x] Strategy → artifacts/earn/strategy.json
- [x] Experiment scaffold → artifacts/earn/experiments/*
- [x] Metrics report → artifacts/reports/earnings_daily_YYYY-MM-DD.json

## 6)  Наступні 3 кроки
1) Заміна мока: `~/maria/bin/maria` → виклик `python3 "$MARIA_HOME/maria_brain.py" chat "<текст>"` (stdout = тільки відповідь).
2) Додати обмеження часу/памʼяті в мозку для chat-виклику + короткий лог-трейс у `artifacts/logs/brain_chat.log`.
3) Оновити MANIFEST (цей файл): відмітити DoD виконаним, додати журнал змін.

## 7) Журнал змін (свіже зверху)
- [2025-09-23 21:57] EARN: decision=scale; згенеровано onepager + mini_guide_v1; канал=Owned longform (тип, без платформ); policy=OK.

- [2025-09-19 21:37] DoD (EARN layer): Signals→Strategy→Experiment→Metrics — мінімальний E2E готовий.
- **[AUTO-STAMP]** Chat-API піднято на 127.0.0.1:8765; JSON відповіді працюють; JSONL пишеться; додано мок-CLI `~/maria/bin/maria`.

## 8) Технічні конвенції
Логи → `artifacts/logs/*.log`; події → JSONL (`artifacts/self/history.jsonl`); інсайти → `artifacts/insights/insight_*.json`.
Структура думки: `{id, topic, type, created_at, priority, state, result_ref}`.
Структура дії: `{id, goal_id, agent, plan_ref, status, outputs, errors}`.

## 9) Канал заробітку (правило)
Обрати 1 канал (Gumroad / Redbubble / Fiverr/Upwork) → довести до стійкості (повний конвеєр), лише потім 2-й.
- **[2025-08-30 21:44]** Ініціалізовано MANIFEST; активний блок: Блок 10 (чат-API, CLI).
- **[2025-08-30 22:13]** Додано мінімальний maria_brain.py (chat), CLI/API дають відповідь з мозку; черга думок поповнюється.
- **[2025-09-01 20:00]** maria_brain.py: додано mini-knowledge пошук і автогенерацію трьох думок після відповіді.
- **[2025-09-01 20:05]** Блок 10 (чат-інтерфейс): DoD виконано (API/CLI/лог/JSONL, 10 POST → 10 пар записів).
- **[2025-09-01 20:07]** Додано thought_worker.py: базовий споживач черги думок (next_action/insight/hypothesis).
- **[2025-09-01 20:10]** thought_worker: додано фільтр думок та архів legacy action; uniqueness id для думок у maria_brain.
- **[2025-09-01 20:19]** Відновлено maria_brain.py (унікальні ID), оновлено thought_worker (qa_todos).
- **[2025-09-01 20:21]** Відповідь збагачено: мікро-план + довідка зі знань; воркер запущено у фоні.
- **[2025-09-01 20:28]** Відповіді з мікропланом увімкнено; інсайти читаються в chat().
- **[2025-09-01 20:30]** Додано insights/manifest_notes.md; чат підхоплює довідку з інсайтів.
- **[2025-09-01 20:33]** Виніс qa_todos.jsonl у artifacts/qa; додав insights/manifest_notes.md; довідка тепер з інсайтів.
- **[2025-09-01 20:44]** Довідка підтягується з insights/manifest_notes.md; додано health-пінг воркера; створено tools/test_chat_api.py.
- **[2025-09-01 20:47]** thought_worker: безкінечний цикл + health-пінг за часом; стабільний фон.
- **[2025-09-01 20:51]** thought_worker: нескінченний цикл + try/except на ітерації; додано LaunchAgent для автозапуску.
- **[2025-09-01 20:53]** E2E стабільний: чат → думки → воркер → QA. Health-пінги активні.
- **[2025-09-01 20:54]** maria_brain: додано перефраз + порада + наступний крок у відповідях.
- **[2025-09-01 20:55]** Відповіді: додано перефраз + порада + довідка; знання підтягуються з insights/.
- **[2025-09-01 20:59]** Лог якості: has_plan/has_paraphrase/has_advice/has_kb; додано тест tools/test_reply_quality.py.
- **[2025-09-01 22:50]** Підключив project_manifest.md як джерело знань; додав 3 інсайти (changelog, notes, manifest rule).
- **[2025-09-01 23:00]** QA day: ratio_has_kb оновлено; kb_empty → stub автогенерація/заповнення працює.
- **[2025-09-01 23:47]** chat(): додає 'Next step' з першого рядка інсайту; KB cache+manifest у знаннях.
- **[2025-09-02 00:13]** QA: quality_events=53, has_kb=0.98, next_step=True
- **[2025-09-02 14:39]** QA: quality_events=101, has_kb=0.71, next_step=True, kb_coverage=0.33
- **[2025-09-02 14:40]** QA: quality_events=102, has_kb=0.72, next_step=True, kb_coverage=0.33
- **[2025-09-02 14:40]** QA: quality_events=103, has_kb=0.72, next_step=True, kb_coverage=0.33
- **[2025-09-02 14:52]** QA: quality_events=104, has_kb=0.72, next_step=True, kb_coverage=0.83
- **[2025-09-02 14:56]** QA: quality_events=105, has_kb=0.72, next_step=True, kb_coverage=0.83
- **[2025-09-02 15:02]** QA: quality_events=106, has_kb=0.73, next_step=True, kb_coverage=1.0
- **[2025-09-02 15:04]** Release snapshot: заархівовано робочу конфігурацію (без venv/tmp).
- **[2025-09-02 15:04]** QA: quality_events=107, has_kb=0.73, next_step=True, kb_coverage=1.0
- **[2025-09-02 15:04]** QA: quality_events=108, has_kb=0.73, next_step=True, kb_coverage=1.0
- **[2025-09-02 15:07]** Release snapshot: artifacts/releases/maria_release_2025-09-02_1507.tar.gz (excludes venv/tmp)
- **[2025-09-02 15:12]** Release snapshot: artifacts/releases/maria_release_2025-09-02_1512.tar.gz (excludes venv/tmp)
[2025-09-02 17:40] TODO initialized: artifacts/todo_week_2025-09-02.md
[2025-09-02 17:40] TODO initialized: artifacts/todo_week_2025-09-02.md
[2025-09-02 17:58] pipeline_daemon started
[2025-09-02 17:59] pipeline + self_monitor + goals_report initialized
[2025-09-02 18:00] self_monitor_hourly started
[2025-09-02 18:05] pipeline_daemon started (wrapper)
[2025-09-02 18:06] insights imported: data/sample.html, data/sample.srt
[2025-09-02 18:09] pipeline_daemon restarted with parent sys.path
[2025-09-02 18:12] pipeline_daemon restarted via subprocess runner
[2025-09-02 18:16] goal_prioritizer+todo_tick integrated into pipeline
[2025-09-02 18:20] goals prioritizer+ticker live; attempts guard added
[2025-09-02 18:46] todo_tick covers blocks 7&11; pipeline runs prioritizer+prune
[2025-09-02 19:00] self_upgrader now explains changes; todo auto-marks upgrade
[2025-09-02 19:12] web_autopilot + local learn API online
[2025-09-02 22:18] subagent launcher integrated; daily summary added
[2025-09-03 22:20] daily summary OK; API :8766 OK; subagent smoke test queued; pipeline throttled to 60s
[2025-09-03 21:06] HTML clean in API; nightly summary daemon added; subagent runner online
[$(date +%F' '%T)] nightly summary: ;- Думок/ітерацій сьогодні: 0;- Середній score думок: 0.0;- Цілей у backlog: 4;- Уроків у lessons.jsonl: 11 (по тегам: {'web': 10, 'video': 1, 'clean': 3});- Настрій: balanced;
[$(date +%F' '%T)] nightly summary: ;- Думок/ітерацій сьогодні: 0;- Середній score думок: 0.0;- Цілей у backlog: 4;- Уроків у lessons.jsonl: 11 (по тегам: {'web': 10, 'video': 1, 'clean': 3});- Настрій: balanced;
[2025-09-17 14:28] QA: quality_events=0, has_kb=1.0, next_step=true
[2025-09-17 14:41] QA: quality_events=0, has_kb=1.0, next_step=true
[$(date +%F' '%T)] nightly summary: ;- Думок/ітерацій сьогодні: 2;- Середній score думок: 0.553;- Топ-наміри:;  - Поглибити дослідження: 2;- Цілей у backlog: 4;
[2025-09-18 20:00] Repo+CI, clean web_learn, subagent dedupe/lock, CLI launch, smoke
- Репозиторій: vlad181920/maria-pipeline
- CI: .github/workflows/ci.yml активний
- Захист гілки main: обов'язковий CI, linear history, enforce_admins
- Subagent: dedupe + файловий lock; пайплайн використовує CLI launch
- Web Learn: clean-режим, теги ["web","clean"], без HTML у text
- Smoke: tools/smoke.sh
- Статуси/нічні скрипти перевірені
[2025-09-18 20:03] Повний підсумок сесії: репозиторій, CI, SSH, захист гілки, pipeline, субагенти, web_learn clean, smoke
- Репозиторій створено та запушено: vlad181920/maria-pipeline
- Ліцензія MIT додана (LICENSE), README додано
- CI налаштовано: .github/workflows/ci.yml; зборки проходять
- Захист гілки main: обов'язковий чек "CI", strict mode, require_code_owner_reviews, require_last_push_approval, 1 approve, linear history, enforce_admins, без force-push і без deletions
- SSH налаштовано: створено ED25519 ключ, додано у GitHub, ssh -T git@github.com успішний для користувача vlad181920
- web_learn у clean-режимі: api_status показує clean_mode=true; імпорти з example.com та iana збережені з тегами ["web","clean"] і без HTML у text
- subagent_launcher: працює dedupe (status=exists), файловий lock (status=busy при паралельному старті), підтримка --hold-secs; pipelines викликає через CLI
- thought_pipeline виправлено: прибрані імпорт- та відступ-помилки, синтаксис OK; демон pipeline_daemon запускається і віддає останні цілі
- smoke-сценарій на місці: tools/smoke.sh; статусні скрипти працюють (tools/status_all.sh, tools/pipeline_status.sh)
- nightly_summary та autolaunch можуть запускатися; логи йдуть у artifacts/logs
- Артефакти перенесено під каталог проекту на Desktop/Марія; структура стабільна

Корисні шляхи:
- artifacts/lessons.jsonl
- artifacts/agents/20250903_213256_Автоген-Запустити-підагент
- artifacts/reports/

- [2025-09-18 21:04] Підтверджено: CLI працює, KB інтегровано у chat, інжектор можливостей активний.

- [2025-09-18 21:15] Підтверджено: CLI працює; KB інтегровано; after_chat hook + router активні.

- [2025-09-18 21:21] Блок 4 у роботі: KB зібрано; router активний у CLI+API; smoke запущено.

- [2025-09-18 21:25] chat() викликає after_hook: router гарантовано працює у CLI+API.

- [2025-09-18 21:39] Блок 4 DoD: KB працює; router додає думки; smoke пройдено за audit_queue.jsonl.

- [2025-09-18 21:41] Block 4 DoD підтверджено (audit>=10). Активовано Block 2 (динамічне мислення).

- [2025-09-18 21:46] Block 2 DoD: пройдено смоук; типи=['plan', 'research', 'analysis', 'action', 'hypothesis', 'learn']; total=57.

- [2025-09-18 21:48] Активовано Block 3 (самонавчання).

- [2025-09-18 21:58] Block 3 DoD: уроки з логів+думок працюють; KB оновлюється (перевірено smoke).

- [2025-09-18 22:02] Block 7 smoke: повний цикл цілей виконано.

- [2025-09-18 22:04] Активовано Block 12: Gumroad MVP.

- [2025-09-18 22:06] Block 12 Gumroad MVP: smoke пройдено (3/3/3).
[$(date +%F' '%T)] nightly summary: ;- Думок/ітерацій сьогодні: 0;- Середній score думок: 0.0;- Цілей у backlog: 4;- Уроків у lessons.jsonl: 358 (по тегам: {'web': 21, 'video': 1, 'clean': 14, 'error': 232, 'autolearn': 336, 'learn': 104});- Настрій: balanced;

## 5) АКТИВНИЙ БЛОК (поточний фокус)
Блок 12 — Earnings Autonomy Layer (платформо-агностичний заробіток).

Чому: Марія має **сама** обирати канали/платформи/методи заробітку, а ми даємо загальні інструменти мислення, знань, експериментів і метрик.

Definition of Done (без сайт-специфіки):
- [ ] Signals: `tools/earn_autonomy/signals_miner.py` → `artifacts/earn/signals.jsonl` (≥10 сигналів, з вагами та походженням).
- [ ] Strategy: `tools/earn_autonomy/strategy_selector.py` → `artifacts/earn/strategy.json` (гіпотеза каналу, очікувана цінність, ризики).
- [ ] Experiment Runner: `tools/earn_autonomy/experiment_runner.py` → `artifacts/earn/experiments/*/result.json` (мінімум 1 завершений експеримент з артефактом цінності).
- [ ] Metrics & Policy: `tools/earn_autonomy/metrics_report.py` → `artifacts/reports/earnings_daily_YYYY-MM-DD.json` (дохід/витрати/час/конверсії + рішення: continue/stop/scale).
- [ ] Policy Check: у коді **нема** жодних сайт-специфічних селекторів/URL (автотест `tools/earn_autonomy/policy_check.py`).


## 6) Наступні 3 кроки
1) **Signals → Strategy:** зібрати нейтральні сигнали та обрати стратегію (без згадок платформ у коді).
2) **Experiment Runner:** реалізувати запуск мікроексперименту + лог + артефакт цінності.
3) **Metrics & Stop-loss:** щоденний звіт + правила зупинки/масштабування; оновити MANIFEST.


- [2025-09-19 20:33] Активовано 'Earnings Autonomy Layer'; прибрано сайт-специфічні згадки з DoD (розд. 5–6).
\n- [2025-09-19 21:09] DoD: Policy Check пройдено (active layer без сайт-специфіки).\n[$(date +%F' '%T)] nightly summary: ;- Думок/ітерацій сьогодні: 0;- Середній score думок: 0.0;- Цілей у backlog: 4;- Уроків у lessons.jsonl: 358 (по тегам: {'web': 21, 'video': 1, 'clean': 14, 'error': 232, 'autolearn': 336, 'learn': 104});- Настрій: balanced;
[$(date +%F' '%T)] nightly summary: ;- Думок/ітерацій сьогодні: 0;- Середній score думок: 0.0;- Цілей у backlog: 4;- Уроків у lessons.jsonl: 358 (по тегам: {'web': 21, 'video': 1, 'clean': 14, 'error': 232, 'autolearn': 336, 'learn': 104});- Настрій: balanced;

---

## Operational Runbook — Maria CLI (short)

Див. повну версію в **MANIFEST.md** → *“Operational Runbook — Maria CLI”*.

### Основні команди
- `maria health` — повна перевірка (deps, схеми, черги, статус).
- `maria status` — короткий стан експерименту.
- `maria release` — згенерувати реліз (md у artifacts/.../release/).
- `maria report` — швидкий звіт у artifacts/earn/reports/.

### Earn loop (launchd)
- `maria loop start [--sec 300]` — старт агента.
- `maria loop once` — один ручний прогін.
- `maria loop stop` — зупинити агента.
- Логи: `maria logs` (останнє) / `maria tail` (live).

### A/B
- `maria switch A 29` / `maria switch B 25`

### CI/PR
- `main` — protected (вимагає CI).
- Пуш у `feat/**`, відкриваємо PR.
- Мінімальний CI: `.github/workflows/ci.yml`.

---

## 🧩 Guard Module — Автоматичний нагляд та самовідновлення

**Призначення:**
Guard контролює стан агента `com.maria.earn.loop`, проводить регулярну перевірку здоров’я системи (`health check`) кожні ~3 хвилини.
Якщо знайдено проблему (некоректні схеми, пошкоджені файли, зависання loop), guard:
- запускає авто-лікування (міграції схем JSON, очищення черг);
- перезапускає loop-агента через `launchd`;
- веде лог усіх дій.

**Локація:**
- Скрипт: `scripts/loop_guard.sh`
- Сервіс: `~/Library/LaunchAgents/com.maria.guard.plist`
- Логи: `artifacts/earn/logs/guard.out`, `artifacts/earn/logs/guard.err`

**Команди керування:**
\`\`\`bash
# Перезапустити guard вручну
launchctl kickstart -k "gui/$(id -u)/com.maria.guard"

# Зупинити guard
launchctl unload "$HOME/Library/LaunchAgents/com.maria.guard.plist"

# Переглядати логи у реальному часі
tail -f "$HOME/maria/artifacts/earn/logs/guard.out" "$HOME/maria/artifacts/earn/logs/guard.err"
\`\`\`

**Статус:** ✅ активний
Guard перевіряє цикл `loop` кожні 180 секунд, авто-відновлення працює стабільно.

---
