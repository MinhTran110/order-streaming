CREATE SOURCE pg_src WITH (
  connector = 'postgres-cdc',
  hostname = '127.0.0.1',
  port = '5432',
  username = 'olist',
  password = 'olist',
  database.name = 'olist',
  slot.name = 'rw_olist_slot'
);

CREATE TABLE orders (
  order_id        VARCHAR PRIMARY KEY,
  customer_state  VARCHAR,
  seller_id       VARCHAR,
  category        VARCHAR,
  n_items         INT,
  price           DOUBLE PRECISION,
  freight         DOUBLE PRECISION,
  payment_type    VARCHAR,
  installments    INT,
  purchase_ts     TIMESTAMP,
  estimated_ts    TIMESTAMP,
  delivered_ts    TIMESTAMP,
  is_late         BOOLEAN
) FROM pg_src TABLE 'public.orders';