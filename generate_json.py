import json
import sqlite3
import os
from pathlib import Path
import re

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def get_digits(text):
    return re.sub(r'\D', '', str(text))

def export_to_json() -> None:
    image_map = {}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                digits = get_digits(os.path.splitext(f)[0])
                if digits and digits not in image_map:
                    image_map[digits] = os.path.relpath(os.path.join(root, f), PROJECT_ROOT).replace("\\", "/")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT title, code, price FROM products")
    items = []
    
    missing_items = []
    for title, code, price in cur.fetchall():
        code_digits = get_digits(code)
        img_path = image_map.get(code_digits, "")
        
        if not img_path:
            missing_items.append(f"{title} (код: {code})")
            
        price_val = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
        items.append({"назва": title, "фото": img_path, "цена": price_val})
    
    conn.close()
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"Готово! Найдено: {len(items) - len(missing_items)} из {len(items)}")
    if missing_items:
        print("\nСписок товаров без фото (проверь, есть ли для них файлы):")
        for item in missing_items:
            print(f"- {item}")

if __name__ == "__main__":
    export_to_json()ы