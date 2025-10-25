import os, json, glob, time, uuid, pathlib

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EARN = os.path.join(BASE, "artifacts", "earn")
DEC  = os.path.join(EARN, "channel_decision.json")
EXP_ROOT = os.path.join(EARN, "experiments")

def latest_exp_dir():
    exps = sorted([p for p in glob.glob(os.path.join(EXP_ROOT, "*")) if os.path.isdir(p)])
    return exps[-1] if exps else None

def load_json(p, default=None):
    try:
        with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default

def write_text(p, s):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p,"w",encoding="utf-8") as f: f.write(s)

def dump_json(p, obj):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p,"w",encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def mk_id(prefix="probe"):
    return f"{prefix}-{time.strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"

def probes_for_channel(ch_id, ch_name):
    # 3 платформи-агностичні мікро-проби; кожна — ≤90 хв
    if ch_id == "owned-longform":
        return [
            {
              "id": mk_id(), "name": "Outline → One-Pager",
              "assumption": "Чітка структура й one-pager під ICP викличуть інтерес (ліди/відгуки).",
              "steps": [
                "Зібрати 3–5 меседжів ICP з strategy/signals.",
                "Скласти outline (10–12 пунктів) і 1-сторінковий one-pager у deliverables/onepager.md.",
                "Підготувати 2–3 короткі прев’ю-витяги (цитати/буліти) у deliverables/snippets.md."
              ],
              "artifacts": ["deliverables/onepager.md","deliverables/snippets.md"],
              "metrics_expected": {"leads": ">=1 або явний інтерес", "time_spent_min": "<=90"},
              "timebox_min": 90,
              "stop_rule": "0 сигналів інтересу після поширення прев’ю → змінити меседж/структуру.",
              "scale_rule": "Якщо є лід/відгук — розширити до повного гайду."
            },
            {
              "id": mk_id(), "name": "Mini-Brief (600–900 слів)",
              "assumption": "Стиснута версія гайду з прикладами підвищує конверсію у запит.",
              "steps": [
                "Написати mini-brief 600–900 слів у deliverables/brief.md (проблема→рішення→кроки→чеклист).",
                "Додати 1 невеликий приклад/кейс (вигаданий або узагальнений) у розділ 'Приклад'."
              ],
              "artifacts": ["deliverables/brief.md"],
              "metrics_expected": {"leads": ">=1/90хв при перевірці", "conversions": ">=0 або чіткі запити"},
              "timebox_min": 90,
              "stop_rule": "Нуль запитів/інтересу → змінити заголовок і перші 150 слів.",
              "scale_rule": "Є запит → готувати повну версію та план продажу."
            },
            {
              "id": mk_id(), "name": "Checklist-20 (діагностичний)",
              "assumption": "Чеклист на 20 пунктів генерує корисність і знижує бар’єр контакту.",
              "steps": [
                "Наповнити deliverables/checklist_20.md конкретикою (без води, буліти).",
                "Додати інструкцію користування (5 рядків) на початку файлу."
              ],
              "artifacts": ["deliverables/checklist_20.md"],
              "metrics_expected": {"leads": ">=1 із користувачів чеклисту", "time_spent_min": "<=60"},
              "timebox_min": 60,
              "stop_rule": "0 реакцій → переформулювати 5 перших пунктів під біль ICP.",
              "scale_rule": "Є реакції → зробити 'pro'-версію з прикладами."
            },
        ]
    # дефолт (інші канали) — універсальні проби
    return [
        {
          "id": mk_id(), "name": f"Value Snippets for {ch_name}",
          "assumption": "Короткі витяги цінності стимулюють контакт.",
          "steps": ["Зібрати 5 буліт-сніпетів у deliverables/snippets.md."],
          "artifacts": ["deliverables/snippets.md"],
          "metrics_expected": {"leads": ">=1", "time_spent_min": "<=60"},
          "timebox_min": 60,
          "stop_rule": "0 реакцій → змінити кут/заголовок.",
          "scale_rule": "Реакції є → зібрати у one-pager."
        },
        {
          "id": mk_id(), "name": "Mini-Brief (600–900)",
          "assumption": "Стисла версія підвищує конверсію у запит.",
          "steps": ["Написати mini-brief у deliverables/brief.md."],
          "artifacts": ["deliverables/brief.md"],
          "metrics_expected": {"leads": ">=1/90хв"},
          "timebox_min": 90,
          "stop_rule": "0 лід-сигналів → змінити перші 150 слів.",
          "scale_rule": "Є лід → розширення."
        },
        {
          "id": mk_id(), "name": "Checklist-20 tune",
          "assumption": "Чеклист знижує бар’єр.",
          "steps": ["Оновити deliverables/checklist_20.md під ICP."],
          "artifacts": ["deliverables/checklist_20.md"],
          "metrics_expected": {"leads": ">=1"},
          "timebox_min": 60,
          "stop_rule": "0 реакцій → змінити перші 5 пунктів.",
          "scale_rule": "Є інтерес → pro-версія."
        },
    ]

def main():
    dec = load_json(DEC, {})
    selected = dec.get("selected") or {}
    ch_id = selected.get("id","owned-longform")
    ch_name = selected.get("name","Owned longform")

    exp_dir = latest_exp_dir()
    if not exp_dir:
        print("no experiment dir"); return

    # Завантажити/оновити result.json
    rpath = os.path.join(exp_dir, "result.json")
    res = load_json(rpath, {"metrics": {}})
    res.setdefault("probes", [])
    if res.get("status") == "prepared":
        res["status"] = "planned"

    # Згенерувати 3 мікро-проби
    new_probes = probes_for_channel(ch_id, ch_name)
    res["probes"] = new_probes

    # Записати
    dump_json(rpath, res)

    # Людинозрозумілий план
    md = ["# Micro-probes (агностичні)", f"Канал: **{ch_name}**", ""]
    for i, p in enumerate(new_probes, 1):
        md.append(f"## {i}) {p['name']}  \nID: `{p['id']}`")
        md.append(f"**Гіпотеза:** {p['assumption']}")
        md.append(f"**Артефакти:** {', '.join(p['artifacts'])}")
        md.append(f"**Кроки:**")
        for s in p["steps"]:
            md.append(f"- {s}")
        md.append(f"**Метрики (очікування):** {json.dumps(p['metrics_expected'], ensure_ascii=False)}")
        md.append(f"**Таймбокс:** {p['timebox_min']} хв")
        md.append(f"**Stop:** {p['stop_rule']}")
        md.append(f"**Scale:** {p['scale_rule']}")
        md.append("")
    write_text(os.path.join(exp_dir, "probes.md"), "\n".join(md) + f"\n— Автогенерація: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(exp_dir)

if __name__ == "__main__":
    main()
