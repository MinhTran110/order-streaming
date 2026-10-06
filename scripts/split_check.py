import pandas as pd

df = pd.read_csv("data/processed/orders.csv", parse_dates=["purchase_ts"])
m = df.groupby(df.purchase_ts.dt.to_period("M")).agg(
    n=("order_id", "count"), late_rate=("is_late", "mean"))
print(m.round(3))
print("tổng tỷ lệ trễ:", round(df.is_late.mean(), 4))