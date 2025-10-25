import os, sys, json, urllib.request, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from insight_saver import save_insight
from utils.html_tools import clean_html, summarize

PORT = int(os.environ.get("WEB_LEARN_PORT") or (sys.argv[1] if len(sys.argv)>1 else 8765))
LOG_DIR = "artifacts/logs"
DATA_DIR = "data"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
ACCESS_LOG = os.path.join(LOG_DIR, "web_learn_access.log")

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def log(rec):
    rec["ts"] = now()
    with open(ACCESS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False)+"\n")

def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent":"MariaLearn/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="ignore")

class H(BaseHTTPRequestHandler):
    def _send_json(self, code, obj):
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))
    def _path(self):
        p = urllib.parse.urlparse(self.path).path
        return (p or "/").rstrip("/") or "/"
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(parsed.query or "")
        p = self._path()
        log({"m":"GET","path":p,"q":q})
        if p in ("/", "/status"):
            lessons = os.path.exists("artifacts/lessons.jsonl")
            size = os.path.getsize("artifacts/lessons.jsonl") if lessons else 0
            return self._send_json(200, {"ok": True, "time": now(), "lessons_file": lessons, "lessons_size": size, "clean_mode": True})
        if p == "/learn":
            url = (q.get("url") or [None])[0]
            title = (q.get("title") or [None])[0] or url
            if not url: return self._send_json(400, {"ok": False, "err": "url required"})
            try: html = fetch_html(url)
            except Exception as e: return self._send_json(502, {"ok": False, "err": str(e)})
            C = clean_html(html)
            final_text = (C["title"]+"\n\n"+("\n".join(C["headings"]))+"\n\n"+C["text"]).strip() or html
            rec = save_insight(source=f"url:{url}", title=title or (C["title"] or url), text=final_text, tags=["web","clean"])
            return self._send_json(200, {"ok": True, "saved": rec})
        return self._send_json(404, {"ok": False, "err": "not found"})
    def do_POST(self):
        p = self._path()
        l = int(self.headers.get("Content-Length","0"))
        raw = self.rfile.read(l).decode("utf-8") if l>0 else "{}"
        try: body = json.loads(raw or "{}")
        except: return self._send_json(400, {"ok": False, "err": "invalid json"})
        log({"m":"POST","path":p,"keys":list(body.keys())})
        if p == "/learn":
            url = body.get("url"); title = body.get("title") or url
            if not url: return self._send_json(400, {"ok": False, "err": "url required"})
            try: html = fetch_html(url)
            except Exception as e: return self._send_json(502, {"ok": False, "err": str(e)})
            C = clean_html(html)
            final_text = (C["title"]+"\n\n"+("\n".join(C["headings"]))+"\n\n"+C["text"]).strip() or html
            rec = save_insight(source=f"url:{url}", title=title or (C["title"] or url), text=final_text, tags=["web","clean"])
            return self._send_json(200, {"ok": True, "saved": rec})
        if p == "/subtitles":
            text = (body.get("text") or "").strip()
            title = body.get("title") or "Subtitles"
            if not text: return self._send_json(400, {"ok": False, "err": "text required"})
            rec = save_insight(source="api:subtitles", title=title, text=text, tags=["video"])
            return self._send_json(200, {"ok": True, "saved": rec})
        return self._send_json(404, {"ok": False, "err": "not found"})

if __name__ == "__main__":
    srv = HTTPServer(("127.0.0.1", PORT), H)
    print(f"[web_learn] http://127.0.0.1:{PORT}")
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
