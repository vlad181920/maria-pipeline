import os, re, json, time, math, statistics, uuid, glob

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
SIGNALS = os.path.join(BASE, "artifacts", "earn", "signals.jsonl")
OUT = os.path.join(BASE, "artifacts", "earn", "strategy.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# --- Абстрактні архетипи каналів (жодної згадки сайтів) ---
ARCHETYPES = [
    {
        "name": "Digital micro-asset (guide/preset/checklist)",
        "keywords": [r"цифров", r"гайд", r"шаблон", r"пресет", r"чеклист", r"template", r"preset", r"guide", r"ebook"],
        "hours": 4,          # базова оцінка часу
        "cash_usd": 0,       # прямі витрати (мін.)
        "payoff_usd": 9,     # середній брутто-дохід за спробу
        "risks": ["низький середній чек", "конкуренція в інформаційних товарах"],
        "metrics": ["CTR пропозиції", "CR у покупку", "ARPU", "відгуки/повтори"],
    },
    {
        "name": "Micro-service offer (audit/implementation)",
        "keywords": [r"послуг", r"фр[іи]ланс", r"аудит", r"консультац"],
        "hours": 6,
        "cash_usd": 0,
        "payoff_usd": 50,
        "risks": ["залежність від людського часу", "непредиктивний попит"],
        "metrics": ["кількість лідів", "CR лід→проєкт", "середній чек", "час на доставку"],
    },
    {
        "name": "Automation micro-tool (agent/script)",
        "keywords": [r"автоматизац", r"скрипт", r"інструмент", r"бот", r"agent"],
        "hours": 8,
        "cash_usd": 0,
        "payoff_usd": 25,
        "risks": ["підтримка інструменту", "сумісність середовищ"],
        "metrics": ["активації", "щоденні користувачі", "конверсія в оплату/донат"],
    },
    {
        "name": "Data/Research brief (dataset/insight report)",
        "keywords": [r"дан[іи]", r"досл[іи]дж", r"зв[іi]т", r"research", r"dataset"],
        "hours": 5,
        "cash_usd": 0,
        "payoff_usd": 19,
        "risks": ["перевірка якості даних", "оновлення та релевантність"],
        "metrics": ["завантаження", "CR у покупку", "відгуки/цитування"],
    },
    {
        "name": "Subscription mini (curation/updates)",
        "keywords": [r"п[іi]дписк", r"оновлен", r"дайджест", r"newsletter"],
        "hours": 6,
        "cash_usd": 0,
        "payoff_usd": 5,  # перший місяць середній
        "risks": ["churn", "постійний обов'язок контенту"],
        "metrics": ["нові підписки", "активність", "retention (M1/M2)"],
    },
    {
        "name": "Affiliate/comparison brief",
        "keywords": [r"афф[іi]л[іi]ат", r"партнер", r"рефераль", r"пор[іi]внян"],
        "hours": 4,
        "cash_usd": 0,
        "payoff_usd": 10,
        "risks": ["залежність від зовнішніх правил", "низькі ставки у нішах"],
        "metrics": ["кліки", "CR у реф. подію", "комісії"],
    },
]

# --- Завантаження сигналів ---
def load_signals(path):
    sigs=[]
    if not os.path.exists(path):
        return sigs
    with open(path,"r",encoding="utf-8") as f:
        for ln in f:
            ln=ln.strip()
            if not ln: continue
            try:
                j=json.loads(ln)
                sigs.append(j)
            except:
                pass
    return sigs

# --- Оцінка релевантності сигналів до архетипу ---
def relevance_score(text, patterns):
    if not text: return 0.0
    score=0.0
    for p in patterns:
        if re.search(p, text, flags=re.I|re.U):
            score += 1.0
    return score

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def pick_top_signals(signals, k=12):
    # пріоритет: type in ['hypothesis','trend'] > 'weak', далі weight
    def key(s):
        t = s.get("type","")
        base = 2 if t in ("hypothesis","trend") else 1
        return (base, float(s.get("weight",0.0)))
    return sorted(signals, key=key, reverse=True)[:k]

def compute_candidates(signals):
    texts = [(s.get("text") or "") for s in signals]
    weights = [float(s.get("weight",0.0)) for s in signals]
    avg_w = statistics.mean(weights) if weights else 0.3

    cands=[]
    for arch in ARCHETYPES:
        rel=0.0
        for t in texts:
            rel += relevance_score(t, arch["keywords"])
        # нормалізуємо релевантність
        rel_norm = rel / (len(texts) or 1)
        # ймовірність успіху як функція релевантності та середньої ваги сигналів
        p_succ = clamp(0.10 + 0.35*rel_norm + 0.25*avg_w, 0.05, 0.85)
        payoff = arch["payoff_usd"]
        cost_cash = arch["cash_usd"]
        # оцінимо час у $-еквіваленті (умовна ставка $8/год)
        cost_time_usd = arch["hours"] * 8
        risk_penalty = (1.0 - p_succ) * 2  # умовний ризик у $
        ev = p_succ * payoff - cost_cash - cost_time_usd*0.1 - risk_penalty

        cands.append({
            "id": str(uuid.uuid4()),
            "name": arch["name"],
            "p_success": round(p_succ,3),
            "est_payoff_usd": payoff,
            "est_cost_cash_usd": cost_cash,
            "est_hours": arch["hours"],
            "ev_usd": round(ev,2),
            "why": f"релевантність={round(rel_norm,3)}, середня вага сигналів={round(avg_w,3)}",
            "risks": arch["risks"],
            "metrics": arch["metrics"],
        })
    # сортуємо за очікуваною цінністю
    cands.sort(key=lambda x: x["ev_usd"], reverse=True)
    return cands

def assemble_first_experiment(best):
    # повністю платформо-агностичний експеримент
    name = best["name"]
    if "Digital micro-asset" in name:
        objective = "Створити мінімальний цифровий актив (1 гайд/набір пресетів) і отримати ≥1 підтвердження цінності."
        deliverable = "ZIP з активом + короткий опис (md) + обкладинка (svg)"
        time_h = min(4, best["est_hours"])
        cash = 0
        success = "≥1 продаж/заявка/відгук або ≥10% CR на демо-інтерес"
    elif "Micro-service" in name:
        objective = "Запакувати мікропослугу (аудит/імплементація) і отримати ≥1 платний запит."
        deliverable = "Опис послуги (md) + 2 кейси/демо + шаблон результату"
        time_h = min(6, best["est_hours"])
        cash = 0
        success = "≥1 платний клієнт або ≥2 кваліфікованих ліди"
    elif "Automation" in name:
        objective = "Зробити мінімальний інструмент/скрипт, що економить час, і зібрати ≥5 активних користувачів."
        deliverable = "CLI/скрипт + README + приклад використання"
        time_h = min(8, best["est_hours"])
        cash = 0
        success = "≥5 DAU або ≥1 платіж/донат"
    elif "Data/Research" in name:
        objective = "Зібрати короткий data-бріф/набір із перевірених джерел і отримати ≥1 монетизацію."
        deliverable = "PDF/MD звіт + CSV/JSON з даними"
        time_h = min(5, best["est_hours"])
        cash = 0
        success = "≥1 продаж або ≥2 запити на розширену версію"
    elif "Subscription" in name:
        objective = "Запустити MVP підписки (1 випуск) і отримати ≥3 підписки/намірів."
        deliverable = "Випуск №1 (md/pdf) + план контенту на 4 тижні"
        time_h = min(6, best["est_hours"])
        cash = 0
        success = "≥3 платні підписки або ≥10 підтверджених інтересів"
    else:  # Affiliate/comparison
        objective = "Підготувати порівняльний бріф з чіткими рекомендаціями і отримати ≥20 цільових кліків."
        deliverable = "MD-бріф + таблиця критеріїв"
        time_h = min(4, best["est_hours"])
        cash = 0
        success = "≥20 цільових кліків або ≥1 комісія"

    return {
        "objective": objective,
        "deliverable": deliverable,
        "budget": {"time_h": time_h, "cash_usd": cash},
        "success_criteria": success,
        "policy": {
            "no_site_lockin": True,
            "max_hours": time_h,
            "max_cash_usd": cash,
        }
    }

def main():
    signals = load_signals(SIGNALS)
    # якщо сигналів немає — зробимо нейтральні заглушки з нульовою вагою
    if not signals:
        signals = [
            {"type":"weak","text":"CHAT: базовий попит на цифрові продукти","weight":0.2},
            {"type":"hypothesis","text":"THOUGHT: автоматизація економить час користувачів","weight":0.4},
            {"type":"trend","text":"KB: запит на структурування знань","weight":0.3},
        ]

    top_signals = pick_top_signals(signals, k=12)
    candidates = compute_candidates(top_signals)
    best = candidates[0]

    strategy = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "signals_used": len(top_signals),
        "top_signals": top_signals,
        "candidate_strategies": candidates,
        "selected": {
            "name": best["name"],
            "ev_usd": best["ev_usd"],
            "p_success": best["p_success"],
            "est_hours": best["est_hours"],
            "est_payoff_usd": best["est_payoff_usd"],
            "risks": best["risks"],
            "metrics": best["metrics"],
            "first_experiment": assemble_first_experiment(best),
        }
    }

    with open(OUT,"w",encoding="utf-8") as f:
        json.dump(strategy, f, ensure_ascii=False, indent=2)

    print(OUT)

if __name__ == "__main__":
    main()
