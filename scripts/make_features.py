import pandas as pd
from olistream.features import static_features

df = pd.read_csv("data/processed/orders.csv",
                 parse_dates=["purchase_ts", "estimated_ts", "delivered_ts"])
f = static_features(df)
f.to_csv("data/processed/features_static.csv", index=False)

print(f.shape)
print(f.isna().sum())
num = ["price", "freight", "freight_ratio", "n_items", "installments", "est_days", "hour", "dow"]
print(f.groupby("is_late")[num].mean().T)