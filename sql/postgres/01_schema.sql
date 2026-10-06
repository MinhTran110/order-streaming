CREATE TABLE orders (
  order_id        VARCHAR(32) PRIMARY KEY,
  customer_state  VARCHAR(2),
  seller_id       VARCHAR(32),
  category        VARCHAR(80),
  n_items         INT,
  price           DOUBLE PRECISION,
  freight         DOUBLE PRECISION,
  payment_type    VARCHAR(20),
  installments    INT,
  purchase_ts     TIMESTAMP,
  estimated_ts    TIMESTAMP,
  delivered_ts    TIMESTAMP,
  is_late         BOOLEAN,
  ingest_ts       TIMESTAMP DEFAULT NOW()
);
ALTER TABLE orders REPLICA IDENTITY FULL;