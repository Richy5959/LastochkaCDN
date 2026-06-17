import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def build_image_map():
    image_map = {}
    print("Сканирую папки на наличие картинок...")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                code = os.path.splitext(file)[0].lower()
                relative_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                image_map[code] = relative_path.replace("\\", "/")
    print(f"Найдено файлов картинок: {len(image_map)}")
    return image_map

def export_to_json() -> None:
    image_map = build_image_map()
    if not DB_PATH.exists():
        print("ОШИБКА: База данных shop.db не найдена!")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("SELECT title, code, price FROM products")
        items = []
        rows = cur.fetchall()
        print(f"Обрабатываю {len(rows)} товаров из базы...")
        
        for title, code, price in rows:
            code_str = str(code).lower() if code else ""
            img_path = image_map.get(code_str, "")
            
            # Если пути нет — сигнализируем
            if not img_path:
                print(f"ВНИМАНИЕ: Для товара {code} картинка не найдена!")
            
            price_display = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
            items.append({"назва": title, "фото": img_path, "цена": price_display})
    finally:
        conn.close()

    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово! Файл data.json обновлен. Проверь вывод выше на наличие предупреждений.")

if __name__ == "__main__":
    export_to_json()