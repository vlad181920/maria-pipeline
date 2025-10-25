import os, re, json, glob, time, pathlib

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXP_ROOT = os.path.join(BASE, "artifacts", "earn", "experiments")
STRAT = os.path.join(BASE, "artifacts", "earn", "strategy.json")

def latest_experiment_dir(root):
    cand = sorted([p for p in glob.glob(os.path.join(root,"*")) if os.path.isdir(p)])
    return cand[-1] if cand else None

def read_strategy(path):
    try:
        return json.load(open(path,"r",encoding="utf-8"))
    except Exception as e:
        return None

def ensure_dir(p):
    pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)

def write(p, s):
    ensure_dir(p)
    with open(p,"w",encoding="utf-8") as f: f.write(s)

def load_top_signals(strat, k=6):
    out=[]
    if not strat: return out
    for s in strat.get("top_signals", [])[:k]:
        t = (s.get("text") or "").strip()
        if t: out.append(t)
    return out

def derive_offer_from_signals(signals):
    # дуже простий «семантичний» підбір — без зовнішніх моделей
    text = " ".join(signals).lower()
    # ICP
    if any(w in text for w in ["фріланс", "послуг", "клієнт"]):
        icp = "- Соло-фахівці та невеликі студії, яким бракує стабільного припливу заявок"
    elif any(w in text for w in ["дан", "dataset", "research", "звіт"]):
        icp = "- Малий бізнес і творці, яким потрібні швидкі інсайти для рішень"
    else:
        icp = "- Власники невеликих онлайн-проєктів і творці цифрових продуктів"
    # Проблема/цінність
    if any(w in text for w in ["автоматизац", "скрипт", "agent", "бот"]):
        promise = "За 48 годин отримаєте чіткий план автоматизації та 1 мікро-впровадження, що економить час."
    elif any(w in text for w in ["досл", "ринок", "метрики", "перевірка"]):
        promise = "За 48 годин отримаєте діагностику пропозиції цінності та план швидкої монетизації."
    else:
        promise = "За 48 годин отримаєте короткий аудит ціннісної пропозиції й пріоритезований план дій."
    title = "Аудит/Імплементація «Монетизація за 48 годин»"
    return icp, promise, title

def populate_micro_service(exp_dir, strat):
    ddir = os.path.join(exp_dir, "deliverables")
    offer_path = os.path.join(ddir, "offer.md")
    signals = load_top_signals(strat, k=6)
    icp, promise, title = derive_offer_from_signals(signals)

    # скласти пропозицію
    offer = f"""# {title}

## Для кого (ICP)
{icp}

## Обіцянка цінності
{promise}

## Що робимо за 48 годин
- Етап 1 (0–8 год): Швидкий аудит: цілі, аудиторія (ICP), повідомлення, пропозиція цінності, перешкоди.
- Етап 2 (8–24 год): План дій + 1 мікро-впровадження (лендінг/артефакт/офер без прив'язки до платформи).
- Етап 3 (24–48 год): Мінімальний запуск, збір метрик, підсумок і наступні кроки.

## На виході отримаєте
- Короткий звіт (MD/PDF) з пріоритетами і доказами (метрики/логіка).
- 1 готовий артефакт цінності (шаблон/гайд/бріф/скрипт) у `deliverables/`.
- Чеклист впровадження на 2 тижні (20 пунктів).

## Метрики успіху (мінімум)
- ≥2 кваліфіковані ліди **або** ≥1 платний запит протягом 7 днів після впровадження.
- Бонус: CR ліди→запит ≥10% **або** явний відгук «корисно/куплю».

## Ціноутворення (чернетка)
- Пакет А: $___ (аудит + план, 48 год).
- Пакет B: $___ (плюс 1 мікро-впровадження).
- Пакет C: $___ (впровадження + супровід 2 тижні).

## Гарантія
Не корисно — безкоштовна корекція або повернення.

## Ризики/обмеження
- Не обіцяємо «чудес», працюємо з тим, що є.
- Жодних сайт-специфічних дій у коді: канали/платформи вибираються окремо й прозоро.

## Додатково
Топ-сигнали, що надихнули пропозицію:
{chr(10).join(f"- {s}" for s in signals) if signals else "- (сигнали не виявлено)"}

— Згенеровано автоматично: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    write(offer_path, offer)

def touch_result_note(exp_dir, note):
    rpath = os.path.join(exp_dir, "result.json")
    try:
        data = json.load(open(rpath,"r",encoding="utf-8"))
    except Exception:
        return
    data.setdefault("metrics", {}).setdefault("notes", []).append(note)
    if "status" in data and data["status"] == "initialized":
        data["status"] = "prepared"
    with open(rpath,"w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    strat = read_strategy(STRAT)
    sel_name = (strat or {}).get("selected", {}).get("name", "")
    exp_dir = latest_experiment_dir(EXP_ROOT)
    if not exp_dir:
        print("no experiment dir found"); return
    if "Micro-service offer" in sel_name:
        populate_micro_service(exp_dir, strat)
    else:
        # інші архетипи можна додати за аналогією
        pass
    touch_result_note(exp_dir, f"deliverables populated from strategy at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(exp_dir)

if __name__ == "__main__":
    main()
