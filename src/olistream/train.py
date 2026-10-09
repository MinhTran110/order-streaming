import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score

STATIC = ["price", "freight", "freight_ratio", "n_items", "installments", "est_days", "hour", "dow"]
DYNAMIC = ["seller_n_orders_7d", "seller_n_delivered_30d", "seller_late_rate_30d", "state_n_orders_7d", "state_n_delivered_30d", "state_late_rate_30d"]
CAT = ["payment_type", "category", "customer_state"]

df = pd.read_csv("data/processed/features_all.csv", parse_dates=["purchase_ts"])
DYNAMIC = [c for c in df.columns if c.startswith(("seller_", "state_"))]
print("feature động:", DYNAMIC)

train = df[(df.purchase_ts < "2018-01-01") & (df.purchase_ts >= "2017-01-01")]
val = df[(df.purchase_ts < "2018-04-01") & (df.purchase_ts >= "2018-01-01")]
print("train:", len(train), "trễ", round(train.is_late.mean(), 3),
      "| val:", len(val), "trễ", round(val.is_late.mean(), 3))

def logreg(num):
    pre = ColumnTransformer([
        ("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=100), CAT)])
    return make_pipeline(pre, LogisticRegression(max_iter=1000, class_weight="balanced"))


def boosting(num):
    pre = ColumnTransformer([
        ("num", "passthrough", num),
        ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CAT)])
    return make_pipeline(pre, HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=0))


def top_decile(y, p, frac=0.1):
    idx = np.argsort(-p)[: int(len(y) * frac)]
    hits = y[idx].sum()
    return hits / len(idx), hits / y.sum()


models = {
    "logreg (tĩnh + động)": (logreg(STATIC + DYNAMIC), STATIC + DYNAMIC),
    "boosting (chỉ tĩnh)": (boosting(STATIC), STATIC),
    "boosting (tĩnh + động)": (boosting(STATIC + DYNAMIC), STATIC + DYNAMIC),
}

rows = []
y = val.is_late.values.astype(int)
for name, (m, cols) in models.items():
    m.fit(train[cols + CAT], train.is_late.astype(int))
    p = m.predict_proba(val[cols + CAT])[:, 1]
    prec, rec = top_decile(y, p)
    rows.append({"model": name, "PR-AUC": average_precision_score(y, p),
                 "ROC-AUC": roc_auc_score(y, p),
                 "precision@top10%": prec, "recall@top10%": rec})

print("mức ngẫu nhiên của PR-AUC (= tỷ lệ trễ trên val):", round(y.mean(), 3))
print(pd.DataFrame(rows).round(3).to_string(index=False))

