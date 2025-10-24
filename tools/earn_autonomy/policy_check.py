import os, re, json, time

BASE = os.environ.get("MARIA_HOME") or os.getcwd()
OUT  = os.path.join(BASE, "artifacts", "reports", "policy_check.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Скануємо лише активний платформо-агностичний шар
INCLUDE_DIRS = [os.path.join(BASE, "tools", "earn_autonomy")]
EXCLUDE_NAMES = {"__pycache__", ".git"}

# Дозволені (безпечні) URI/неймспейси, які не вважаємо сайт-URL
ALLOWED_URL_SUBSTR = (
    "http://www.w3.org/2000/svg",
    "http://www.w3.org/1999/xlink",
    "data:",
    "mailto:",
)

URL_RE = re.compile(r'https?://[^\s"\']+', re.I)
PLATFORM_WORDS = [
    "gumroad","redbubble","etsy","upwork","fiverr","shopify","youtube","instagram",
    "twitter","x.com","tiktok","facebook","medium","substack","patreon","kdp","amazon",
    "notion","airtable","wordpress","webflow","teachable","udemy","coursera","kaggle",
]
PLAT_RE = re.compile(r'(' + r'|'.join(re.escape(w) for w in PLATFORM_WORDS) + r')', re.I)

def should_scan_file(path: str) -> bool:
    # лише з INCLUDE_DIRS
    p = os.path.abspath(path)
    if not any(os.path.commonpath([p, d]) == d for d in INCLUDE_DIRS if os.path.exists(d)):
        return False
    # не скануємо сам перевіряльник
    if os.path.basename(p) == "policy_check.py":
        return False
    # пропускаємо службові теки/файли
    parts = set(os.path.normpath(p).split(os.sep))
    if parts & EXCLUDE_NAMES:
        return False
    return p.endswith((".py", ".sh"))

def scan_file(path):
    issues = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh, start=1):
                # URL-и
                for url in URL_RE.findall(line):
                    if any(allowed in url for allowed in ALLOWED_URL_SUBSTR):
                        continue
                    issues.append({"file": path, "line": i, "type": "url", "snippet": url})
                # Назви платформ
                m = PLAT_RE.search(line)
                if m:
                    issues.append({"file": path, "line": i, "type": "platform", "match": m.group(1), "snippet": line.strip()})
    except Exception as e:
        issues.append({"file": path, "line": 0, "type": "error", "snippet": str(e)})
    return issues

def iter_files():
    for root in INCLUDE_DIRS:
        if not os.path.exists(root):
            continue
        for r, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_NAMES]
            for f in files:
                path = os.path.join(r, f)
                if should_scan_file(path):
                    yield path

def main():
    files = list(iter_files())
    issues = []
    for f in files:
        issues.extend(scan_file(f))
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scanned_files": files,
        "issues": issues,
        "summary": {
            "files": len(files),
            "issues_total": len(issues),
            "issues_by_type": {
                "url": sum(1 for x in issues if x["type"]=="url"),
                "platform": sum(1 for x in issues if x["type"]=="platform"),
                "error": sum(1 for x in issues if x["type"]=="error"),
            },
            "pass": len(issues) == 0
        }
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(OUT)
    print("POLICY CHECK:", "PASS" if report["summary"]["pass"] else "FAIL (see report)")

if __name__ == "__main__":
    main()
