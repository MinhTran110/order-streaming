import argparse
import time
import pandas as pd
from olistream.db import pg_conn

p = argparse.ArgumentParser()
p.add_argument("--start", default="2018-04-01")
p.add_argument("--end", default="2099-01-01")
p.add_argument("--speedup", type=float, default=86400)
p.add_argument("--max-sleep", type=float, default=1.0)
p.add_argument("--limit", type=int, default=0)
a = p.parse_args()

df = pd.read_csv("data/processed/orders.csv",
                 parse_dates=["purchase_ts", "estimated_ts", "delivered_ts"])
df = df[(df.purchase_ts >= a.start) & (df.purchase_ts < a.end)]

ins = df.assign(t=df.purchase_ts, kind=0)
upd = df.assign(t=df.delivered_ts, kind=1)
ev = pd.concat([ins, upd]).sort_values(["t", "kind"])
if a.limit:
    ev = ev.head(a.limit)

INSERT = """INSERT INTO orders (order_id, customer_state, seller_id, category, n_items, price,
            freight, payment_type, installments, purchase_ts, estimated_ts)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING"""
UPDATE = "UPDATE orders SET delivered_ts=%s, is_late=%s WHERE order_id=%s"


def s(v):
    return None if pd.isna(v) else v


cur = pg_conn().cursor()
prev = ev.t.iloc[0]
for i, r in enumerate(ev.itertuples(index=False), 1):
    gap = (r.t - prev).total_seconds() / a.speedup
    time.sleep(min(max(gap, 0), a.max_sleep))
    prev = r.t
    if r.kind == 0:
        cur.execute(INSERT, (r.order_id, s(r.customer_state), s(r.seller_id), s(r.category),
                             int(r.n_items), float(r.price), float(r.freight),
                             s(r.payment_type), int(r.installments),
                             r.purchase_ts.to_pydatetime(), r.estimated_ts.to_pydatetime()))
    else:
        cur.execute(UPDATE, (r.delivered_ts.to_pydatetime(), bool(r.is_late), r.order_id))
    if i % 1000 == 0:
        print(f"{i}/{len(ev)} sự kiện | thời gian mô phỏng: {r.t}")

print("xong:", len(ev), "sự kiện")