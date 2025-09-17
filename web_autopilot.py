import os, re, sys, time, json, urllib.parse, urllib.request
from html.parser import HTMLParser
from datetime import datetime
from insight_saver import import_html, save_insight

CRAWL_DIR = "data/crawled"
os.makedirs(CRAWL_DIR, exist_ok=True)

class LinkParser(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.links = set()
        self.base = base
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a": return
        href = dict(attrs).get("href")
        if not href: return
        url = urllib.parse.urljoin(self.base, href)
        self.links.add(url)

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent":"MariaBot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    return data.decode("utf-8", errors="ignore")

def same_domain(u1, u2):
    return urllib.parse.urlparse(u1).netloc == urllib.parse.urlparse(u2).netloc

def save_page(url, html):
    ts = int(time.time())
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", urllib.parse.urlparse(url).path.strip("/") or "index")
    fname = f"{ts}_{safe[:60]}.html"
    path = os.path.join(CRAWL_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path

def crawl(seed_url: str, max_pages: int = 8, max_depth: int = 1):
    seen = set()
    queue = [(seed_url, 0)]
    imported = []
    while queue and len(seen) < max_pages:
        url, d = queue.pop(0)
        if url in seen: continue
        seen.add(url)
        try:
            html = fetch(url)
        except Exception as e:
            continue
        path = save_page(url, html)
        rec = import_html(path, title=url)
        imported.append(rec)
        if d < max_depth:
            p = LinkParser(url); p.feed(html)
            for nxt in p.links:
                if nxt.startswith("mailto:"): continue
                if not nxt.startswith(("http://","https://")): continue
                if not same_domain(seed_url, nxt): continue
                if nxt not in seen:
                    queue.append((nxt, d+1))
    return {"seed": seed_url, "pages": len(seen), "imported": len(imported)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 web_autopilot.py <seed_url> [max_pages=8] [max_depth=1]")
        sys.exit(1)
    seed = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    out = crawl(seed, max_pages, max_depth)
    print(json.dumps(out, ensure_ascii=False))
