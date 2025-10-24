## 2025-09-24 — Експеримент 20250919_211414__micro-service-offer-audit-implementation
- Активна хвиля: B ($29)
- Попередня активна: A ($19)
- Файли: config.json, waves.jsonl, metrics_summary.json, metrics_history.jsonl, release/*.md
## 2025-09-24 — Експеримент 20250919_211414__micro-service-offer-audit-implementation
- Активна хвиля: A ($19), wave=2
- Попередня хвиля: B ($29), wave=1 — лід=1, конверсія=1, виручка=$29
- Файли: config.json, waves.jsonl, metrics_summary.json, metrics_history.jsonl, release/*.md
## 2025-09-30 — Експеримент 20250919_211414__micro-service-offer-audit-implementation
- Активна хвиля: B ($29.0), wave=10
- Див. metrics_history.jsonl та release/*

## Operational Runbook — Maria CLI

**Команда:** `maria <subcommand>` — доступна з будь-якого місця (додана в `PATH`).

### Основні команди
- `maria health` — повна перевірка (deps, схеми, черги, статус).
- `maria status` — короткий стан експерименту.
- `maria release` — згенерувати реліз (markdown у `artifacts/earn/experiments/*/release/`).
- `maria report` — швидкий звіт у `artifacts/earn/reports/`.

### Earn loop (автозапуск через launchd)
- `maria loop start` — старт агента (інтервал за замовчуванням 300s).
- `maria loop start --sec 120` — старт із кастомним інтервалом (секунди).
- `maria loop once` — один ручний прогін циклу.
- `maria loop stop` — зупинити агента.

**Логи агента:**
- `maria logs` — останні 100 рядків stdout/stderr.
- `maria tail` — live-перегляд логів.

### A/B експерименти
- `maria switch A 29` — увімкнути варіант **A** з ціною **$29**.
- `maria switch B 25` — увімкнути варіант **B** з ціною **$25**.

### Структура проєкту (релевантне)
- `bin/` — CLI (`maria`).
- `scripts/` — службові скрипти (loop, health, reports…).
- `tools/` — Python-утиліти (агрегація, шини, валідація).
- `artifacts/earn/` — релізи, звіти, логи.
- `schemas/` — JSON-схеми (events/commands/metrics_summary).

### Нотатки по CI/PR
- Гілка `main` захищена (вимагає статус **CI**).
- Пушимо у фіче-гілки (`feat/**`), відкриваємо PR.
- Мінімальний CI: `.github/workflows/ci.yml`.

### Швидкі приклади
```bash
maria loop start
maria health
maria report
maria switch B 27
maria loop stop


### Guard (нагляд за loop + авто-лікування)
- Автоперевірка health кожні ~3 хв, перезапускає `com.maria.earn.loop` за потреби.
- Логи: `artifacts/earn/logs/guard.out`, `guard.err`

**Команди:**
\`\`\`bash
# старт/перезапуск
launchctl load "$HOME/Library/LaunchAgents/com.maria.guard.plist"
launchctl kickstart -k "gui/\$(id -u)/com.maria.guard"

# зупинка
launchctl unload "\$HOME/Library/LaunchAgents/com.maria.guard.plist"

# логи
tail -f "\$HOME/maria/artifacts/earn/logs/guard.out" "\$HOME/maria/artifacts/earn/logs/guard.err"
\`\`\`
