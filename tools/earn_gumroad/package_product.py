import os, json, time, zipfile
BASE=os.environ.get("MARIA_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
ROOT=os.path.join(BASE,"artifacts","gumroad")
def package_one(slug, price=7):
    d=os.path.join(ROOT, slug)
    md=os.path.join(d,"product.md")
    cover=os.path.join(d,"cover.svg")
    if not os.path.exists(md): return 0
    zpath=os.path.join(d,"assets.zip")
    with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(md, "README.md")
        # додатково вкладемо ліцензію
        lic_path=os.path.join(d,"LICENSE.txt")
        open(lic_path,"w",encoding="utf-8").write("MIT-like: особисте використання дозволено.")
        z.write(lic_path,"LICENSE.txt")
    listing={
        "title": open(md,"r",encoding="utf-8").read().splitlines()[0].lstrip("# ").strip(),
        "slug": slug,
        "summary": "Короткий практичний гайд/набір шаблонів.",
        "price_usd": price,
        "files": {
            "assets_zip": zpath,
            "cover_svg": cover
        },
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(d,"listing.json"),"w",encoding="utf-8") as f:
        json.dump(listing,f,ensure_ascii=False,indent=2)
    return 1

def main():
    created=0
    for slug in sorted(os.listdir(ROOT)):
        d=os.path.join(ROOT,slug)
        if not os.path.isdir(d): continue
        created+=package_one(slug)
    print(created)

if __name__=="__main__":
    main()
