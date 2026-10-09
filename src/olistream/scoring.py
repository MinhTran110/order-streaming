import time
import joblib
import pandas as pd
from olistream.db import pg_conn, rw_conn

NUM = ["price", "freight", "freight_ratio", "n_items", "installments", "est_days", "hour", "dow"]

bundle = joblib.load("models/model.joblib")
model, feats, thr = bundle["model"], bundle["features"], bundle["threshold"]
rw = rw_conn().cursor()
pg = pg_conn().cursor()

SAVE = """INSERT INTO predictions (order_id, score, flagged)
          VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"""


def fetch():
    rw.execute(f"SELECT order_id, purchase_ts, {', '.join(feats)} FROM order_features")
    return pd.DataFrame(rw.fetchall(), columns=[d[0] for d in rw.description])


scored = set(fetch().order_id)
print(f"bỏ qua {len(scored)} đơn đang có sẵn. Ngưỡng cảnh báo: {thr:.3f}. Đang chờ đơn mới...")

while True:
    df = fetch()
    new = df[~df.order_id.isin(scored)].copy()
    if len(new):
        new[NUM] = new[NUM].astype(float)
        p = model.predict_proba(new[feats])[:, 1]
        pg.executemany(SAVE, [(o, float(s), bool(s >= thr)) for o, s in zip(new.order_id, p)])
        print(f"đã chấm {len(new)} đơn mới, gắn cờ {int((p >= thr).sum())}")
        scored.update(new.order_id)
    time.sleep(2)