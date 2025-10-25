import os, json, glob, re, time, pathlib, uuid

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EARN_DIR = os.path.join(BASE, "artifacts", "earn")
STRAT = os.path.join(EARN_DIR, "strategy.json")
SIGS  = os.path.join(EARN_DIR, "signals.jsonl")
DECISION = os.path.join(EARN_DIR, "channel_decision.json")
EXP_ROOT = os.path.join(EARN_DIR, "experiments")

CHANNELS = [
  {"id":"owned-longform",   "name":"Owned longform (гайд/звіт/стаття)"},
  {"id":"shortform-visual", "name":"Shortform visual (короткі візуальні мікро-матеріали)"},
  {"id":"market-aggregator","name":"Marketplace-like (агрегатор попиту/пропозицій)"},
  {"id":"direct-outreach",  "name":"Direct outreach (прямі звернення до ICP)"},
  {"id":"communities",      "name":"Communities/forums-like (обговорення/спільноти)"},
  {"id":"search-listing",   "name":"Search/SEO-like listing (опис/перелік/карта пошуку)"},
  {"id":"subscription",     "name":"Subscription-like (регулярні випуски/бріфи)"},
]

KW = {
  "owned-longform":   ["гайд","звіт","brief","мануал","довідник","case","дослідж"],
  "shortform-visual": ["коротк","візуал","прев'ю","обклад","картин","сніпет","шорт"],
  "market-aggregator":["замовл","ліди","попит","біржа","проєкт","замовник","виконавець"],
  "direct-outreach":  ["лист","dm","напрям","outreach","контакт","icp","пропозиція"],
  "communities":      ["спільнот","форум","обговор","відгук","питання","community"],
  "search-listing":   ["пошук","listing","каталог","порівняння","review","огляд"],
  "subscription":     ["щотиж","щоден","випуск","digest","серія","серіал","підпис"],
}

def load_strategy():
  try:
    return json.load(open(STRAT,"r",encoding="utf-8"))
  except Exception:
    return {}

def load_signals():
  out=[]
  if os.path.exists(SIGS):
    with open(SIGS,"r",encoding="utf-8") as f:
      for line in f:
        line=line.strip()
        if not line: continue
        try:
          j=json.loads(line)
          t=(j.get("text") or "").strip()
          if t: out.append(t)
        except Exception:
          pass
  strat=load_strategy()
  for s in strat.get("top_signals",[])[:8]:
    t=(s.get("text") if isinstance(s,dict) else s) or ""
    t=t.strip()
    if t: out.append(t)
  return out[:24]

def score_channels(texts):
  joined=" ".join(texts).lower()
  scores=[]
  for ch in CHANNELS:
    cid=ch["id"]; sc=0; why=[]
    for kw in KW.get(cid,[]):
      if re.search(rf"\b{re.escape(kw)}", joined):
        sc += 1; why.append(kw)
    # легкі евристики від стратегії
    if "micro-service" in joined and cid in ("direct-outreach","communities","owned-longform"):
      sc += 1; why.append("micro-service synergy")
    if "brief" in joined and cid in ("owned-longform","subscription","search-listing"):
      sc += 1; why.append("brief synergy")
    scores.append({"id":cid,"name":next(c["name"] for c in CHANNELS if c["id"]==cid),"score":sc,"why":why})
  scores.sort(key=lambda x:(x["score"]), reverse=True)
  return scores

def latest_exp():
  cands=sorted([p for p in glob.glob(os.path.join(EXP_ROOT,"*")) if os.path.isdir(p)])
  return cands[-1] if cands else None

def write(p, s):
  pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
  with open(p,"w",encoding="utf-8") as f: f.write(s)

def jdump(p, obj):
  pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
  with open(p,"w",encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def main():
  strat=load_strategy()
  texts=load_signals()
  scored=score_channels(texts)
  selected=scored[0] if scored else {"id":"owned-longform","name":"Owned longform (гайд/звіт/стаття)","score":0,"why":["default"]}

  decision={
    "id": str(uuid.uuid4()),
    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "strategy_name": (strat.get("selected",{}) or {}).get("name",""),
    "candidates": scored[:4],
    "selected": selected,
    "policy": {"site_lockin": False, "max_hours": 6, "max_cash_usd": 0},
    "note": "Абстрактний тип каналу. Жодних назв сайтів."
  }
  jdump(DECISION, decision)

  exp=latest_exp()
  if exp:
    plan=f"""# Channel plan (агностичний)
Тип каналу: **{selected['name']}**

## Гіпотеза
Цільова аудиторія (ICP) отримає цінність від цього формату та зробить мінімальну дію (лід/запит/оплата).

## Скелет дій
1) Сформулювати 1–2 меседжі під ICP та {selected['name']}.
2) Підготувати артефакт(и) цінності з `deliverables/` (без прив'язки до будь-якої платформи).
3) Доставити артефакт у канали **типу** {selected['name']} (конкретний носій Марія обирає автономно).
4) Зібрати метрики (ліди/конверсії/час/витрати) → `result.json` → `metrics_report.py`.

## Умови зупинки/масштабу
- Stop: 25% бюджету часу — жодного сигналу → переосмислити меседж/артефакт.
- Scale: ≥1 конверсія або дохід > 0 → планувати повторення/розширення.
"""
    write(os.path.join(exp,"channel_plan.md"), plan)

  print(DECISION)

if __name__=="__main__":
  main()
