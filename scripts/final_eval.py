import pandas as pd
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
import joblib
import os
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.ensemble import HistGradientBoostingClassifier


STATIC = ["price", "freight", "freight_ratio", "n_items", "installments", "est_days", "hour", "dow"]
CAT = ["payment_type", "category", "customer_state"]
FEATURES = STATIC + CAT
FLAG_SHARE = 0.10

df = pd.read_csv("data/processed/features_all.csv", parse_dates=["purchase_ts"])
train = df[(df.purchase_ts >= "2017-01-01") & (df.purchase_ts < "2018-01-01")]
val = df[(df.purchase_ts >= "2018-01-01") & (df.purchase_ts < "2018-04-01")]
test = df[df.purchase_ts >= "2018-04-01"]

pre = ColumnTransformer([
    ("num", "passthrough", STATIC),
    ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CAT)])
model = make_pipeline(pre, HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=0))
model.fit(train[FEATURES], train.is_late.astype(int))

thr = float(np.quantile(model.predict_proba(val[FEATURES])[:, 1], 1 - FLAG_SHARE))
print(f"ngưỡng điểm (gắn cờ {FLAG_SHARE:.0%} đơn cao nhất ở validation): {thr:.3f}")


def report(name, d):
    y = d.is_late.astype(int).values
    p = model.predict_proba(d[FEATURES])[:, 1]
    flag = p >= thr
    tp = int((flag & (y == 1)).sum())
    prec = tp / max(flag.sum(), 1)
    base = y.mean()
    print(f"\n{name}: {len(d)} đơn | tỷ lệ trễ thật {base:.3f}")
    print(f"  PR-AUC {average_precision_score(y, p):.3f} (ngẫu nhiên {base:.3f}) | ROC-AUC {roc_auc_score(y, p):.3f}")
    print(f"  gắn cờ {flag.mean():.1%} số đơn | precision {prec:.3f} | recall {tp / y.sum():.3f} | lift {prec / base:.2f}x")


report("validation (đã dùng để chọn ngưỡng)", val)
report("TEST (đánh giá cuối)", test)

os.makedirs("models", exist_ok=True)
joblib.dump({"model": model, "features": FEATURES, "threshold": thr}, "models/model.joblib")
print("\nđã lưu models/model.joblib")

