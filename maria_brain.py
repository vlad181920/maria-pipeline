import os, json, datetime, re

MARIA_HOME = os.environ.get("MARIA_HOME", os.path.expanduser("~/Desktop/Марія"))
INSIGHTS_DIR = os.path.join(MARIA_HOME, "artifacts", "insights")
PROJECT_MANIFEST = os.path.join(MARIA_HOME, "project_manifest.md")
QUEUE_FILE = os.path.join(MARIA_HOME, "artifacts", "thoughts", "queue.jsonl")
LOG_FILE = os.path.join(MARIA_HOME, "artifacts", "logs", "brain_core.log")

def _now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _log(event, **kw):
    rec = {"ts": _now(), "event": event}
    rec.update(kw)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def _append_jsonl(path, rec):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def _norm_query(q):
    return q.strip().lower()

def _advice_with_or_without_kb(kb_text):
    if kb_text:
        return "Використай знайдені нотатки для уточнення."
    return "Зроби 1 запис у маніфесті про наступний мінімальний крок."

def _auto_insight_stub(text):
    safe = re.sub(r"[^a-zA-Z0-9а-яА-ЯіїєґІЇЄҐ_-]+", "-", text)[:40].strip("-")
    fn = f"stub_{safe}.md"
    path = os.path.join(INSIGHTS_DIR, fn)
    os.makedirs(INSIGHTS_DIR, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"**[Правило]** Чернетка для теми: {text}\n")
    return path

def _collect_knowledge():
    results = []
    if os.path.exists(INSIGHTS_DIR):
        for fn in os.listdir(INSIGHTS_DIR):
            if fn.endswith(".md"):
                path = os.path.join(INSIGHTS_DIR, fn)
                try:
                    t = open(path, "r", encoding="utf-8").read()
                    if t.strip():
                        results.append((path, t))
                except:
                    pass
    try:
        if os.path.exists(PROJECT_MANIFEST):
            t = open(PROJECT_MANIFEST, "r", encoding="utf-8").read()
            if t.strip():
                results.append((PROJECT_MANIFEST, t))
    except:
        pass
    return results

def chat(text):
    base = f"Марія: почула — {text}"
    plan = "Крок 1: зафіксувати запит і перевірити наявні нотатки/інсайти. Крок 2: поставити 1–2 уточнюючі питання й зафіксувати відповіді в інсайтах."
    parap = f"Ти питаєш: «{text.strip()}»."

    kb_entries = _collect_knowledge()
    if kb_entries:
        src, insight_text = kb_entries[0]
        advice = _advice_with_or_without_kb(insight_text)
        _log("quality", tags=["has_plan", "has_paraphrase", "has_advice", "has_kb"])
        reply = (
            f"{base}\n"
            f"План: {plan}\n"
            f"{parap}\n"
            f"Порада: {advice}\n"
            f"Довідка (із нотаток): {insight_text[:220]}{'…' if len(insight_text)>220 else ''}"
        )
        try:
            first = ""
            txt = (insight_text or "").strip()
            if txt:
                first = txt.splitlines()[0]
                first = first.replace("**[Правило]**", "").strip(" -–•").strip()
            if first:
                reply = reply + "\nNext step: " + first
        except Exception:
            pass
        _log("kb_used", source=src)
        _log("chat_out", reply=reply)
        return reply
    else:
        advice = _advice_with_or_without_kb(None)
        _log("quality", tags=["has_plan", "has_paraphrase", "has_advice"])
        reply = (
            f"{base}\n"
            f"План: {plan}\n"
            f"{parap}\n"
            f"Порада: {advice}"
        )
        stub = _auto_insight_stub(text)
        _log("kb_empty", stub=stub)
        _log("chat_out", reply=reply)
        return reply

if __name__ == "__main__":
    demo_qs = [
        "де фіксувати зміни по маніфесту?",
        "як вести журнал змін?",
        "куди писати нотатки по плану?",
        "будь-що нове без знань abc-xyz"
    ]
    for q in demo_qs:
        print("\n---")
        print(chat(q))
