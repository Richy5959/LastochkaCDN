import json
import sqlite3
import os
from pathlib import Path
import re

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def get_digits(text):
    # Оставляем только цифры
    return re.sub(r'\D', '', str(text))

def export_to_json() -> None:
    image_map = {}
    print("Индексирую файлы...")
    # Собираем карту: {число: путь}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                digits = get_digits(os.path.splitext(f)[0])
                if digits and digits not in image_map:
                    image_map[digits] = os.path.relpath(os.path.join(root, f), PROJECT_ROOT).replace("\\", "/")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT title, code, price FROM products")
    items = []
    
    for title, code, price in cur.fetchall():
        code_digits = get_digits(code)
        # Если находим точное совпадение цифр - ставим фото, иначе - пустая строка
        img_path = image_map.get(code_digits, "")
        
        price_val = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
        items.append({"назва": title, "фото": img_path, "цена": price_val})
    
    conn.close()
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Готово! data.json обновлен (только точные совпадения).")

if __name__ == "__main__":
    export_to_json()