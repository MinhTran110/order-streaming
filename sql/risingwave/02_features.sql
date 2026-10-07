CREATE MATERIALIZED VIEW seller_features_7d AS
SELECT seller_id, window_start, window_end,
    COUNT(*) AS n_orders,
    AVG(price) AS avg_price,
    AVG(freight) AS avg_freight,
    COUNT(is_late) AS n_delivered,
    AVG(CASE WHEN is_late THEN 1 ELSE 0 END) AS late_rate
FROM HOP(orders, purchase_ts, INTERVAL '1 day', INTERVAL '7 days')
GROUP BY seller_id, window_start, window_end;


CREATE MATERIALIZED VIEW state_daily AS
SELECT customer_state, window_start,
    COUNT(*) AS n_orders,
    AVG(freight) AS avg_freight,
    AVG(CASE WHEN is_late THEN 1 ELSE 0 END) AS late_rate
FROM TUMBLE(orders, purchase_ts, INTERVAL '1 day')
GROUP BY customer_state, window_start;

