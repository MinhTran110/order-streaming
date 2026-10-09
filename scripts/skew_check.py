import pandas as pd
from olistream.db import rw_conn

NUM = ["price", "freight", "freight_ratio", "n_items", "installments", "est_days", "hour", "dow"]
CAT = ["payment_type", "category", "customer_state"]

cur = rw_conn().cursor()
cur.execute(f"SELECT order_id, {', '.join(NUM + CAT)} FROM order_features")
rw = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
rw[NUM] = rw[NUM].astype(float)

ref = pd.read_csv("data/processed/features_all.csv")[["order_id"] + NUM + CAT]
m = rw.merge(ref, on="order_id", suffixes=("_rw", "_pd"))
print("đơn ở RisingWave:", len(rw), "| ghép được với CSV:", len(m))

for c in NUM:
    d = (m[c + "_rw"] - m[c + "_pd"]).abs()
    print(f"{c:14s} lệch tối đa {d.max():.2e} | số dòng lệch > 1e-6: {int((d > 1e-6).sum())}")
for c in CAT:
    a, b = m[c + "_rw"].fillna("unknown"), m[c + "_pd"].fillna("unknown")
    print(f"{c:14s} số dòng khác nhau: {int((a != b).sum())}")

