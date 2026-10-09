import pandas as pd
from sklearn.metrics import roc_auc_score

df = pd.read_csv("data/processed/features_all.csv", parse_dates=["purchase_ts"])
dyn = [c for c in df.columns if c.startswith(("seller_", "state_"))]
periods = {"2017-Q1": ("2017-01-01", "2017-04-01"), "2017-Q2": ("2017-04-01", "2017-07-01"),
           "2017-Q3": ("2017-07-01", "2017-10-01"), "2017-Q4": ("2017-10-01", "2018-01-01"),
           "val 2018-Q1": ("2018-01-01", "2018-04-01")}

rows = []
for name, (a, b) in periods.items():
    d = df[(df.purchase_ts >= a) & (df.purchase_ts < b)]
    r = {"giai đoạn": name, "tỷ lệ trễ": round(d.is_late.mean(), 3)}
    for c in dyn:
        x = d[[c, "is_late"]].dropna()
        r[c] = round(roc_auc_score(x.is_late, x[c]), 3)
    rows.append(r)
print(pd.DataFrame(rows).to_string(index=False))
