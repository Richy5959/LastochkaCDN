import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def export_to_json() -> None:
    # 1. Собираем все картинки в словарь: {артикул: путь_к_файлу}
    image_map = {}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Берем имя файла без расширения
                name = os.path.splitext(file)[0].lower()
                # Берем артикул до подчеркивания
                article = name.split('_')[0]
                path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT).replace("\\", "/")
                # Сохраняем, если еще нет (берем первое попавшееся)
                if article not in image_map:
                    image_map[article] = path
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT title, code, price FROM products")
    items = []
    
    missing_count = 0
    for title, code, price in cur.fetchall():
        # Приводим код из базы к нижнему регистру для поиска
        code_str = str(code).lower()
        
        # Поиск картинки
        img_path = image_map.get(code_str, "")
        
        if not img_path:
            missing_count += 1
            # Можно раскомментировать принт ниже, чтобы увидеть список проблемных товаров
            # print(f"Не найдено фото для: {title} (код {code})")
            
        price_display = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
        items.append({"назва": title, "фото": img_path, "цена": price_display})
    
    conn.close()
    
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово! Обработано товаров: {len(items)}. Не найдено фото: {missing_count}")

if __name__ == "__main__":
    export_to_json()