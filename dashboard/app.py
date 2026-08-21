from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "walmart_dataset" / "data"
GOLD_LAYER_PATH = BASE_DIR / "dashboard" / "gold_layer.csv"

st.set_page_config(page_title="Walmart Retail Analytics", page_icon="🛒", layout="wide")


@st.cache_data
def load_source_data() -> dict[str, pd.DataFrame]:
    files = {
        "customers": "customers.csv",
        "employees": "employees.csv",
        "orders": "orders.csv",
        "order_items": "order_items.csv",
        "products": "products.csv",
        "stores": "stores.csv",
    }

    data: dict[str, pd.DataFrame] = {}
    for name, filename in files.items():
        path = DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing dataset: {path}")

        df = pd.read_csv(path)
        for ts_column in ["created_timestamp", "updated_timestamp", "order_timestamp"]:
            if ts_column in df.columns:
                df[ts_column] = pd.to_datetime(df[ts_column], errors="coerce")

        data[name] = df

    return data


@st.cache_data
def build_gold_layer() -> pd.DataFrame:
    """Mirror the dbt gold transformation logic used by this project.

    This follows the same business-layer pattern as the dbt files:
    - join orders to order items
    - join products, customers, employees, and stores
    - keep the key fields from the curated gold/fact layer
    """
    source = load_source_data()

    orders = source["orders"].copy()
    order_items = source["order_items"].copy()
    products = source["products"].copy()
    customers = source["customers"].copy()
    employees = source["employees"].copy()
    stores = source["stores"].copy()

    customers = customers.rename(
        columns={
            "first_name": "customer_first_name",
            "last_name": "customer_last_name",
            "email": "customer_email",
            "city": "customer_city",
            "province": "customer_province",
            "country": "customer_country",
        }
    )

    stores = stores.rename(
        columns={
            "store_name": "store_name",
            "city": "store_city",
            "province": "store_province",
            "country": "store_country",
        }
    )

    employees = employees.rename(
        columns={
            "first_name": "employee_first_name",
            "last_name": "employee_last_name",
            "job_title": "employee_job_title",
            "salary": "employee_salary",
        }
    )

    products = products.rename(
        columns={
            "product_name": "product_name",
            "category": "category",
            "brand": "brand",
            "price": "price",
        }
    )

    fact = orders.merge(order_items, on="order_id", how="left")
    fact = fact.merge(
        customers[["customer_id", "customer_first_name", "customer_last_name", "customer_email", "customer_city", "customer_province", "customer_country"]],
        on="customer_id",
        how="left",
    )
    fact = fact.merge(products[["product_id", "product_name", "category", "brand", "price"]], on="product_id", how="left")
    fact = fact.merge(
        employees[["employee_id", "store_id", "employee_first_name", "employee_last_name", "employee_job_title", "employee_salary"]],
        on="store_id",
        how="left",
    )
    fact = fact.merge(stores[["store_id", "store_name", "store_city", "store_province", "store_country"]], on="store_id", how="left")

    fact = fact[
        [
            "order_id",
            "order_item_id",
            "product_id",
            "store_id",
            "employee_id",
            "customer_id",
            "order_timestamp",
            "order_status",
            "payment_method",
            "total_amount",
            "quantity",
            "unit_price",
            "line_amount",
            "product_name",
            "category",
            "brand",
            "price",
            "customer_city",
            "customer_province",
            "customer_country",
            "store_name",
            "store_city",
            "store_province",
            "store_country",
            "employee_first_name",
            "employee_last_name",
            "employee_job_title",
            "employee_salary",
        ]
    ].copy()

    fact = fact.rename(
        columns={
            "customer_city": "customer_city",
            "customer_province": "customer_province",
            "customer_country": "customer_country",
            "store_city": "store_city",
            "store_province": "store_province",
            "store_country": "store_country",
            "employee_first_name": "employee_first_name",
            "employee_last_name": "employee_last_name",
            "employee_job_title": "employee_job_title",
            "employee_salary": "employee_salary",
        }
    )

    fact.to_csv(GOLD_LAYER_PATH, index=False)
    return fact


