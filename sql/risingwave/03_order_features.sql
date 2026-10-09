CREATE MATERIALIZED VIEW order_features AS
SELECT
  order_id,
  purchase_ts,
  price,
  freight,
  freight / (CASE WHEN price < 0.01 THEN 0.01 ELSE price END) AS freight_ratio,
  n_items,
  installments,
  EXTRACT(EPOCH FROM (estimated_ts - purchase_ts)) / 86400.0 AS est_days,
  EXTRACT(HOUR FROM purchase_ts)::INT AS hour,
  (EXTRACT(DOW FROM purchase_ts)::INT + 6) % 7 AS dow,
  payment_type,
  COALESCE(category, 'unknown') AS category,
  customer_state
FROM orders;

