import os, json, time, uuid, re, hashlib, glob

BASE = os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
KB = os.path.join(BASE, "artifacts", "kb", "index.json")
THOUGHTS = os.path.join(BASE, "artifacts", "thoughts", "audit_queue.jsonl")
OUT = os.path.join(BASE, "artifacts", "earn", "signals.jsonl")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Мінімальні нейтральні "гачки" для заробітку (без прив'язки до платформ)
HOOKS = [
    r"\bринок", r"\bпопит", r"\bпродаж", r"\bмонетизац", r"\bклієнт",
    r"\bцифров(ий|і|і продукти)", r"\bшаблон", r"\bпресет", r"\bгайд",
    r"\bфриланс|\bфріланс", r"\bпослуги", r"\bмаркетплейс", r"\bплатформ",
    r"\bпідписка", r"\bаффіліат|\bпартнерськ", r"\bліди", r"\bконверс",
    r"\bексперимент", r"\bціноутвор"
]
HOOK = re.compile("|".join(HOOKS), flags=re.I|re.U)

def digest(txt): 
    return hashlib.sha1((txt or "").encode("utf-8","ignore")).hexdigest()[:16]

def kb_docs():
    try:
        J = json.load(open(KB,"r",encoding="utf-8"))
        for d in J.get("docs",[]):
            yield {
                "title": (d.get("title") or d.get("path") or "").strip(),
                "preview": (d.get("preview") or "").strip(),
                "path": d.get("path","")
            }
    except FileNotFoundError:
        return

def last_chat_lines(n=300):
    # беремо останній діалог, якщо є
    files = sorted(glob.glob(os.path.join(BASE,"artifacts","chat","dialogue_*.jsonl")))
    if not files: return []
    lines=[]
    with open(files[-1],"r",encoding="utf-8") as f:
        for line in f:
            lines.append(line.strip())
    return lines[-n:]

def add_signal(f, sigtype, text, weight, meta=None):
    obj = {
        "id": str(uuid.uuid4()),
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": sigtype,                  # 'trend' | 'product' | 'platform?'
        "text": text.strip(),
        "weight": round(float(weight), 3),
        "digest": digest(sigtype+"|"+text),
        "meta": meta or {}
    }
    f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return obj

def main():
    seen = set()
    created = 0
    with open(OUT,"a",encoding="utf-8") as out:
        # 1) KB → трендові/продуктові сигнали (зовсім загальні)
        for d in kb_docs():
            blob = f"{d['title']} — {d['preview']}"
            if not blob.strip(): continue
            m = HOOK.search(blob)
            w = 0.6 if m else 0.2
            sig = f"KB: {d['title']}"
            dg = digest("trend|"+sig)
            if dg in seen: continue
            add_signal(out, "trend", sig, w, {"path": d.get("path","")})
            seen.add(dg); created += 1

        # 2) Думки → гіпотези про напрямок (без підказок що саме робити)
        try:
            with open(THOUGHTS,"r",encoding="utf-8") as f:
                for line in f:
                    j = None
                    try: j = json.loads(line)
                    except: continue
                    topic = (j.get("topic") or "").strip()
                    if not topic: continue
                    # якщо тема містить гачки — це слабкий сигнал на «можливий шлях»
                    w = 0.7 if HOOK.search(topic) else 0.4
                    sig = f"THOUGHT: {topic}"
                    dg = digest("hypothesis|"+sig)
                    if dg in seen: continue
                    add_signal(out, "hypothesis", sig, w, {"source_type": j.get("type","")})
                    seen.add(dg); created += 1
        except FileNotFoundError:
            pass

        # 3) Останні фрази з чату → додаткові слабкі сигнали
        for ln in last_chat_lines(200):
            if not ln: continue
            try:
                j = json.loads(ln)
                role = j.get("role") or j.get("who") or ""
                text = j.get("text") or j.get("content") or ""
            except:
                role=""; text=ln
            if not text.strip(): continue
            w = 0.5 if HOOK.search(text) else 0.2
            sig = f"CHAT({role}): {text[:160]}"
            dg = digest("chat|"+sig)
            if dg in seen: continue
            add_signal(out, "weak", sig, w, {})
            seen.add(dg); created += 1

    print(created)

if __name__ == "__main__":
    main()
