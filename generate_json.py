import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def build_image_map():
    """Сканирует проект и создает карту: { 'код_в_нижнем_регистре': 'относительный_путь' }"""
    image_map = {}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Пропускаем папку .git и саму папку с базой, если нужно
        if '.git' in root or 'venv' in root:
            continue
            
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Берем имя файла без расширения и приводим к нижнему регистру
                code = os.path.splitext(file)[0].lower()
                # Путь от корня проекта
                relative_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                # Сохраняем путь, заменяя обратные слеши Windows на обычные
                image_map[code] = relative_path.replace("\\", "/")
    return image_map

def export_to_json() -> None:
    image_map = build_image_map()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("SELECT title, code, price FROM products")
        items = []
        for title, code, price in cur.fetchall():
            # Поиск по коду в нижнем регистре
            code_str = str(code).lower() if code else ""
            img_path = image_map.get(code_str, "")
            
            price_display = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
            items.append({"назва": title, "фото": img_path, "цена": price_display})
    finally:
        conn.close()

    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Экспортировано {len(items)} товаров.")
    print(f"Всего картинок в проекте найдено: {len(image_map)}")

if __name__ == "__main__":
    export_to_json()