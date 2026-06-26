ALTER TABLE public.products ADD COLUMN IF NOT EXISTS is_discount boolean NOT NULL DEFAULT false;

UPDATE public.products SET is_discount = true WHERE cost > price;

ALTER TABLE public.products ADD CONSTRAINT products_cost_price_check CHECK (cost <= price OR is_discount = true);