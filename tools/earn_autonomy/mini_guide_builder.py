import os, json, glob, time, pathlib

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EARN = os.path.join(BASE, "artifacts", "earn")
STRAT = os.path.join(EARN, "strategy.json")

def latest_exp_dir():
    root = os.path.join(EARN, "experiments")
    exps = sorted([p for p in glob.glob(os.path.join(root, "*")) if os.path.isdir(p)])
    return exps[-1] if exps else None

def read_text(p):
    try:
        with open(p, "r", encoding="utf-8") as f: return f.read()
    except Exception:
        return ""

def write_text(p, s):
    pathlib.Path(os.path.dirname(p)).mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(s)

def jload(p, default=None):
    try:
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    except Exception:
        return default

def jdump(p, obj):
    pathlib.Path(os.path.dirname(p)).mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def build_onepager(exp_dir, offer_md, checklist_md, signals):
    # взяти до 6 коротких сигналів (зверху)
    sig_lines = []
    for s in signals[:6]:
        t = str(s.get("text","")).strip()
        if t.startswith("THOUGHT:"): t = t.replace("THOUGHT:", "").strip()
        sig_lines.append(f"- {t}"[:300])
    sig_block = "\n".join(sig_lines) if sig_lines else "- (сигнали відсутні)"

    checklist_preview = "\n".join(
        [l for l in checklist_md.splitlines() if l.strip().startswith("- ")]
    ).splitlines()[:10]
    checklist_preview = "\n".join(checklist_preview) if checklist_preview else "- (додати пункти)"

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    onepager = f"""# One-Pager: «Монетизація за 48 годин»
Згенеровано: {now}

## Для кого (ICP)
Власники невеликих онлайн-проєктів і творці цифрових продуктів.

## Обіцянка цінності
За 48 годин: короткий аудит + пріоритетний план + 1 мікро-впровадження.

## Що саме робимо (3 етапи)
1) 0–8 год: аудит (цілі, ICP, пропозиція цінності, бар’єри).
2) 8–24 год: план дій + 1 мікро-впровадження (без прив’язки до платформ).
3) 24–48 год: мінімальний запуск, збір метрик, наступні кроки.

## Сигнали/доводи (витяг)
{sig_block}

## Чеклист (фрагмент 10/20)
{checklist_preview}

## Як міряти
- leads, conversions, revenue_usd, time_spent_min, cost_usd
- оновлення: `tools/earn_autonomy/metrics_update.py` (див. приклади у README експерименту)

## Наступний крок
Зібрати прев’ю-сніпети, створити mini-guide v1 та рознести у канали **типу** owned longform.
"""
    opath = os.path.join(exp_dir, "deliverables", "onepager.md")
    write_text(opath, onepager)
    return opath

def build_mini_guide(exp_dir, offer_md, checklist_md, onepager_md):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    body = f"""# Монетизація за 48 годин — Mini-Guide v1
Згенеровано: {now}

## 1) Для кого (ICP) і проблема
- Власники невеликих онлайн-проєктів / творці цифрових продуктів.
- Типові бар’єри: нечіткий меседж, слабка пропозиція цінності, відсутність швидкого експерименту.

## 2) Обіцянка цінності
Короткий аудит → пріоритетний план → 1 мікро-впровадження за 48 год.

## 3) План дій (48 год)
**Етап 1 (0–8 год):** аудит (цілі, ICP, пропозиція, бар’єри).
**Етап 2 (8–24 год):** план + 1 впровадження (артефакт у `deliverables/`).
**Етап 3 (24–48 год):** мінімальний запуск, метрики, підсумки, наступні кроки.

## 4) One-Pager (витяг)
{onepager_md.strip()[:2000]}

## 5) Приклад оферу (витяг)
{offer_md.strip()[:2000]}

## 6) Чеклист 20 пунктів
{checklist_md.strip()}

## 7) Як міряти ефективність
- **Основні:** leads, conversions, revenue_usd, time_spent_min, cost_usd
- **Команди прикладів:**
  - `python3 tools/earn_autonomy/metrics_update.py --leads +1 --note "лід з прев’ю" --report`
  - `python3 tools/earn_autonomy/metrics_update.py --conversions +1 --revenue +19 --note "оплата" --report`

## 8) Доставка (без прив’язки до платформ)
- Зібрати 2–3 прев’ю з `deliverables/snippets.md`
- Рознести у відповідні **типи** носіїв каналу (owned longform), **без** згадок конкретних сайтів у коді.
"""
    mpath = os.path.join(exp_dir, "deliverables", "mini_guide_v1.md")
    write_text(mpath, body)
    return mpath

def build_snippets(exp_dir, onepager_md):
    lines = [l.strip("-• ").strip() for l in onepager_md.splitlines() if l.strip()][:120]
    # виберемо 3 короткі тези
    picks = []
    for l in lines:
        if len(picks) >= 3: break
        if 20 <= len(l) <= 140:
            picks.append(l[:140])
    if not picks:
        picks = [
            "48 годин: аудит → план → мікро-впровадження.",
            "One-pager + mini-guide v1 для швидкого старту.",
            "Метрики: leads, conversions, revenue, time, cost."
        ]
    s = "\n".join([f"- {p}" for p in picks])
    spath = os.path.join(exp_dir, "deliverables", "snippets.md")
    write_text(spath, s)
    return spath

def main():
    exp = latest_exp_dir()
    if not exp:
        print("no experiment dir"); return
    ddir = os.path.join(exp, "deliverables")
    pathlib.Path(ddir).mkdir(parents=True, exist_ok=True)

    offer_md = read_text(os.path.join(ddir, "offer.md"))
    checklist_md = read_text(os.path.join(ddir, "checklist_20.md"))
    onepager_path = os.path.join(ddir, "onepager.md")
    onepager_md = read_text(onepager_path)

    strategy = jload(STRAT, {}) or {}
    signals = strategy.get("top_signals", [])

    # якщо onepager порожній — згенерувати
    if not onepager_md.strip():
        onepager_path = build_onepager(exp, offer_md, checklist_md, signals)
        onepager_md = read_text(onepager_path)

    # mini-guide + snippets
    mini_path = build_mini_guide(exp, offer_md, checklist_md, onepager_md)
    snip_path = build_snippets(exp, onepager_md)

    # примітка в result.json
    rpath = os.path.join(exp, "result.json")
    res = jload(rpath, {}) or {}
    notes = res.setdefault("metrics", {}).setdefault("notes", [])
    notes.append(f"mini_guide_v1 built at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    jdump(rpath, res)

    print("onepager:", onepager_path)
    print("mini_guide:", mini_path)
    print("snippets:", snip_path)

if __name__ == "__main__":
    main()
