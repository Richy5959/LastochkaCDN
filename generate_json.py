import json
import csv
import os
from pathlib import Path

# Убедись, что файл называется products.csv
CSV_PATH = Path(__file__).with_name("products.csv")
JSON_PATH = Path(__file__).with_name("data.json")

def export_to_json() -> None:
    items = []
    
    # Читаем CSV
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Берем данные прямо из колонок, как в таблице
            title = row.get("Название UA") or row.get("Название RU", "")
            price = row.get("Цена", 0)
            img_path = row.get("Путь к фото", "")
            
            items.append({
                "назва": title, 
                "фото": img_path, 
                "цена": price
            })
    
    # Сохраняем
    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово! Обработано {len(items)} товаров по данным из таблицы.")

if __name__ == "__main__":
    export_to_json()