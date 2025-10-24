import os, json, time, re
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
IDEAS=os.path.join(BASE,"artifacts","gumroad","ideas.jsonl")
ROOT=os.path.join(BASE,"artifacts","gumroad")
KB=os.path.join(BASE,"artifacts","kb","index.json")
os.makedirs(ROOT, exist_ok=True)

MD_TMPL="""# {title}

## Що всередині
- 10–15 хвилин читання
- Покроковий план дій
- Чеклист для самоперевірки

## Кому корисно
- Тим, хто хоче {benefit1}
- І хто цінує {benefit2}

## Кроки
1) Підготовка — зібрати базові дані/ресурси
2) Дія — виконати мінімальний експеримент
3) Перевірка — поміряти результат за метриками

## Чеклист (20 пунктів)
{checklist}

## Додатки з бази знань
{kb_refs}

— Зроблено в проєкті «Марія» ({ts})
"""

def svg_cover(title, path):
    safe=re.sub(r'["<>]','', title)
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="800">
  <rect width="100%" height="100%" fill="#111"/>
  <rect x="40" y="40" width="1320" height="720" rx="32" fill="#222" />
  <text x="100" y="240" font-size="64" fill="#fff" font-family="Arial" font-weight="700">{safe}</text>
  <text x="100" y="320" font-size="28" fill="#ddd" font-family="Arial">Проєкт «Марія» · Гайд/пресети</text>
  <text x="100" y="700" font-size="20" fill="#bbb" font-family="Arial">{time.strftime("%Y-%m-%d")}</text>
</svg>'''
    with open(path,"w",encoding="utf-8") as f: f.write(svg)

def kb_refs_for(title):
    try:
        J=json.load(open(KB,"r",encoding="utf-8"))
        refs=[]
        for d in J.get("docs",[])[:10]:
            if title.split(":")[0].split("—")[0].strip().lower() in (d.get("title","")+d.get("preview","")).lower():
                refs.append(f"- {d.get('title') or d.get('path')} — { (d.get('preview') or '')[:120] }")
        return "\n".join(refs) or "- (буде додано при оновленні KB)"
    except: return "- (недоступно)"

def build_one(idea):
    slug=idea["slug"]; title=idea["title"]
    d=os.path.join(ROOT, slug); os.makedirs(d, exist_ok=True)
    md=os.path.join(d,"product.md"); cover=os.path.join(d,"cover.svg")
    checklist="\n".join([f"- [ ] Пункт {i}" for i in range(1,21)])
    md_text=MD_TMPL.format(
        title=title, benefit1="швидкий старт без води", benefit2="структуровані інструкції",
        checklist=checklist, kb_refs=kb_refs_for(title), ts=time.strftime("%Y-%m-%d %H:%M")
    )
    open(md,"w",encoding="utf-8").write(md_text)
    svg_cover(title, cover)
    return d

def main(n=3):
    ideas=[]
    try:
        with open(IDEAS,"r",encoding="utf-8") as f:
            for line in f:
                import json as J
                try: ideas.append(J.loads(line))
                except: pass
    except FileNotFoundError:
        return 0
    created=0
    for idea in ideas[:n]:
        d=build_one(idea); created+=1
    print(created)

if __name__=="__main__":
    main()
