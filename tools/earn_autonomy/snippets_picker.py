#!/usr/bin/env python3
import os, re, json, sys, glob, datetime, textwrap

BASE = os.environ.get("MARIA_HOME") or os.getcwd()

def latest_exp_dir():
    paths = sorted(glob.glob(os.path.join(BASE,"artifacts/earn/experiments","*__micro-service-offer-audit-implementation")), reverse=True)
    return paths[0] if paths else None

def read(path):
    try:
        with open(path, "r", encoding="utf-8") as f: return f.read()
    except: return ""

def clean_markdown(md):
    md = re.sub(r"^#+.*$", "", md, flags=re.MULTILINE)      # прибрати заголовки
    md = re.sub(r"^\s*—\s*Згенеровано.*$", "", md, flags=re.MULTILINE)
    md = re.sub(r"^\s*Згенеровано:.*$", "", md, flags=re.MULTILINE)
    md = re.sub(r"`[^`]*`", "", md)                         # inline code
    md = re.sub(r"\*\*|\*", "", md)                         # bold/italic
    md = re.sub(r"\([^)]+\)", "", md)                       # (дужки) часті
    md = md.replace(" "," ").replace("-","-")
    lines = [re.sub(r"\s+"," ",l).strip(" -•—\t") for l in md.splitlines()]
    lines = [l for l in lines if l and not l.lower().startswith(("## ","# ","http"))]
    return "\n".join(lines)

def pick_candidates(text):
    # розбиваємо на короткі речення або буліти
    parts = []
    for line in text.splitlines():
        if re.match(r"^-?\s*\[?\]? ?", line):  # чеклист/буліти
            line = re.sub(r"^-?\s*(\[\s?\]|\[x\])?\s*", "", line)
        # розщепити на речення
        bits = re.split(r"(?<=[\.\!\?])\s+", line)
        for b in bits:
            b = b.strip(" .!-–")
            if 50 <= len(b) <= 200:
                parts.append(b)
    # легке ранжування: ключові слова на тему нашої пропозиції
    kw = ["48 год", "аудит", "план", "впроваджен", "мікро", "метрик", "лід", "конверс", "цінність"]
    def score(s): return sum(1 for k in kw if k.lower() in s.lower())
    parts = sorted(set(parts), key=lambda s: (-score(s), -len(s)))
    return parts[:3] if parts else []

def main():
    exp = None
    for i,arg in enumerate(sys.argv):
        if arg in ("--exp","-e") and i+1 < len(sys.argv):
            exp = sys.argv[i+1]
    if not exp:
        exp = latest_exp_dir()
    if not exp or not os.path.isdir(exp):
        print("No experiment dir found.", file=sys.stderr); sys.exit(2)

    ddir = os.path.join(exp,"deliverables")
    one = os.path.join(ddir,"onepager.md")
    mini = os.path.join(ddir,"mini_guide_v1.md")
    out = os.path.join(ddir,"snippets_clean.md")
    res = os.path.join(exp,"result.json")

    text = clean_markdown(read(one) + "\n" + read(mini))
    picks = pick_candidates(text)

    if not picks:
        # fallback: візьмемо 2 найдовші осмислені лінії
        lines = [l for l in text.splitlines() if len(l) > 40][:2]
        picks = lines

    header = "# Preview snippets (platform-agnostic)\n"
    body = "\n".join(f"- {p}" for p in picks)
    with open(out,"w",encoding="utf-8") as f:
        f.write(header + body + "\n")

    # позначка в result.json
    try:
        data = json.load(open(res,"r",encoding="utf-8"))
    except Exception:
        data = {"metrics":{"notes":[]}}
    notes = data.setdefault("metrics",{}).setdefault("notes",[])
    notes.append(f"snippets_clean.md generated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with open(res,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

    print("snippets_file:", out)
    for i,p in enumerate(picks,1):
        print(f"{i}) {p}")

if __name__ == "__main__":
    main()
