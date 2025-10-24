import os, json, time, re, uuid, pathlib, textwrap

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STRAT = os.path.join(BASE, "artifacts", "earn", "strategy.json")
EXP_ROOT = os.path.join(BASE, "artifacts", "earn", "experiments")
REPORTS = os.path.join(BASE, "artifacts", "reports")
os.makedirs(EXP_ROOT, exist_ok=True); os.makedirs(REPORTS, exist_ok=True)

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "exp"

def write(path, content):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def jdump(path, obj):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def load_strategy():
    with open(STRAT, "r", encoding="utf-8") as f:
        return json.load(f)

def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def build_common_files(exp_dir, sel, archetype_name):
    fe = sel["first_experiment"]
    # README
    readme = f"""# Експеримент: {archetype_name}
Створено: {now()}

## Мета
{fe['objective']}

## Критерій успіху
{fe['success_criteria']}

## Бюджет
- Час: ≤ {fe['budget']['time_h']} год
- Гроші: ≤ ${fe['budget']['cash_usd']}

## Політика
- no_site_lockin = {fe['policy'].get('no_site_lockin', True)}
- max_hours = {fe['policy']['max_hours']}
- max_cash_usd = {fe['policy']['max_cash_usd']}

## Метрики для відстеження
- leads, conversions, revenue_usd, time_spent_min, cost_usd
- додаткові: ctr, cr, arpu, dau — за потребою

> Примітка: жодних сайт-специфічних кроків у коді. Канал/платформа обираються Марією окремо.
"""
    write(os.path.join(exp_dir, "README.md"), readme)

    # План дій (платформо-агностичний)
    plan = f"""# План-скелет (агностичний)
1) Визначити ICP (ідеальний профіль клієнта) та сценарій цінності (1–2 речення).
2) Побудувати артефакт цінності (див. deliverables/).
3) Сформувати пропозицію (offer.md) і 1–2 варіанти ціни.
4) Запустити мікроексперимент (канал вибирає Марія динамічно).
5) Зібрати метрики → оновити result.json → вчитись.

Контрольні точки:
- Stop-loss: якщо нема жодного сигналу цінності до 25% часу — змінити меседж/артефакт.
- Scale-up: якщо досягнуто критерій успіху — підготувати наступну ітерацію/масштаб.
"""
    write(os.path.join(exp_dir, "plan.md"), plan)

    # Початковий result.json
    result = {
        "id": str(uuid.uuid4()),
        "created_at": now(),
        "archetype": archetype_name,
        "status": "initialized",
        "metrics": {
            "leads": 0,
            "conversions": 0,
            "revenue_usd": 0.0,
            "time_spent_min": 0,
            "cost_usd": 0.0,
            "notes": []
        }
    }
    jdump(os.path.join(exp_dir, "result.json"), result)

def deliverables_for_micro_asset(exp_dir):
    ddir = os.path.join(exp_dir, "deliverables")
    # Мінімальний цифровий актив
    guide = """# Мінімальний гайд (чернетка)
## Назва
Як досягти X за N кроків

## Для кого
ICP: …

## Кроки
1) …
2) …
3) …

## Чеклист
- [ ] Пункт 1
- [ ] Пункт 2
- [ ] Пункт 3

## Додаток
Посилання на джерела/приклади (лише дозволені/відкриті).
"""
    write(os.path.join(ddir, "product.md"), guide)
    cover = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
<rect width="100%" height="100%" fill="#111"/><text x="60" y="140" fill="#fff" font-size="64">Digital Micro-Asset</text>
<text x="60" y="220" fill="#bbb" font-size="32">MVP cover — edit me</text></svg>"""
    write(os.path.join(ddir, "cover.svg"), cover)
    write(os.path.join(ddir, "README.txt"), "Згенеровано автоматично. Заповни product.md і онови cover.svg.")

def deliverables_for_micro_service(exp_dir):
    ddir = os.path.join(exp_dir, "deliverables")
    offer = """# Опис мікропослуги (чернетка)
## Назва
Аудит/Імплементація X за 48 годин

## Для кого (ICP)
- Галузь:
- Розмір:
- Симптоми проблеми:

## Обіцянка цінності
За 48 годин отримаєте ____ з чітким планом дій та прикладом реалізації.

## Склад роботи (SOW)
- Етап 1: Оцінка (2–3 ключових виміри)
- Етап 2: План дій з пріоритезацією
- Етап 3: Швидка імплементація (1 мікро-впровадження)

## Артефакти на виході
- Звіт (PDF/MD) + чеклист впровадження
- 1 шаблон (конфіг/скрипт/таблиця)

## Ціноутворення (чернетка)
- Пакет А: $___ (обсяг A)
- Пакет B: $___ (обсяг B)

## Гарантія
Якщо не корисно — повернення/переробка.

## Обмеження/ризики
- …
"""
    write(os.path.join(ddir, "offer.md"), offer)
    write(os.path.join(ddir, "deliverable_template.md"),
          "# Шаблон кінцевого артефакту\n\nОпис структури того, що клієнт отримує.\n")
    write(os.path.join(ddir, "checklist_20.md"),
          "\n".join([f"- [ ] Пункт {i}" for i in range(1,21)]))

def deliverables_for_automation_tool(exp_dir):
    ddir = os.path.join(exp_dir, "deliverables")
    write(os.path.join(ddir, "README.md"),
          "# Automation micro-tool (скелет)\n- cli.py (вхід)\n- module/\n- examples/\n")
    write(os.path.join(ddir, "cli.py"), "#!/usr/bin/env python3\nprint('hello-tool')\n")

def deliverables_for_data_brief(exp_dir):
    ddir = os.path.join(exp_dir, "deliverables")
    write(os.path.join(ddir, "brief.md"),
          "# Data/Research brief (чернетка)\n## Питання\n…\n## Дані/джерела\n…\n## Висновки\n…\n")
    write(os.path.join(ddir, "data.csv"), "column,title\n")

def deliverables_for_subscription(exp_dir):
    ddir = os.path.join(exp_dir, "deliverables")
    write(os.path.join(ddir, "issue_1.md"),
          "# Пілотний випуск №1\nТема: …\nКонтент: …\nПлан наступних 4 випусків: …\n")

def deliverables_for_affiliate(exp_dir):
    ddir = os.path.join(exp_dir, "deliverables")
    write(os.path.join(ddir, "brief.md"),
          "# Порівняльний бріф (чернетка)\n## Критерії\n…\n## Порівняння\n…\n## Рекомендації\n…\n")

def run():
    strat = load_strategy()
    sel = strat["selected"]
    archetype_name = sel["name"]
    exp_slug = slugify(archetype_name)
    exp_dir = os.path.join(EXP_ROOT, time.strftime("%Y%m%d_%H%M%S") + "__" + exp_slug)
    os.makedirs(exp_dir, exist_ok=True)

    build_common_files(exp_dir, sel, archetype_name)

    # Артефакти за архетипом (жодних сайтів)
    if "Digital micro-asset" in archetype_name:
        deliverables_for_micro_asset(exp_dir)
    elif "Micro-service" in archetype_name:
        deliverables_for_micro_service(exp_dir)
    elif "Automation micro-tool" in archetype_name:
        deliverables_for_automation_tool(exp_dir)
    elif "Data/Research brief" in archetype_name:
        deliverables_for_data_brief(exp_dir)
    elif "Subscription mini" in archetype_name:
        deliverables_for_subscription(exp_dir)
    else:  # Affiliate/comparison
        deliverables_for_affiliate(exp_dir)

    print(exp_dir)

if __name__ == "__main__":
    run()
