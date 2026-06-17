import json
import sqlite3
import os
from pathlib import Path
import re

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def get_digits(text):
    """Оставляет в строке только цифры (А20 -> 20, 351_0 -> 351)"""
    return re.sub(r'\D', '', str(text))

def export_to_json() -> None:
    # 1. Создаем карту {число: путь_к_файлу}
    image_map = {}
    print("Индексирую файлы...")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Получаем только цифры из имени файла
                digits = get_digits(os.path.splitext(f)[0])
                if digits and digits not in image_map:
                    image_map[digits] = os.path.relpath(os.path.join(root, f), PROJECT_ROOT).replace("\\", "/")
    
    # 2. Связываем
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT title, code, price FROM products")
    items = []
    
    found = 0
    for title, code, price in cur.fetchall():
        # Получаем только цифры из кода товара
        code_digits = get_digits(code)
        img_path = image_map.get(code_digits, "")
        
        if img_path: found += 1
            
        price_val = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
        items.append({"назва": title, "фото": img_path, "цена": price_val})
    
    conn.close()
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово! Найдено соответствий: {found} из {len(items)}")

if __name__ == "__main__":
    export_to_json()