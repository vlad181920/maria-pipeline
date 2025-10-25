#!/usr/bin/env python3
import os, sys, re, json, glob, argparse, textwrap, datetime as dt
from pathlib import Path

BASE = os.environ.get("MARIA_HOME") or os.getcwd()

def find_latest_exp():
    root = Path(BASE) / "artifacts" / "earn" / "experiments"
    if not root.exists():
        return None
    # найсвіжіша тека за mtime
    dirs = [p for p in root.iterdir() if p.is_dir()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def read_file_if_exists(p):
    try:
        return Path(p).read_text(encoding="utf-8")
    except Exception:
        return ""

def first_lines(txt, n=2):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    return lines[:n]

def extract_value_bits(onepager_txt, mini_txt):
    """Безпечний парсер: жодних інлайн-флагів (?m) і екранувань у патернах.
    Дістаємо:
      - val: перший рядок після розділу 'Обіцянка'
      - deliverable: фіксована коротка назва
      - stage_hint: до 3 рядків, що починаються з '1)'/'2)'/'3)' або '**Етап'
    """
    import re
    onepager_txt = onepager_txt or ""
    mini_txt = mini_txt or ""

    # 1) Value (обіцянка) — шукаємо заголовок 'Обіцянка' і наступний непорожній рядок
    val = ""
    def pick_value(t):
        m = re.search(r"(?im)^##?\s*Обіцянка[^\n]*\n+([^-\n].+)", t)
        return m.group(1).strip() if m else ""
    val = pick_value(onepager_txt) or pick_value(mini_txt)

    # 2) Deliverable — коротке пояснення
    deliverable = "аудит + план + 1 мікро-впровадження"

    # 3) Етапи — без регексу зі складними escape: просто лінійний перегляд
    stages = []
    for line in onepager_txt.splitlines():
        ls = line.lstrip()
        if ls.startswith("1)") or ls.startswith("2)") or ls.startswith("3)"):
            stages.append(line.strip())
    if not stages:
        for line in mini_txt.splitlines():
            ls = line.strip()
            if ls.startswith("**Етап"):
                stages.append(ls.strip("* ").strip())

    stage_hint = "; ".join(stages[:3])
    return val, deliverable, stage_hint
def make_candidates(val, deliverable):
    # Базові «будівельні блоки»
    base_promises = [
        "Короткий аудит → пріоритетний план → 1 мікро-впровадження за 48 год",
        "За 48 годин: короткий аудит, план і 1 мікро-впровадження",
        "Аудит ціннісної пропозиції + план дій за 48 годин",
        "48 годин до мінімальної монетизації: аудит, план, впровадження",
    ]
    if val:
        base_promises.append(val)

    headlines = []
    for p in base_promises:
        headlines += [
            f"Монетизація за 48 годин: {p}",
            f"{p} — прозорий результат і метрики",
            f"48 год → {deliverable}: {p.split('за 48')[0].strip()}",
            f"{p}",
        ]

    # Прибрати дублікати, почистити
    uniq = []
    seen = set()
    for h in headlines:
        hh = re.sub(r"\\s+", " ", h).strip(" —")
        if hh and hh not in seen:
            uniq.append(hh)
            seen.add(hh)
    return uniq

def lead_from(onepager_txt, mini_txt):
    # 2–3 речення, без платформ
    a = "За 48 год отримаєте короткий аудит, пріоритетний план і 1 мікро-впровадження."
    b = "Працюємо без прив'язки до платформ; рішення приймаємо на основі метрик (ліди, конверсії, дохід, час)."
    c = "Після мінімального запуску — підсумок і наступні кроки."
    # спробувати витягнути 1 речення з onepager/mini
    src = onepager_txt or mini_txt
    sline = ""
    if src:
        # беремо перші 150–220 символів важливого тексту
        body = re.sub(r"#.*|^\\s*[-*].*", "", src, flags=re.MULTILINE)
        body = re.sub(r"\\s+", " ", body).strip()
        sline = body[:180].rsplit(" ", 1)[0]
    lead = " ".join([a, b, c])
    alt = " ".join([a, sline]) if sline else lead
    leads = [lead, alt]
    # унікальні
    out, seen = [], set()
    for L in leads:
        LL = re.sub(r"\\s+", " ", L).strip()
        if LL and LL not in seen:
            out.append(LL)
            seen.add(LL)
    return out

# ——— скоринг ————————————————————————————————————————————————————————

ACTION_WORDS = {"запустіть","отримайте","створіть","зробіть","перевірте","монетизуйте","спакуйте","впровадьте","знайдіть","протестуйте"}
HYPE_WORDS = {"неймовірн","ультра","вражающ","найкращ","100%","гарантовано","wow","super"}
SPEC_TOKENS = {"аудит","план","впроваджен","чеклист","метрик"}

def score_headline(h):
    h0 = h.lower()
    # Довжина (ідеал ~50, ок зоною 30–70)
    L = len(h)
    len_score = max(0.0, 1.0 - ((L-50)/30.0)**2)  # парабола
    # Числа / конкретика
    num_score = 0.0
    if re.search(r"\\d", h): num_score += 0.10
    if "48" in h: num_score += 0.05
    # Дієслова дії
    act = sum(1 for w in ACTION_WORDS if w in h0)
    act_score = min(0.15, 0.08*act)
    # Специфічні токени
    spec = sum(1 for t in SPEC_TOKENS if t in h0)
    spec_score = min(0.15, 0.07*spec)
    # Анти-хайп
    hype = sum(1 for w in HYPE_WORDS if w in h0)
    hype_pen = min(0.2, 0.1*hype)
    # Знаки
    excl_pen = 0.2 if h.count("!") > 1 else 0.0
    comma_pen = 0.1 if h.count(",") > 3 else 0.0
    raw = len_score + num_score + act_score + spec_score - hype_pen - excl_pen - comma_pen
    return max(0.0, min(1.0, raw))

def score_lead(t):
    # Простота: середня довжина слова й слів/речення
    txt = re.sub(r"\\s+", " ", t).strip()
    sents = [s for s in re.split(r"[\\.\\!\\?]+", txt) if s.strip()]
    words = re.findall(r"[\\w\\-’ʼ]+", txt, flags=re.UNICODE)
    if not sents or not words:
        return 0.3
    wps = len(words)/len(sents)
    avg_wlen = sum(len(w) for w in words)/len(words)
    # таргет: wps<=18, avg_wlen<=6
    wps_score = max(0.0, 1.0 - max(0.0,(wps-18))/18.0)
    wlen_score = max(0.0, 1.0 - max(0.0,(avg_wlen-6))/4.0)
    return max(0.0, min(1.0, 0.5*wps_score + 0.5*wlen_score))

def combo_score(h, l):
    # 70% заголовок, 30% ліда
    return round(0.7*score_headline(h) + 0.3*score_lead(l), 3)

# ——— головна логіка ————————————————————————————————————————————————————

def main():
    ap = argparse.ArgumentParser(description="Platform-agnostic message tester (headline + lead).")
    ap.add_argument("--exp", help="Path to experiment dir", default=None)
    ap.add_argument("--n", type=int, help="Top-N to keep (default 6)", default=6)
    ap.add_argument("--apply-top", action="store_true", help="Write top selection into message_selected.md")
    ap.add_argument("--dry-run", action="store_true", help="Don't write files, print only")
    args = ap.parse_args()

    exp = Path(args.exp) if args.exp else find_latest_exp()
    if not exp or not exp.exists():
        print("No experiment found.", file=sys.stderr); sys.exit(2)

    ddir = exp / "deliverables"
    onepager = read_file_if_exists(ddir/"onepager.md")
    mini = read_file_if_exists(ddir/"mini_guide_v1.md")
    snippets_clean = read_file_if_exists(ddir/"snippets_clean.md")
    if not snippets_clean:
        snippets_clean = read_file_if_exists(ddir/"snippets.md")

    val, deliverable, stage_hint = extract_value_bits(onepager, mini)
    headlines = make_candidates(val, deliverable)

    # згенерувати ліди (використаємо і onepager/mini, і нейтральний текст)
    leads = lead_from(onepager, mini)
    if snippets_clean:
        # додамо короткі варіанти з сніпетів (лише як лід)
        for l in first_lines(snippets_clean, 2):
            if len(l.split()) >= 5:
                leads.append(l)

    # сформувати пари та оцінити
    pairs = []
    for h in headlines:
        for l in leads:
            s = combo_score(h, l)
            pairs.append({"headline": h, "lead": l, "score": s})

    # ранжування
    pairs.sort(key=lambda x: x["score"], reverse=True)
    top = pairs[:max(3, args.n)]

    # вивід у консоль
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[message_tester] {ts} exp={exp.name} candidates={len(pairs)} top={len(top)}")
    for i, p in enumerate(top, 1):
        print(f"{i}) {p['score']:.3f} — {p['headline']}")
        print("   ", textwrap.shorten(p["lead"], width=140, placeholder="…"))

    if args.dry_run:
        return

    out_dir = exp / "message_tests" / dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)

    # зберігаємо
    (out_dir/"results.json").write_text(json.dumps({
        "generated_at": ts,
        "experiment": exp.name,
        "total_candidates": len(pairs),
        "top": top
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Message candidates (platform-agnostic)", f"_Generated: {ts}_", ""]
    for i, p in enumerate(top, 1):
        md += [f"## {i}) {p['score']:.3f}",
               f"### Заголовок\n{p['headline']}",
               f"### Лід\n{p['lead']}", ""]
    (out_dir/"candidates.md").write_text("\n".join(md)+"\n", encoding="utf-8")

    if args.apply_top and top:
        sel = top[0]
        sel_md = (exp/"message_selected.md")
        sel_md.write_text(
            f"# Вибраний меседж\nЗгенеровано: {ts}\n\n## Заголовок\n{sel['headline']}\n\n## Лід\n{sel['lead']}\n",
            encoding="utf-8"
        )
        # покладемо нотатку в metrics.notes
        rj = exp/"result.json"
        try:
            data = json.loads(rj.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        notes = data.setdefault("metrics", {}).setdefault("notes", [])
        notes.append(f"message_selected: {sel['headline'][:80]}")
        rj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[apply-top] wrote {sel_md}")

if __name__ == "__main__":
    main()
