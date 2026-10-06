import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("data/processed/orders.csv", parse_dates=["purchase_ts", "estimated_ts", "delivered_ts"])
df.info()
print(df.head())
print(df.isna().sum())
df.describe(include="all").T

m = df.groupby(df.purchase_ts.dt.to_period("M").astype(str)).agg(
    n_orders=("order_id", "count"), late_rate=("is_late", "mean"))

# So don hang theo thang va ty le tre
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(m.index, m.n_orders, color="lightgray")
ax.tick_params(axis="x", rotation=60)
ax.set_ylabel("số đơn")
ax2 = ax.twinx()
ax2.plot(m.index, m.late_rate, color="red", marker="o")
ax2.set_ylabel("tỷ lệ trễ")
plt.tight_layout()
plt.show()

# So don hang theo nam va ty le tre theo bang
s = df.groupby(df.purchase_ts.dt.to_period("Y").astype(str)).agg(
    n_orders=("order_id", "count"), late_rate=("is_late", "mean"))
s.late_rate.plot(kind="bar", color="red", figsize=(6, 4))
plt.xlabel("Năm")
plt.ylabel("Tỷ lệ trễ")
plt.show()

# so sanh cac bien so sanh giua cac don tre va don khong tre
df["freight_ratio"] = df.freight / df.price
df["est_days"] = (df.estimated_ts - df.purchase_ts).dt.days

fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, c in zip(axes, ["price", "freight", "freight_ratio", "est_days"]):
    df.boxplot(column=c, by="is_late", ax=ax, showfliers=False)
plt.suptitle("")
plt.show()

# phan bo don theo seller va loai thanh toan
sc = df.groupby("seller_id").size()
print(sc.describe())
sc.clip(upper=200).plot.hist(bins=50, figsize=(8, 4))
plt.xlabel("số đơn mỗi seller (cắt ở 200)")
plt.show()


df.groupby("payment_type").is_late.agg(["count", "mean"])

from ydata_profiling import ProfileReport
profile = ProfileReport(df, title="Olist Orders EDA", explorative=True)

profile.to_file("data/processed/orders_eda.html")
