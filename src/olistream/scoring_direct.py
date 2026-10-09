import time
import joblib
import pandas as pd
from olistream.db import pg_conn

NUM = ["price", "freight", "freight_ratio", "n_items", "installments", "est_days", "hour", "dow"]

bundle = joblib.load("models/model.joblib")
model, feats, thr = bundle["model"], bundle["features"], bundle["threshold"]
cur = pg_conn().cursor()

cur.execute("SELECT NOW()::timestamp")
start = cur.fetchone()[0]

QUERY = """
SELECT order_id, price, freight,
  freight / (CASE WHEN price < 0.01 THEN 0.01 ELSE price END) AS freight_ratio,
  n_items, installments,
  EXTRACT(EPOCH FROM (estimated_ts - purchase_ts)) / 86400.0 AS est_days,
  EXTRACT(HOUR FROM purchase_ts)::INT AS hour,
  (EXTRACT(DOW FROM purchase_ts)::INT + 6) %% 7 AS dow,
  payment_type, COALESCE(category, 'unknown') AS category, customer_state
FROM orders o
WHERE o.ingest_ts > %s
  AND NOT EXISTS (SELECT 1 FROM predictions_direct d WHERE d.order_id = o.order_id)"""
SAVE = """INSERT INTO predictions_direct (order_id, score, flagged)
          VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"""

print(f"chỉ chấm các đơn ghi vào Postgres sau {start}. Ngưỡng: {thr:.3f}. Đang chờ...")
while True:
    cur.execute(QUERY, (start,))
    new = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
    if len(new):
        new[NUM] = new[NUM].astype(float)
        p = model.predict_proba(new[feats])[:, 1]
        cur.executemany(SAVE, [(o, float(s), bool(s >= thr)) for o, s in zip(new.order_id, p)])
        print(f"đã chấm {len(new)} đơn mới, gắn cờ {int((p >= thr).sum())}")
    time.sleep(2)