@st.cache_data
def load_gold_data() -> pd.DataFrame:
    """Prefer a real warehouse gold table if configured; otherwise use the gold-layer export created from the project logic."""
    host = os.getenv("DATABRICKS_HOST")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")
    catalog = os.getenv("DATABRICKS_CATALOG")
    schema = os.getenv("DATABRICKS_SCHEMA")

    if host and http_path and token and catalog and schema:
        try:
            from databricks import sql

            with sql.connect(server_hostname=host, http_path=http_path, access_token=token) as connection:
                with connection.cursor() as cursor:
                    query = f"SELECT * FROM {catalog}.{schema}.fact_orders"
                    df = pd.read_sql(query, connection)
                    if not df.empty:
                        return df
        except Exception:
            st.warning("Databricks gold table unavailable; falling back to local gold-layer export.")

    if GOLD_LAYER_PATH.exists():
        return pd.read_csv(GOLD_LAYER_PATH)

    return build_gold_layer()


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    if "order_timestamp" not in df.columns:
        return df

    start_date = st.sidebar.date_input("Start date", value=df["order_timestamp"].min().date())
    end_date = st.sidebar.date_input("End date", value=df["order_timestamp"].max().date())
    selected_status = st.sidebar.multiselect(
        "Order status",
        options=sorted(df["order_status"].dropna().unique().tolist()),
        default=sorted(df["order_status"].dropna().unique().tolist()),
    )
    selected_country = st.sidebar.multiselect(
        "Country",
        options=sorted(df["store_country"].dropna().unique().tolist()),
        default=sorted(df["store_country"].dropna().unique().tolist()),
    )

    df = df[(df["order_timestamp"].dt.date >= pd.Timestamp(start_date).date()) & (df["order_timestamp"].dt.date <= pd.Timestamp(end_date).date())]
    if selected_status:
        df = df[df["order_status"].isin(selected_status)]
    if selected_country:
        df = df[df["store_country"].isin(selected_country)]

    return df


