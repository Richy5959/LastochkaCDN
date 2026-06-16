"""Upload product data from data.json to Supabase.

Prerequisites:
* `pip install requests`
* Environment variables `SUPABASE_URL` and `SUPABASE_KEY` must be set.
* Table `products` should exist (run `supabase_init.sql`).

The script reads the JSON file generated earlier (contains 597 items) and
upserts each record into Supabase via the REST API.  Only the mandatory fields
are filled – additional columns (price, stock, etc.) can be added later.
"""

import os
import json
import requests

# Retrieve environment variables and strip any accidental whitespace
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL:
    SUPABASE_URL = SUPABASE_URL.strip()
if SUPABASE_KEY:
    SUPABASE_KEY = SUPABASE_KEY.strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Please set SUPABASE_URL and SUPABASE_KEY environment variables")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    # Merge on primary key (code) – existing rows will be updated
    "Prefer": "resolution=merge-duplicates",
}

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

for item in data.get("Товары", []):
    # The original JSON only contains "назва" and "фото".  We use the title as
    # the product name and also store it as the code for simplicity.
    payload = {
        "code": item.get("назва"),
        "name": item.get("назва"),
        "price": None,
        "stock": None,
        "color": None,
        "size": None,
        "type": None,
        "image_url": item.get("фото") or "",
    }
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/products", headers=headers, json=payload)
    if resp.ok:
        print(f"Uploaded: {payload['code']}")
    else:
        # Safely print error messages that may contain non‑ASCII characters
        try:
            print(f"Error uploading {payload['code']}: {resp.status_code} {resp.text}")
        except UnicodeEncodeError:
            safe_msg = f"Error uploading {payload['code']}: {resp.status_code} {resp.text}".encode('utf-8', errors='replace').decode()
            print(safe_msg)

print("Upload finished.")
