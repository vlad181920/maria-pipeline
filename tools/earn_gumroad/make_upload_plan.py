import os, json, glob, time
BASE=os.environ.get("MARIA_HOME") or os.getcwd()
ROOT=os.path.join(BASE,"artifacts","gumroad")
plans=[]
for d in sorted(glob.glob(os.path.join(ROOT,"*"))):
    if not os.path.isdir(d): continue
    lj=os.path.join(d,"listing.json"); md=os.path.join(d,"product.md")
    cover=os.path.join(d,"cover.svg"); zipf=os.path.join(d,"assets.zip")
    if not (os.path.exists(lj) and os.path.exists(zipf)): continue
    L=json.load(open(lj,"r",encoding="utf-8"))
    desc=open(md,"r",encoding="utf-8").read() if os.path.exists(md) else L.get("summary","")
    plans.append({
      "id": L["slug"],
      "steps":[
        {"action":"goto","url":"https://app.gumroad.com/login"},
        {"action":"login","email_env":"GUMROAD_EMAIL","password_env":"GUMROAD_PASSWORD","cookie_env":"GUMROAD_SESSION_COOKIE"},
        {"action":"goto","url":"https://app.gumroad.com/products/new"},
        {"action":"wait","ms":1200},

        # Title/Name (на новому UI поле може називатися по-різному)
        {"action":"fill_any","candidates":[
          "input[aria-label*='Title' i]",
          "input[placeholder*='Title' i]",
          "input[name=title]",
          "input[aria-label*='Name' i]",
          "input[placeholder*='Name' i]",
          "input[name=name]",
          "form input[type=text]"
        ],"value":L["title"]},

        # Price
        {"action":"fill_any","candidates":[
          "input[aria-label*='Price' i]",
          "input[placeholder*='Price' i]",
          "input[name=price]",
          "input[type=number]"
        ],"value":str(L["price_usd"])},

        # Файли (zip + cover)
        {"action":"upload_files","zip":zipf,"cover":cover},

        # Опис (contenteditable або textarea)
        {"action":"fill_desc","value":desc[:8000]},

        # Збереження (різні варіанти кнопок)
        {"action":"save_any","candidates":[
          "button:has-text('Save')",
          "text=Save changes",
          "text=Save",
          "button[type=submit]"
        ]},

        # Публікація за .env (draft/published)
        {"action":"set_visibility","mode_env":"GUMROAD_PUBLISH_MODE"}
      ]
    })
out=os.path.join(ROOT,"plans","upload_plan.json")
os.makedirs(os.path.dirname(out),exist_ok=True)
json.dump({"created_at":time.strftime("%Y-%m-%d %H:%M:%S"),"plans":plans},open(out,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(out)
