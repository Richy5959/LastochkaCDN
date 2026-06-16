-- Re‑create the table to ensure the schema cache is refreshed.
DROP TABLE IF EXISTS public.products CASCADE;
CREATE TABLE public.products (
    code      TEXT PRIMARY KEY,   -- Код товара
    name      TEXT NOT NULL,     -- Название/заголовок
    price     INT4,              -- Цена (целое число)
    stock     INT4,              -- Количество в наличии
    color     TEXT,              -- Цвет/цвета
    size      TEXT,              -- Размеры (может быть список через запятую)
    type      TEXT,              -- Тип товара (например, трусики, боди)
    image_url TEXT               -- Ссылка на изображение (CDN)
);

-- Optional: create an index for faster search by name
CREATE INDEX IF NOT EXISTS idx_products_name ON public.products (name);

-- Allow anonymous role to insert rows (used for initial data load)
CREATE POLICY "allow_anon_insert"
  ON public.products
  FOR INSERT
  TO anon
  USING (true);

-- (Optional) After loading data you may want to tighten security or disable this policy.