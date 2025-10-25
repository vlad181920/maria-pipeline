from tools.after_chat_hook import hook
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, date
import os, json, subprocess

app = FastAPI()

MARIA_HOME = os.environ.get("MARIA_HOME", os.path.expanduser("~/Desktop/Марія"))
CHAT_DIR = os.path.join(MARIA_HOME, "artifacts", "chat")
os.makedirs(CHAT_DIR, exist_ok=True)

class ChatIn(BaseModel):
    user: str

def append_jsonl(rec: dict):
    path = os.path.join(CHAT_DIR, f"dialogue_{date.today().isoformat()}.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def maria_reply(text: str) -> str:
    """
    Повертає відповідь від локального CLI Марії, якщо доступний,
    інакше дає безпечний фолбек. Таймаут захищає від зависання.
    """
    cli = os.path.expanduser("~/maria/bin/maria")
    if os.path.exists(cli) and os.access(cli, os.X_OK):
        try:
            out = subprocess.run(
                [cli, "chat", text],
                capture_output=True, text=True, timeout=20, check=False,
                env={**os.environ, "MARIA_HOME": MARIA_HOME}
            )
            body = (out.stdout or out.stderr or "").strip()
            return body if body else "[fallback] Порожня відповідь від maria CLI."
        except subprocess.TimeoutExpired:
            return "[fallback] maria CLI: таймаут 20с."
        except Exception as e:
            return f"[fallback] maria CLI error: {e}"
    return "[fallback] Я Марія. Тестовий режим. Ви сказали: " + text

@app.get("/health")
def health():
    return {"ok": True, "service": "chat_api"}

@app.post("/api/chat")
def chat(inp: ChatIn):
    try:
        _t=""
        for _k in ("text","message","q","prompt"):
            try:
                _t = locals().get(_k) or _t
            except:
                pass
        if not _t:
            try:
                _t = payload.get("text") if isinstance(payload, dict) else _t
            except:
                pass
        hook(_t)
    except:
        pass
    ts = datetime.now().isoformat(timespec="seconds")
    append_jsonl({"ts": ts, "role": "user", "text": inp.user})
    reply = maria_reply(inp.user)
    append_jsonl({"ts": ts, "role": "assistant", "text": reply})
    return {"ok": True, "ts": ts, "reply": reply}
