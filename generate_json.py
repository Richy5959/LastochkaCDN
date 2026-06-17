import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def export_to_json() -> None:
    # 1. Создаем карту всех найденных картинок, где ключ - артикул до подчеркивания
    image_map = {}
    print("Сканирую папки с картинками...")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Получаем артикул (часть до _) и путь к файлу
                article = file.split('_')[0].lower()
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT).replace("\\", "/")
                
                if article not in image_map:
                    image_map[article] = []
                image_map[article].append(rel_path)
    
    # 2. Читаем базу и связываем товары
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("SELECT title, code, price FROM products")
        items = []
        for title, code, price in cur.fetchall():
            code_str = str(code).lower()
            img_path = ""
            
            # Ищем, есть ли в нашей карте артикул, совпадающий с кодом товара
            if code_str in image_map and image_map[code_str]:
                img_path = image_map[code_str][0] # Берем первую картинку
            
            price_display = int(price) if isinstance(price, (float, int)) and price == int(price) else price
            items.append({"назва": title, "фото": img_path, "цена": price_display})
    finally:
        conn.close()

    # 3. Сохраняем в JSON
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово! Файл data.json успешно обновлен.")

if __name__ == "__main__":
    export_to_json()