import os, json, time, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=os.environ.get("MARIA_HOME") or os.getcwd()
ENV_PATH=Path(BASE)/"artifacts/gumroad/.env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if line and not line.startswith("#") and "=" in line:
            k,v=line.split("=",1); os.environ.setdefault(k.strip(), v.strip())

def env(k, d=""): return os.environ.get(k, d)
def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}")

DBG = Path(BASE)/"artifacts/gumroad/debug"; DBG.mkdir(parents=True, exist_ok=True)
REPORT_PATH = Path(BASE)/"artifacts/gumroad/upload_report.json"

MAX_PER_PRODUCT = int(env("GUMROAD_MAX_SECONDS","120"))  # ліміт часу на один продукт, сек
DEFAULT_TIMEOUT  = int(env("GUMROAD_ACTION_TIMEOUT_MS","7000"))  # таймаут дії, мс

def safe_click(page, sel, timeout=DEFAULT_TIMEOUT):
    try: page.locator(sel).first.click(timeout=timeout); log(f"click: {sel}"); return True
    except Exception as e: log(f"click miss: {sel} ({e})"); return False

def wait_any(page, candidates, timeout=DEFAULT_TIMEOUT):
    start=time.time()
    while (time.time()-start)*1000 < timeout:
        for sel in candidates:
            try:
                page.locator(sel).first.wait_for(state="visible", timeout=300)
                return sel
            except: pass
    return None

def do_login(page):
    cookie = env("GUMROAD_SESSION_COOKIE","").strip()
    if cookie:
        name=cookie.split("=")[0]; value="=".join(cookie.split("=")[1:]).split(";")[0]
        page.context.add_cookies([{"name":name,"value":value,"domain":".gumroad.com","path":"/","httpOnly":True,"secure":True}])
        page.goto("https://app.gumroad.com/dashboard"); page.wait_for_load_state("networkidle"); log("login: cookie"); return
    email=env("GUMROAD_EMAIL"); pwd=env("GUMROAD_PASSWORD")
    page.goto("https://app.gumroad.com/login"); page.wait_for_load_state("domcontentloaded")
    page.fill("input[type=email]", email); page.fill("input[type=password]", pwd)
    safe_click(page, "button[type=submit]") or safe_click(page, "text=Log in") or safe_click(page,"text=Login")
    page.wait_for_load_state("networkidle"); log("login: form")

def upload_files(page, zipf, cover):
    # намагаємось знайти окремі інпути для файлів/обкладинки
    inputs = page.locator("input[type=file]")
    try: n = inputs.count()
    except: n = 0
    img_inputs=[]; any_inputs=[]
    for i in range(n):
        try:
            acc = (inputs.nth(i).get_attribute("accept") or "").lower()
            if "image" in acc: img_inputs.append(inputs.nth(i))
            else: any_inputs.append(inputs.nth(i))
        except: pass
    # основний файл
    for loc in (any_inputs or [inputs.first]):
        try: loc.set_input_files(zipf); log(f"upload asset: {zipf}"); break
        except: pass
    # обкладинка
    for loc in (img_inputs or [inputs.first]):
        try: loc.set_input_files(cover); log(f"upload cover: {cover}"); break
        except: pass

