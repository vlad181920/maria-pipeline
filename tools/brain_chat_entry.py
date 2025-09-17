#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, json, traceback, datetime, importlib
from importlib.machinery import SourceFileLoader

MARIA_HOME = os.environ.get("MARIA_HOME", os.path.expanduser("~/Desktop/Марія"))
LOG_DIR = os.path.join(MARIA_HOME, "artifacts", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "brain_chat.log")

def log(line: str):
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")

def find_brain_file():
    # Кандидати шляхів за замовчуванням
    candidates = [
        os.path.join(MARIA_HOME, "maria_brain.py"),
        os.path.join(MARIA_HOME, "src", "maria_brain.py"),
        os.path.join(MARIA_HOME, "maria", "brain.py"),
        os.path.join(MARIA_HOME, "src", "maria", "brain.py"),
    ]
    # Пошук по дереву як резерв
    for root, dirs, files in os.walk(MARIA_HOME):
        if "venv" in dirs:  # пропустити venv
            dirs.remove("venv")
        if "node_modules" in dirs:
            dirs.remove("node_modules")
        if "maria_brain.py" in files:
            candidates.insert(0, os.path.join(root, "maria_brain.py"))
            break
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None

def load_brain_module():
    # Спершу спробуємо звичайний імпорт з доданим шляхом
    if MARIA_HOME not in sys.path:
        sys.path.insert(0, MARIA_HOME)
    try:
        return importlib.import_module("maria_brain")
    except Exception:
        pass
    # Якщо не вийшло — знайдемо файл і завантажимо напряму
    f = find_brain_file()
    if not f:
        raise ModuleNotFoundError("Не знайшов maria_brain.py у проєкті.")
    name = "maria_brain_autoload"
    mod = SourceFileLoader(name, f).load_module()
    return mod

def choose_reply_fn(mb):
    # 1) функції рівня модуля
    for fn_name in ("chat", "run_chat", "respond", "main"):
        if hasattr(mb, fn_name) and callable(getattr(mb, fn_name)):
            return lambda text: str(getattr(mb, fn_name)(text))
    # 2) клас MariaBrain().chat
    if hasattr(mb, "MariaBrain"):
        inst = mb.MariaBrain()
        if hasattr(inst, "chat") and callable(getattr(inst, "chat")):
            return lambda text: str(inst.chat(text))
    return None

def _read_text_from_argv_stdin(args):
    if len(args) >= 2 and args[0] == "chat":
        return " ".join(args[1:]).strip()
    data = sys.stdin.read().strip()
    return data

def main():
    try:
        args = sys.argv[1:]
        text = _read_text_from_argv_stdin(args)
        if not text:
            print("[fallback] Порожній запит.")
            return
        log(f"IN: {text}")
        try:
            mb = load_brain_module()
            fn = choose_reply_fn(mb)
            if not fn:
                reply = "[fallback] maria_brain без відомого інтерфейсу chat()."
            else:
                reply = fn(text)
        except Exception as e:
            log("ERROR load/call brain:\n" + traceback.format_exc())
            reply = "[fallback] Помилка при імпорті/виклику maria_brain (див. brain_chat.log)."
        print(reply)
        log(f"OUT: {reply}")
    except Exception:
        log("FATAL in entry:\n" + traceback.format_exc())
        print("[fallback] Критична помилка (див. brain_chat.log).")

if __name__ == "__main__":
    main()
