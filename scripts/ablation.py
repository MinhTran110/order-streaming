import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder

STATIC = ["price", "freight", "freight_ratio", "n_items", "installments", "est_days", "hour", "dow"]
CAT = ["payment_type", "category", "customer_state"]

df = pd.read_csv("data/processed/features_all.csv", parse_dates=["purchase_ts"])
SELLER = [c for c in df.columns if c.startswith("seller_")]
STATE = [c for c in df.columns if c.startswith("state_")]
train = df[(df.purchase_ts >= "2017-01-01") & (df.purchase_ts < "2018-01-01")]
val = df[(df.purchase_ts >= "2018-01-01") & (df.purchase_ts < "2018-04-01")]
y_val = val.is_late.astype(int)


def run(num, seed):
    pre = ColumnTransformer([
        ("num", "passthrough", num),
        ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CAT)])
    m = make_pipeline(pre, HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=seed))
    m.fit(train[num + CAT], train.is_late.astype(int))
    return average_precision_score(y_val, m.predict_proba(val[num + CAT])[:, 1])


variants = {"tĩnh": STATIC, "tĩnh + seller": STATIC + SELLER,
            "tĩnh + state": STATIC + STATE, "tĩnh + cả hai": STATIC + SELLER + STATE}
print("mức ngẫu nhiên:", round(y_val.mean(), 3))
for name, cols in variants.items():
    s = [run(cols, k) for k in range(5)]
    print(f"{name:16s} PR-AUC trung bình {np.mean(s):.3f} ± {np.std(s):.3f}")

    