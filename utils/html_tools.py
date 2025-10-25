import re
from html.parser import HTMLParser

class _Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip = 0
        self.parts = []
        self.title = ""
        self.headings = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script","style","noscript"):
            self._skip += 1
        if tag in ("br","p","div","li"):
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script","style","noscript") and self._skip>0:
            self._skip -= 1
        if tag in ("p","div"):
            self.parts.append("\n")
    def handle_data(self, data):
        if self._skip: return
        txt = data.strip()
        if not txt: return
        self.parts.append(txt+" ")
    def handle_startendtag(self, tag, attrs):
        if tag in ("br",):
            self.parts.append("\n")

def clean_html(html: str):
    # добути <title> та <h1..h3>
    title = ""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I|re.S)
    if m: title = re.sub(r"\s+"," ", m.group(1)).strip()
    heads = re.findall(r"<h([1-3])[^>]*>(.*?)</h\1>", html, flags=re.I|re.S)
    headings = [re.sub(r"<[^>]+>","", h, flags=re.S).strip() for _,h in heads]

    p = _Extractor(); p.feed(html); raw = "".join(p.parts)
    # прибрати зайві пропуски
    text = re.sub(r"[ \t]+"," ", raw)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return {"title": title or p.title or "", "headings": headings, "text": text}

def summarize(text: str, max_sentences: int = 5):
    # наївний резюме: топ довших речень без дублів
    sents = re.split(r"(?<=[\.\!\?])\s+|\n+", text)
    sents = [s.strip() for s in sents if len(s.strip())>0]
    uniq = []
    seen = set()
    for s in sorted(sents, key=lambda x: len(x), reverse=True):
        key = s.lower()
        if key in seen: continue
        seen.add(key)
        uniq.append(s)
        if len(uniq) >= max_sentences: break
    return " ".join(uniq)
