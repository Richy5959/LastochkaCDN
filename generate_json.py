import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def export_to_json() -> None:
    # Создаем карту: {имя_файла_без_расширения: полный_путь}
    image_map = {}
    print("Индексирую файлы...")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                name = os.path.splitext(f)[0].lower()
                image_map[name] = os.path.relpath(os.path.join(root, f), PROJECT_ROOT).replace("\\", "/")
    
    conn = sqlite3.connect(DB_PATH)
    # Предполагаем, что у товаров есть поле code (артикул)
    cur = conn.execute("SELECT title, code, price FROM products")
    items = []
    
    for title, code, price in cur.fetchall():
        code_str = str(code).lower()
        img_path = ""
        
        # 1. Пытаемся найти точное совпадение (А20)
        if code_str in image_map:
            img_path = image_map[code_str]
        else:
            # 2. Ищем варианты с подчеркиванием (например, А20_0, А20_1)
            # Перебираем все ключи, чтобы найти тот, который начинается с нашего кода
            for key in image_map:
                if key.startswith(f"{code_str}_"):
                    img_path = image_map[key]
                    break
        
        price_val = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
        items.append({"назва": title, "фото": img_path, "цена": price_val})
    
    conn.close()
    
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Готово! Привязка по точному артикулу или префиксу (А20_0).")

if __name__ == "__main__":
    export_to_json()