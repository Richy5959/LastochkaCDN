"""Utility to import product data from the CSV file into a SQLite database.

The CSV file ``ВЛАД Telegram МАГАЗИН_тест - Master.csv`` contains a large number of
product rows with the following columns (the header line from the file):

```
Код товару,Заголовок,Бренд,Артикул постач.,Колір,"Закупка, грн",тип,,Ціна,фото,Кіл-ть,Розміри в інтернет-магазині
```

Only a subset of these columns is required for the shop front‑end.  The script
creates a SQLite database ``shop.db`` with a single table ``products`` that stores
the most important fields:

* ``code`` – product code (text, primary key)
* ``title`` – product title/description (text)
* ``brand`` – brand name (text, nullable)
* ``sku`` – supplier article number (text, nullable)
* ``color`` – colour description (text, nullable)
* ``price`` – retail price (real, nullable)
* ``photo`` – relative path to the product image (text, nullable)
* ``quantity`` – stock amount (integer, nullable)

The script is idempotent – if ``shop.db`` already exists it will be recreated.
It uses the standard library only (``csv`` and ``sqlite3``) so it works on any
environment without extra dependencies.
"""

import csv
import sqlite3
from pathlib import Path

CSV_PATH = Path(__file__).with_name("ВЛАД Telegram МАГАЗИН_тест - Master.csv")
DB_PATH = Path(__file__).with_name("shop.db")


def create_database(conn: sqlite3.Connection) -> None:
    """Create the ``products`` table.

    The schema mirrors the columns we keep from the CSV.  ``code`` is the primary
    key because it uniquely identifies a product in the source file.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            code TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            brand TEXT,
            sku TEXT,
            color TEXT,
            price REAL,
            photo TEXT,
            quantity INTEGER
        )
        """
    )
    conn.commit()


def import_csv(conn: sqlite3.Connection) -> None:
    """Read the CSV file and insert rows into the ``products`` table.

    Empty strings are stored as ``NULL`` in the database.  ``price`` and
    ``quantity`` are converted to ``float``/``int`` when possible.
    """
    with CSV_PATH.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            # Helper to normalise empty values to None
            def n(val: str):
                return val.strip() or None

            code = n(row.get("Код товару"))
            title = n(row.get("Заголовок"))
            brand = n(row.get("Бренд"))
            sku = n(row.get("Артикул постач."))
            color = n(row.get("Колір"))
            # Price column is named "Ціна" – it may contain commas as decimal
            price_raw = n(row.get("Ціна"))
            try:
                price = float(price_raw.replace(",", ".")) if price_raw else None
            except ValueError:
                price = None
            photo = n(row.get("фото"))
            qty_raw = n(row.get("Кіл-ть"))
            try:
                quantity = int(float(qty_raw)) if qty_raw else None
            except ValueError:
                quantity = None

            rows.append((code, title, brand, sku, color, price, photo, quantity))

    conn.executemany(
        "INSERT OR REPLACE INTO products (code, title, brand, sku, color, price, photo, quantity) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()


def main() -> None:
    # Remove existing DB to guarantee a clean import each run
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        create_database(conn)
        import_csv(conn)
        print(f"Database created at {DB_PATH} with {conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]} records")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