def run_plan(pw, plan_path):
    report={"started_at":time.strftime("%Y-%m-%d %H:%M:%S"), "items":[]}
    browser = pw.chromium.launch(headless=env("GUMROAD_HEADLESS","true").lower()=="true")
    context = browser.new_context()
    context.set_default_timeout(DEFAULT_TIMEOUT)
    page = context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)

    data=json.load(open(plan_path,"r",encoding="utf-8"))
    plans=data.get("plans",[])
    if not plans:
        print("No plans inside:", plan_path); context.close(); browser.close(); return report

    do_login(page)

    for p in plans:
        slug=p.get("id","unknown")
        status={"slug":slug,"ok":False,"error":None}
        started=time.time()
        try:
            for step in p.get("steps", []):
                # watchdog
                if time.time()-started > MAX_PER_PRODUCT:
                    raise TimeoutError(f"product_timeout>{MAX_PER_PRODUCT}s")

                a = (step.get("action","") or "").strip().lower()
                log(f"step: {a}")

                if a=="goto":
                    page.goto(step["url"]); page.wait_for_load_state("domcontentloaded")
                    # fallback: якщо це сторінка створення й поля не видно — спробуємо старий домен
                    if "products/new" in step["url"]:
                        page.wait_for_timeout(600)
                        if not page.locator("input, textarea, [contenteditable=true]").first.is_visible():
                            page.goto("https://gumroad.com/products/new")
                            page.wait_for_load_state("domcontentloaded"); page.wait_for_timeout(600)

                elif a=="login":
                    pass  # логін вже виконано

                elif a=="wait":
                    page.wait_for_timeout(int(step.get("ms",500)))

                elif a=="click":
                    safe_click(page, step["selector"])

                elif a=="fill":
                    try: page.fill(step["selector"], step.get("value","")); log(f"fill: {step['selector']}")
                    except Exception as e: log(f"fill miss: {step.get('selector')} ({e})")

                elif a=="fill_any":
                    cands = step.get("candidates", [])
                    val = step.get("value","")
                    sel = wait_any(page, cands, timeout=DEFAULT_TIMEOUT)
                    if sel:
                        try: page.fill(sel, val); log(f"fill_any hit: {sel}")
                        except Exception as e: log(f"fill_any miss: {sel} ({e})")
                    else:
                        log("fill_any: no candidate visible")

                elif a=="upload":
                    try: page.set_input_files(step["selector"], step["file"]); log(f"upload via {step['selector']}")
                    except Exception as e: log(f"upload miss: {e}")

                elif a=="upload_cover":
                    try: page.set_input_files("input[type=file]", step["file"]); log("upload cover generic")
                    except Exception as e: log(f"upload_cover miss: {e}")

                elif a=="upload_files":
                    upload_files(page, step.get("zip",""), step.get("cover",""))

                elif a=="fill_desc":
                    desc = step.get("value","")
                    if safe_click(page, "[contenteditable=true]"):
                        page.keyboard.type(desc)
                    else:
                        filled=False
                        for cand in ["textarea","[name=description]","#description","[data-testid*='description' i]"]:
                            try: page.fill(cand, desc); log(f"desc via {cand}"); filled=True; break
                            except: pass
                        if not filled: log("WARN: description not filled")

                elif a=="save":
                    safe_click(page, step["selector"])

                elif a=="save_any":
                    hit=False
                    for cand in step.get("candidates", []):
                        if safe_click(page, cand):
                            hit=True; break
                    if not hit: log("save_any: no candidate clicked")

                elif a=="set_visibility":
                    mode = env(step.get("mode_env","GUMROAD_PUBLISH_MODE"), "draft").lower()
                    if mode=="published":
                        safe_click(page, "text=Publish")

                else:
                    log(f"skip unknown action: {a}")

            status["ok"]=True
            log(f"Done: {slug}")

        except Exception as e:
            html_path = DBG/f"{slug}_fail.html"; png_path  = DBG/f"{slug}_fail.png"
            try: Path(html_path).write_text(page.content(), encoding="utf-8")
            except: pass
            try: page.screenshot(path=str(png_path))
            except: pass
            status["error"]=str(e); log(f"FAIL {slug}: {e}")

        report["items"].append(status)

    context.close(); browser.close()
    report["finished_at"]=time.strftime("%Y-%m-%d %H:%M:%S")
    Path(REPORT_PATH).write_text(json.dumps(report,ensure_ascii=False,indent=2), encoding="utf-8")
    print(str(REPORT_PATH))
    return report

if __name__=="__main__":
    plan = Path(BASE)/"artifacts/gumroad/plans/upload_plan.json"
    if not plan.exists():
        print("No plan found:", plan); sys.exit(1)
    with sync_playwright() as pw:
        run_plan(pw, str(plan))
