"""Export products from the SQLite database to data.json.

The original ``data.json`` contained only a few hard‑coded items, so the web
page displayed an incomplete catalogue.  This script reads the full product list
from ``shop.db`` (created by ``generate_db.py``) and writes a JSON file in the
format expected by the front‑end:

```json
{ "Товары": [ {"назва": "<title>", "фото": "<photo>"}, ... ] }
```

Only the title and photo fields are exported, but the script can be extended to
include additional columns if needed.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")


def export_to_json() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        # Export title and construct image filename from product code.
        # Export title, price and construct image filename from product code.
        cur = conn.execute("SELECT title, code, price FROM products")
        items = []
        for title, code, price in cur.fetchall():
            img_path = f"{code}.jpg" if code else ""
            # Format price as integer if possible, otherwise keep raw value
            price_display = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
            items.append({"назва": title, "фото": img_path, "цена": price_display})
    finally:
        conn.close()

    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(items)} products to {JSON_PATH}")


if __name__ == "__main__":
    export_to_json()
