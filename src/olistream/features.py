import pandas as pd

def static_features(df):
    f = pd.DataFrame( 
        {
           "order_id": df['order_id'],
           "purchase_ts": df['purchase_ts'],
        }
    )
    f = pd.DataFrame({"order_id": df.order_id, "purchase_ts": df.purchase_ts})
    f["price"] = df.price
    f["freight"] = df.freight
    f["freight_ratio"] = df.freight / df.price.clip(lower=0.01)
    f["n_items"] = df.n_items
    f["installments"] = df.installments
    f["est_days"] = (df.estimated_ts - df.purchase_ts).dt.total_seconds() / 86400
    f["hour"] = df.purchase_ts.dt.hour
    f["dow"] = df.purchase_ts.dt.dayofweek
    f["payment_type"] = df.payment_type
    f["category"] = df.category.fillna("unknown")
    f["customer_state"] = df.customer_state
    f["is_late"] = df.is_late
    return f

df = pd.read_csv("data/processed/orders.csv", parse_dates=["purchase_ts", "estimated_ts", "delivered_ts"])
f = static_features(df)
f.to_csv("data/processed/features.csv", index=False)

print(f.shape)
print(f.head())
print(f.isna().sum())
num = ["price", "freight", "freight_ratio", "n_items", "installments", "est_days", "hour", "dow"]
print(f.groupby("is_late")[num].mean().T)



