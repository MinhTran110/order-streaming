import numpy as np
import pandas as pd
from olistream.features import static_features, dynamic_features

df = pd.read_csv("data/processed/orders.csv",
                 parse_dates=["purchase_ts", "estimated_ts", "delivered_ts"])
df = df.sort_values("purchase_ts").reset_index(drop=True)

dyn = pd.concat([dynamic_features(df, "seller_id", "seller"),
                 dynamic_features(df, "customer_state", "state")], axis=1)
feat = pd.concat([static_features(df), dyn], axis=1)
feat.to_csv("data/processed/features_all.csv", index=False)


def brute(row, key, name):
    sub = df[df[key] == row[key]]
    t = row.purchase_ts
    n_orders = ((sub.purchase_ts >= t - pd.Timedelta(days=7)) & (sub.purchase_ts < t)).sum()
    d = sub[(sub.delivered_ts < t) & (sub.delivered_ts >= t - pd.Timedelta(days=30))]
    rate = d.is_late.mean() if len(d) else np.nan
    return n_orders, len(d), rate


bad = 0
for i in df.sample(300, random_state=0).index:
    for key, name in [("seller_id", "seller"), ("customer_state", "state")]:
        n_o, n_d, r = brute(df.loc[i], key, name)
        got = (feat.loc[i, f"{name}_n_orders_7d"], feat.loc[i, f"{name}_n_del_30d"],
               feat.loc[i, f"{name}_late_rate_30d"])
        if not (n_o == got[0] and n_d == got[1] and np.isclose(r, got[2], equal_nan=True)):
            bad += 1
print("số dòng lệch so với cách tính thủ công:", bad)

print(feat.shape)
print("tỷ lệ trễ thật:", round(df.is_late.mean(), 4))
print("trung bình seller_late_rate_30d:", round(feat.seller_late_rate_30d.mean(), 4))
print("trung bình state_late_rate_30d:", round(feat.state_late_rate_30d.mean(), 4))
print("tỷ lệ thiếu seller_late_rate_30d:", round(feat.seller_late_rate_30d.isna().mean(), 3))

