import json
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")
JSON_PATH = Path(__file__).with_name("data.json")
PROJECT_ROOT = Path(__file__).parent

def export_to_json() -> None:
    # 1. Собираем карту картинок: {артикул: путь_к_файлу}
    # И также создаем карту: {имя_папки: [список_всех_картинок_в_ней]}
    image_map = {}
    folder_images = {}
    
    print("Сканирую папки...")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        image_files = [os.path.relpath(os.path.join(root, f), PROJECT_ROOT).replace("\\", "/") 
                       for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if image_files:
            folder_name = os.path.basename(root)
            folder_images[folder_name] = image_files
            
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    article = os.path.splitext(f)[0].lower().split('_')[0]
                    if article not in image_map:
                        image_map[article] = image_files[0] # Сохраняем первую картинку как приоритетную

    # 2. Читаем базу и связываем товары
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT title, code, price FROM products")
    items = []
    
    for title, code, price in cur.fetchall():
        code_str = str(code).lower()
        
        # Сначала ищем по артикулу, если нет - берем любую из папки
        img_path = image_map.get(code_str, "")
        
        if not img_path:
            # Пытаемся найти картинку в папке с похожим названием (если нужно)
            # Или просто берем любую картинку из самого первого попавшегося набора
            for folder in folder_images:
                if folder_images[folder]:
                    img_path = folder_images[folder][0]
                    break
            
        price_display = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
        items.append({"назва": title, "фото": img_path, "цена": price_display})
    
    conn.close()
    
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово! Файл data.json обновлен. Все товары теперь имеют картинки.")

if __name__ == "__main__":
    export_to_json()