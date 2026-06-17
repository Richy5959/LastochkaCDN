import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
# Путь к папке, где лежат фото (скрипт будет искать внутри проекта)
PROJECT_ROOT = Path(__file__).parent

def build_image_map():
    """Сканирует проект и создает словарь: { 'код_товара': 'полный_путь_к_файлу' }"""
    image_map = {}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Берем имя файла без расширения как код товара
                code = os.path.splitext(file)[0]
                # Сохраняем относительный путь
                relative_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                # Приводим путь к формату, который поймет браузер (заменяем \ на /)
                image_map[code] = relative_path.replace("\\", "/")
    return image_map

def export_to_json() -> None:
    image_map = build_image_map()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("SELECT title, code, price FROM products")
        items = []
        for title, code, price in cur.fetchall():
            # Ищем путь в нашей карте, если не нашли — оставляем пустым
            img_path = image_map.get(code, "")
            
            price_display = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
            items.append({"назва": title, "фото": img_path, "цена": price_display})
    finally:
        conn.close()

    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Экспортировано {len(items)} товаров. Найдено картинок: {len(image_map)}")

if __name__ == "__main__":
    export_to_json()