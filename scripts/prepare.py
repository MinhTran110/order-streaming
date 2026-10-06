import pandas as pd
# Doc va loc 
ts = ["order_purchase_timestamp", "order_estimated_delivery_date", "order_delivered_customer_date"]

ol = pd.read_csv("data/raw/olist_orders_dataset.csv", parse_dates = ts)
ol = ol[(ol.order_status == "delivered") & ol.order_delivered_customer_date.notna()]

# Gop thong tin san pham theo tung don hang
prod = pd.read_csv("data/raw/olist_products_dataset.csv")[["product_id", "product_category_name"]]
tr = pd.read_csv("data/raw/product_category_name_translation.csv")
items = (pd.read_csv("data/raw/olist_order_items_dataset.csv")
           .merge(prod, on="product_id", how="left")
           .merge(tr, on="product_category_name", how="left"))

it = items.groupby("order_id").agg(
    seller_id=("seller_id", "first"),
    category=("product_category_name_english", "first"),
    n_items=("order_item_id", "count"),
    price=("price", "sum"),
    freight=("freight_value", "sum")).reset_index()

# Gop thong tin don hang, khach hang, san pham va thanh toan
pay = (pd.read_csv("data/raw/olist_order_payments_dataset.csv").sort_values("payment_value", ascending=False).drop_duplicates("order_id"))[["order_id", "payment_type", "payment_installments"]].rename(columns={"payment_installments": "installments"})

cust = pd.read_csv("data/raw/olist_customers_dataset.csv")[["customer_id", "customer_state"]]

# Noi tat ca thong tin vao 1 bang duy nhat
df = (ol.merge(cust, on="customer_id").merge(it, on="order_id").merge(pay, on="order_id")
        .rename(columns={"order_purchase_timestamp": "purchase_ts",
                         "order_estimated_delivery_date": "estimated_ts",
                         "order_delivered_customer_date": "delivered_ts"}))

df["is_late"] = df.delivered_ts > df.estimated_ts

cols = ["order_id", "customer_state", "seller_id", "category", "n_items", "price", "freight",
        "payment_type", "installments", "purchase_ts", "estimated_ts", "delivered_ts", "is_late"]
df = df[cols].sort_values("purchase_ts")
df.to_csv("data/processed/orders.csv", index=False)

print(len(df), "đơn | tỷ lệ trễ:", round(df.is_late.mean(), 4))
print(df.purchase_ts.min(), "->", df.purchase_ts.max())
print(df.groupby(df.purchase_ts.dt.to_period("Q")).size())

