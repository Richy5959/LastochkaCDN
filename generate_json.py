import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def export_to_json() -> None:
    image_map = {}
    print("Индексирую файлы с учетом префиксов...")
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Берем полное имя без расширения как ключ (например, 'A20' или '20')
                name = os.path.splitext(f)[0].lower()
                image_map[name] = os.path.relpath(os.path.join(root, f), PROJECT_ROOT).replace("\\", "/")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT title, code, price FROM products")
    items = []
    
    for title, code, price in cur.fetchall():
        # Пытаемся найти точное совпадение
        code_str = str(code).lower()
        
        # Сначала ищем код как есть (например, 'а20')
        # Если не нашли, ищем просто цифры (на случай, если файл называется '20')
        img_path = image_map.get(code_str, image_map.get(code_str.lstrip('атьскбдн'), ""))
            
        price_val = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
        items.append({"назва": title, "фото": img_path, "цена": price_val})
    
    conn.close()
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Готово! Теперь привязка идет по полному коду.")

if __name__ == "__main__":
    export_to_json()