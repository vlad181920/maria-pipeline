#!/usr/bin/env python3
import os, json, time, random, requests
from pathlib import Path

root = Path(__file__).resolve().parent.parent
artifacts = root / "artifacts" / "earn"
products_dir = artifacts / "gumroad_products"
products_dir.mkdir(parents=True, exist_ok=True)

API_TOKEN = os.environ.get("GUMROAD_TOKEN", "")
API_URL = "https://api.gumroad.com/v2/products"

if not API_TOKEN:
    print("[gumroad] ❌ Missing GUMROAD_TOKEN in environment")
    exit(1)

def gen_product_data():
    adjectives = ["Cosmic", "Digital", "Mystic", "AI", "Creative", "Smart"]
    nouns = ["Guide", "Template", "Preset", "System", "Pack", "Algorithm"]
    name = f"{random.choice(adjectives)} {random.choice(nouns)}"
    desc = f"A unique {name.lower()} created by Maria AI."
    price = random.choice([5, 9, 12, 19, 25, 29])
    file_path = products_dir / f"{name.replace(' ', '_')}.txt"
    file_path.write_text(desc, encoding="utf-8")
    return {"name": name, "description": desc, "price_cents": price * 100, "file_paths": [str(file_path)]}

def upload_product(data):
    files = [('file', open(data["file_paths"][0], 'rb'))]
    payload = {"access_token": API_TOKEN, "name": data["name"], "description": data["description"], "price_cents": data["price_cents"]}
    r = requests.post(API_URL, data=payload, files=files)
    if r.status_code == 200:
        resp = r.json()
        if resp.get("success"):
            product_id = resp["product"]["id"]
            print(f"[gumroad] ✅ Uploaded {data['name']} → id={product_id}")
            return product_id
        else:
            print(f"[gumroad] ⚠️ Error: {resp}")
    else:
        print(f"[gumroad] ❌ HTTP {r.status_code}: {r.text}")

def main():
    print("[gumroad] 🚀 Starting product upload")
    prod = gen_product_data()
    upload_product(prod)
    print("[gumroad] done")

if __name__ == "__main__":
    main()
