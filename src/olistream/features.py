import pandas as pd
import numpy as np

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


def dynamic_features(df, key, name, order_days=7, late_days=30):
    wo = np.timedelta64(order_days, "D")
    wl = np.timedelta64(late_days, "D")
    n_orders = pd.Series(0.0, index=df.index)
    n_del = pd.Series(0.0, index=df.index)
    late_rate = pd.Series(np.nan, index=df.index)

    for _, g in df.groupby(key):
        t = g.purchase_ts.values
        p = np.sort(t)
        n_orders.loc[g.index] = (np.searchsorted(p, t, "left")
                                 - np.searchsorted(p, t - wo, "left"))

        d = g.sort_values("delivered_ts")
        dt = d.delivered_ts.values
        cum = np.concatenate([[0], np.cumsum(d.is_late.values.astype(int))])
        hi = np.searchsorted(dt, t, "left")
        lo = np.searchsorted(dt, t - wl, "left")
        nd = hi - lo
        n_del.loc[g.index] = nd
        late_rate.loc[g.index] = np.where(nd > 0, (cum[hi] - cum[lo]) / np.maximum(nd, 1), np.nan)

    return pd.DataFrame({
        f"{name}_n_orders_{order_days}d": n_orders,
        f"{name}_n_del_{late_days}d": n_del,
        f"{name}_late_rate_{late_days}d": late_rate,
    })



