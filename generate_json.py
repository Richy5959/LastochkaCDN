def export_to_json() -> None:
    image_map = build_image_map()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("SELECT title, code, price FROM products")
        items = []
        for title, code, price in cur.fetchall():
            code_str = str(code).lower() if code else ""
            img_path = image_map.get(code_str, "")
            
            # ПРОВЕРКА: если путь найден, проверим, существует ли файл
            full_path = PROJECT_ROOT / img_path
            if img_path and not full_path.exists():
                print(f"ПРЕДУПРЕЖДЕНИЕ: Файл не найден по пути: {img_path}")
            
            price_display = int(price) if isinstance(price, (int, float)) and price.is_integer() else price
            items.append({"назва": title, "фото": img_path, "цена": price_display})
    finally:
        conn.close()

    JSON_PATH.write_text(json.dumps({"Товары": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Экспортировано {len(items)} товаров.")