def main() -> None:
    gold_df = load_gold_data()
    if "order_timestamp" in gold_df.columns:
        gold_df["order_timestamp"] = pd.to_datetime(gold_df["order_timestamp"], errors="coerce")
    if "total_amount" in gold_df.columns:
        gold_df["total_amount"] = pd.to_numeric(gold_df["total_amount"], errors="coerce")
    if "line_amount" in gold_df.columns:
        gold_df["line_amount"] = pd.to_numeric(gold_df["line_amount"], errors="coerce")

    filtered = filter_data(gold_df)

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0b1220 0%, #101827 100%);
            color: #e5eefc;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        [data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 14px;
            padding: 0.8rem 1rem;
            box-shadow: 0 8px 24px rgba(2, 6, 23, 0.34);
        }
        [data-testid="stMetricValue"] {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f8fafc;
        }
        div[data-testid="stMetricLabel"] {
            color: #cbd5e1;
            font-size: 0.8rem;
        }
        .section-label {
            color: #cbd5e1;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin: 1.2rem 0 0.6rem 0;
        }
        .chart-panel {
            background: rgba(15, 23, 42, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 14px;
            padding: 0.75rem;
            box-shadow: 0 10px 24px rgba(2, 6, 23, 0.28);
            margin-top: 0.5rem;
        }
        h1 {
            color: #f8fafc;
            margin-bottom: 0.2rem;
        }
        .stCaption {
            color: #cbd5e1 !important;
        }
        .stDataFrame {
            background: rgba(15, 23, 42, 0.82);
            border-radius: 12px;
        }
        table, th, td {
            color: #e2e8f0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Walmart Retail Analytics")
    st.caption("Gold-layer dashboard covering revenue, store performance, product sales, and order trends.")

    total_revenue = float(filtered["line_amount"].fillna(0).sum())
    total_orders = int(filtered["order_id"].nunique()) if "order_id" in filtered.columns else 0
    avg_order_value = float(filtered.groupby("order_id")["line_amount"].sum().mean()) if total_orders else 0.0
    top_product = (
        filtered.groupby("product_name", as_index=False)["line_amount"].sum().sort_values("line_amount", ascending=False).head(1)
        if "product_name" in filtered.columns
        else pd.DataFrame({"product_name": ["N/A"], "line_amount": [0]})
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Orders", f"{total_orders:,}")
    col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
    col4.metric("Top Product", top_product["product_name"].iat[0] if not top_product.empty else "N/A")

    st.markdown('<div class="section-label">Performance overview</div>', unsafe_allow_html=True)

    store_sales = (
        filtered.groupby(["store_name", "store_country"], as_index=False)["line_amount"].sum().sort_values("line_amount", ascending=False)
        if {"store_name", "store_country"}.issubset(filtered.columns)
        else filtered.groupby("store_name", as_index=False)["line_amount"].sum().sort_values("line_amount", ascending=False)
    )
    fig_store = px.bar(
        store_sales,
        x="store_name",
        y="line_amount",
        color="store_country" if "store_country" in store_sales.columns else None,
        title="Revenue by Store",
        labels={"line_amount": "Revenue", "store_name": "Store"},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_store.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        legend_title_text="Country",
        title_x=0.02,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        category_sales = (
            filtered.groupby("category", as_index=False)["line_amount"].sum().sort_values("line_amount", ascending=False)
            if "category" in filtered.columns
            else pd.DataFrame({"category": ["N/A"], "line_amount": [0]})
        )
        fig_category = px.pie(
            category_sales,
            names="category",
            values="line_amount",
            title="Revenue Contribution by Category",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_category.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10),
            title_x=0.02,
        )
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.plotly_chart(fig_category, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        status_summary = (
            filtered.groupby("order_status", as_index=False)["order_id"].nunique().sort_values("order_id", ascending=False)
            if {"order_status", "order_id"}.issubset(filtered.columns)
            else pd.DataFrame({"order_status": ["N/A"], "order_id": [0]})
        )
        fig_status = px.bar(
            status_summary,
            x="order_status",
            y="order_id",
            title="Orders by Status",
            labels={"order_id": "Order Count", "order_status": "Status"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_status.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10),
            title_x=0.02,
        )
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        st.plotly_chart(fig_status, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-panel" style="margin-top: 1rem;">', unsafe_allow_html=True)
    st.plotly_chart(fig_store, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top: 1.5rem;">Trend analysis</div>', unsafe_allow_html=True)
    time_sales = (
        filtered.assign(month=filtered["order_timestamp"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)["line_amount"].sum()
        .sort_values("month")
        if "order_timestamp" in filtered.columns
        else pd.DataFrame({"month": ["N/A"], "line_amount": [0]})
    )
    fig_time = px.line(
        time_sales,
        x="month",
        y="line_amount",
        title="Monthly Revenue Trend",
        labels={"line_amount": "Revenue", "month": "Month"},
        template="plotly_white",
        color_discrete_sequence=["#2563eb"],
    )
    fig_time.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        title_x=0.02,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_time, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top: 1.5rem;">Top products</div>', unsafe_allow_html=True)
    top_products = (
        filtered.groupby("product_name", as_index=False)["line_amount"].sum().sort_values("line_amount", ascending=False).head(10)
        if "product_name" in filtered.columns
        else pd.DataFrame({"product_name": ["N/A"], "line_amount": [0]})
    )
    fig_products = px.bar(
        top_products,
        x="line_amount",
        y="product_name",
        orientation="h",
        title="Top Products by Revenue",
        labels={"line_amount": "Revenue", "product_name": "Product"},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig_products.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        title_x=0.02,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(fig_products, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top: 1.5rem;">Data snapshot</div>', unsafe_allow_html=True)
    display_cols = [
        col for col in [
            "order_id",
            "order_item_id",
            "product_id",
            "store_id",
            "employee_id",
            "customer_id",
            "order_timestamp",
            "order_status",
            "total_amount",
            "line_amount",
            "product_name",
            "category",
            "store_name",
            "customer_country",
            "store_country",
        ] if col in filtered.columns
    ]
    st.dataframe(filtered[display_cols].head(10), use_container_width=True)


if __name__ == "__main__":
    main()
