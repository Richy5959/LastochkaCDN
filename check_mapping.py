import sqlite3
import os
from pathlib import Path

def check():
    PROJECT_ROOT = Path(__file__).parent
    DB_PATH = PROJECT_ROOT / "shop.db"
    
    # 1. Собираем все реальные имена файлов
    found_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                found_files.append(f.lower())

    # 2. Смотрим коды из базы
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT title, code FROM products LIMIT 10")
    rows = cur.fetchall()
    
    print("--- ПРИМЕРЫ ИЗ БАЗЫ ---")
    for title, code in rows:
        print(f"Товар: {title} | Код: {code}")
    
    print("\n--- ПРИМЕРЫ ИЗ ПАПОК ---")
    for f in found_files[:10]:
        print(f"Файл: {f}")

check()