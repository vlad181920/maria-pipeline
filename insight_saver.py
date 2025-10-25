import os, json, re
from datetime import datetime

INSIGHTS = "artifacts/lessons.jsonl"
os.makedirs("artifacts", exist_ok=True)

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_insight(source: str, title: str, text: str, tags=None):
    rec = {
        "ts": _now(),
        "source": source,
        "title": title,
        "text": text.strip(),
        "tags": tags or []
    }
    with open(INSIGHTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

def html_to_text(html: str) -> str:
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S|re.I)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S|re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def import_html(path: str, title: str = ""):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    text = html_to_text(html)
    return save_insight(source=f"html:{path}", title=title or os.path.basename(path), text=text, tags=["web"])

def import_subtitles(path: str, title: str = ""):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "-->" in line: 
                continue
            if line.strip().isdigit():
                continue
            s = line.strip()
            if s:
                lines.append(s)
    text = " ".join(lines)
    return save_insight(source=f"srt:{path}", title=title or os.path.basename(path), text=text, tags=["video"])

if __name__ == "__main__":
    pass
