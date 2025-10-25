import os, json, re, glob

TODO = "artifacts/todo_week_2025-09-02.md"
LESSONS = "artifacts/lessons.jsonl"
BACKLOG = "artifacts/goals/backlog.jsonl"
ATTEMPTS = "artifacts/goals/attempts.jsonl"
PARKING = "artifacts/goals/parking.jsonl"
WEEKLY = "artifacts/reports"
STATE = "artifacts/self/state.jsonl"
UPGRADE_REPORTS = "artifacts/reports/self_upgrade_explanations"

def has_lines(path, n=1):
    if not os.path.exists(path): return False
    try:
        with open(path,"r",encoding="utf-8") as f:
            for i,_ in enumerate(f,1):
                if i>=n: return True
    except: pass
    return False

def lessons_have_tag(tag):
    if not os.path.exists(LESSONS): return False
    try:
        with open(LESSONS,"r",encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line: continue
                try:
                    rec=json.loads(line)
                except:
                    continue
                if tag in (rec.get("tags") or []):
                    return True
    except:
        return False
    return False

def backlog_prioritized():
    if not os.path.exists(BACKLOG): return False
    try:
        with open(BACKLOG,"r",encoding="utf-8") as f:
            for line in f:
                if '"_weight":' in line:
                    return True
    except:
        return False
    return False

def weekly_report_exists():
    return bool(glob.glob(os.path.join(WEEKLY, "weekly_goals_*.md")))

def any_failed_goals():
    return os.path.exists(ATTEMPTS) or has_lines(PARKING, 1)

def have_upgrade_reports():
    if not os.path.isdir(UPGRADE_REPORTS): return False
    return any(True for _ in os.scandir(UPGRADE_REPORTS))

def mark(text, needle):
    pattern = rf"- \[ \] {re.escape(needle)}"
    repl    = f"- [x] {needle}"
    return re.sub(pattern, repl, text)

def tick():
    if not os.path.exists(TODO): return {"ok":False,"err":"todo file not found"}
    with open(TODO,"r",encoding="utf-8") as f:
        content = f.read()

    if os.path.exists("inner_dialogue.py"):
        content = mark(content, "Додати **внутрішній монолог / дебати** між думками (`inner_dialogue.py`)")

    if has_lines("artifacts/metrics/thoughts.jsonl", 1):
        content = mark(content, "Впровадити **оцінку ефективності думок** (зберігати метрики)")

    if has_lines("artifacts/goals/backlog.jsonl", 1):
        content = mark(content, "Запускати **нові цілі з думок**, які пройшли оцінку (зв’язати з `goal_planner.py`)")

    if has_lines("artifacts/logs/pipeline.log", 1):
        content = mark(content, "Зробити цикл «думка → емоція → дія → рефлексія → нова думка» без розривів")

    if has_lines(LESSONS, 1):
        content = mark(content, "Зберігати уроки у `artifacts/lessons.jsonl`")

    if lessons_have_tag("web"):
        content = mark(content, "Додати парсер для **веб-статей** (HTML → знання, інтегрувати в `insight_saver.py`)")

    if lessons_have_tag("video"):
        content = mark(content, "Зробити конвертер для **YouTube / відео** (субтитри → інсайт)")

    if backlog_prioritized():
        content = mark(content, "Реалізувати **пріоритезацію цілей** (важливість + ресурси)")

    if weekly_report_exists():
        content = mark(content, "Додати звіт `weekly_goals_report.py` (які цілі досягнуті, які ні)")

    if any_failed_goals():
        content = mark(content, "Автоматично відкидати **неефективні цілі** після кількох невдач")

    if os.path.exists("self_monitor.py"):
        content = mark(content, "Зробити `self_monitor.py` (моніторинг кількості думок, емоцій, успішності дій)")

    if has_lines(STATE, 1):
        content = mark(content, "Лог у `artifacts/self/state.jsonl`: короткий запис «як почувається Марія»")

    if have_upgrade_reports():
        content = mark(content, "Розширити **self_upgrader.py**, щоб пояснював свої зміни")

    with open(TODO,"w",encoding="utf-8") as f:
        f.write(content)
    return {"ok":True}

if __name__=="__main__":
    print(json.dumps(tick(), ensure_ascii=False))
