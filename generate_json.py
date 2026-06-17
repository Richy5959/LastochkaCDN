import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def build_image_map():
    image_map = {}
    print("Сканирую папки...")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Сохраняем имя файла в нижнем регистре
                name = file.lower()
                path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT).replace("\\", "/")
                image_map[name] = path
    return image_map

def export_to_json() -> None:
    image_map = build_image_map()
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT title, code, price FROM products")
    items = []
    
    print("Сопоставляю товары с файлами...")
    for title, code, price in cur.fetchall():
        code_str = str(code).lower() if code else ""
        img_path = ""
        
        # УМНЫЙ ПОИСК: ищем файл, в имени которого есть код товара
        for filename, path in image_map.items():
            if code_str in filename:
                img_path = path
                break
        
        if not img_path:
            print(f"ВНИМАНИЕ: Для товара {code} картинка не найдена!")
            
        price_display = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
        items.append({"назва": title, "фото": img_path, "цена": price_display})
    
    conn.close()
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Готово! data.json обновлен.")

if __name__ == "__main__":
    export_to_json()