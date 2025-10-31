"""Data loading and aggregation helpers for the Olist dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from olist.data import Olist
from olist.seller_updated import Seller

from .utils import METRIC_LABELS, STATE_NAME_MAP, format_brl


COMMISSION_RATE = 0.10
SUBSCRIPTION_FEE = 80
ALPHA_IT = 3157.27
BETA_IT = 978.23
COST_MAP: Dict[int, int] = {1: 100, 2: 50, 3: 40, 4: 0, 5: 0}


@dataclass(frozen=True)
class SliderConfig:
    max: int
    marks: Dict[int, str]
    default: int
    step: int


@dataclass(frozen=True)
class DashboardData:
    financial_overview: Dict[str, float]
    waterfall_figure: go.Figure
    monthly_metrics: pd.DataFrame
    category_profitability: pd.DataFrame
    category_slider_max: int
    monthly_metric_options: List[Dict[str, str]]
    state_metrics: pd.DataFrame
    state_slider: SliderConfig
    customer_spotlight: Dict[str, Dict[str, Any]]
    strategy_df: pd.DataFrame
    strategy_highlights: Dict[str, Dict[str, float]]
    strategy_slider: SliderConfig
    top_category_names: List[str]
    top_category_profit: float
    latest_net_revenue: float
    net_revenue_change: float
    baseline_strategy: Dict[str, float]
    profit_strategy: Dict[str, float]
    margin_strategy: Dict[str, float]
    profit_uplift: float
    margin_uplift: float


def prepare_base_frames(
    orders_df: pd.DataFrame,
    order_items_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return delivered orders, delivered order_items and per-order reputation costs."""

    delivered_orders = orders_df[orders_df["order_status"] == "delivered"].copy()
    delivered_orders = delivered_orders[
        [
            "order_id",
            "customer_id",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]
    ]

    order_items_delivered = order_items_df[
        order_items_df["order_id"].isin(delivered_orders["order_id"])
    ].copy()

    reviews_clean = reviews_df[["order_id", "review_score"]].dropna().copy()
    reviews_clean["review_score"] = reviews_clean["review_score"].astype(int)
    reviews_clean["reputation_cost"] = reviews_clean["review_score"].map(COST_MAP)
    order_cost = (
        reviews_clean.groupby("order_id", as_index=False)["reputation_cost"].max()
    )

    return delivered_orders, order_items_delivered, order_cost


def compute_monthly_metrics(
    delivered_orders: pd.DataFrame,
    order_items_delivered: pd.DataFrame,
    order_cost: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate monthly GMV, revenue streams and reputation costs."""

    items_with_purchase = order_items_delivered.merge(
        delivered_orders[["order_id", "order_purchase_timestamp"]],
        on="order_id",
        how="left",
    )
    items_with_purchase["month"] = (
        items_with_purchase["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    )

    monthly = (
        items_with_purchase.groupby("month", as_index=False)
        .agg(
            gross_sales=("price", "sum"),
            freight=("freight_value", "sum"),
            active_sellers=("seller_id", "nunique"),
        )
        .sort_values("month")
    )

    monthly["gmv"] = monthly["gross_sales"] + monthly["freight"]
    monthly["olist_commission"] = monthly["gross_sales"] * COMMISSION_RATE
    monthly["subscription_revenue"] = monthly["active_sellers"] * SUBSCRIPTION_FEE
    monthly["olist_revenue"] = monthly["olist_commission"] + monthly["subscription_revenue"]

    monthly_cost = delivered_orders[["order_id", "order_purchase_timestamp"]].merge(
        order_cost, on="order_id", how="left"
    )
    monthly_cost["reputation_cost"] = monthly_cost["reputation_cost"].fillna(0.0)
    monthly_cost["month"] = (
        monthly_cost["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    )
    monthly_cost = monthly_cost.groupby("month", as_index=False)["reputation_cost"].sum()

    monthly = monthly.merge(monthly_cost, on="month", how="left")
    monthly["reputation_cost"] = monthly["reputation_cost"].fillna(0.0)
    monthly["net_revenue"] = monthly["olist_revenue"] - monthly["reputation_cost"]

    return monthly


def compute_category_profitability(
    order_items_delivered: pd.DataFrame,
    products_df: pd.DataFrame,
    translations_df: pd.DataFrame,
    order_cost: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate commission, allocated reputation costs and profit by category."""

    items = order_items_delivered.merge(
        products_df[["product_id", "product_category_name"]],
        on="product_id",
        how="left",
    )

    translation_map = translations_df.set_index("product_category_name")[
        "product_category_name_english"
    ]
    items["product_category"] = items["product_category_name"].map(translation_map)
    items["product_category"] = items["product_category"].fillna(
        items["product_category_name"]
    )
    items["product_category"] = items["product_category"].fillna("Unknown")

    items["order_price_total"] = items.groupby("order_id")["price"].transform("sum")
    denominator = items["order_price_total"].replace(0, pd.NA)
    items["price_share"] = (items["price"] / denominator).fillna(0.0)

    cost_series = order_cost.set_index("order_id")["reputation_cost"]
    items["order_reputation_cost"] = items["order_id"].map(cost_series).fillna(0.0)
    items["reputation_cost_allocated"] = (
        items["price_share"] * items["order_reputation_cost"]
    )

    category = items.groupby("product_category", as_index=False).agg(
        gross_sales=("price", "sum"),
        reputation_cost=("reputation_cost_allocated", "sum"),
        order_count=("order_id", "nunique"),
    )
    category["olist_commission"] = category["gross_sales"] * COMMISSION_RATE
    category["net_profit"] = category["olist_commission"] - category["reputation_cost"]

    category = category.sort_values("net_profit", ascending=False)
    return category


def compute_state_metrics(
    delivered_orders: pd.DataFrame,
    order_items_delivered: pd.DataFrame,
    customers_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute delivery delay and satisfaction metrics per customer state."""

    order_sales = order_items_delivered.groupby("order_id")["price"].sum()

    orders = delivered_orders.merge(
        customers_df[["customer_id", "customer_state"]],
        on="customer_id",
        how="left",
    )
    orders["order_gross_sales"] = orders["order_id"].map(order_sales).fillna(0.0)
    orders["order_olist_commission"] = orders["order_gross_sales"] * COMMISSION_RATE

    reviews_scores = (
        reviews_df[["order_id", "review_score"]]
        .dropna()
        .groupby("order_id", as_index=False)["review_score"].mean()
    )
    orders = orders.merge(reviews_scores, on="order_id", how="left")

    orders["delivery_delay"] = (
        orders["order_delivered_customer_date"]
        - orders["order_estimated_delivery_date"]
    ).dt.days
    orders = orders.dropna(subset=["customer_state"])
    orders["delivery_delay"] = orders["delivery_delay"].fillna(0.0)

    state_metrics = orders.groupby("customer_state", as_index=False).agg(
        avg_delay=("delivery_delay", "mean"),
        avg_review=("review_score", "mean"),
        order_count=("order_id", "nunique"),
        olist_commission=("order_olist_commission", "sum"),
    )
    state_metrics = state_metrics.dropna(subset=["avg_review"])
    state_metrics = state_metrics.sort_values("order_count", ascending=False)
    state_metrics["customer_state_name"] = state_metrics["customer_state"].map(STATE_NAME_MAP).fillna(
        state_metrics["customer_state"]
    )
    return state_metrics


def compute_financial_overview(sellers_df: pd.DataFrame) -> Dict[str, float]:
    revenues_sales = sellers_df["sales"].sum() * COMMISSION_RATE
    revenues_subscription = sellers_df["months_on_olist"].sum() * SUBSCRIPTION_FEE
    revenues_total = sellers_df["revenues"].sum()

    costs_reviews = sellers_df["cost_of_reviews"].sum()
    seller_count = sellers_df.shape[0]
    item_count = sellers_df["quantity"].sum()
    costs_it = ALPHA_IT * np.sqrt(seller_count) + BETA_IT * np.sqrt(item_count)

    profits_gross = sellers_df["profits"].sum()
    profits_net = profits_gross - costs_it
    margin = profits_net / revenues_total if revenues_total else 0.0

    return {
        "revenues_sales": revenues_sales,
        "revenues_subscription": revenues_subscription,
        "revenues_total": revenues_total,
        "costs_reviews": costs_reviews,
        "costs_it": costs_it,
        "profits_gross": profits_gross,
        "profits_net": profits_net,
        "margin": margin,
        "seller_count": seller_count,
        "item_count": item_count,
    }


def build_waterfall_figure(financials: Dict[str, float]) -> go.Figure:
    measure = [
        "relative",
        "relative",
        "total",
        "relative",
        "total",
        "relative",
        "total",
    ]
    x = [
        "Subscriptions",
        "Sales fees",
        "Total revenues",
        "Review costs",
        "Gross profit",
        "IT costs",
        "Net profit",
    ]
    y = [
        financials["revenues_subscription"],
        financials["revenues_sales"],
        0,
        -financials["costs_reviews"],
        0,
        -financials["costs_it"],
        0,
    ]
    text = [
        format_brl(financials["revenues_subscription"]),
        format_brl(financials["revenues_sales"]),
        format_brl(financials["revenues_total"]),
        format_brl(-financials["costs_reviews"]),
        format_brl(financials["profits_gross"]),
        format_brl(-financials["costs_it"]),
        format_brl(financials["profits_net"]),
    ]

    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=measure,
            x=x,
            y=y,
            text=text,
            textposition="outside",
            connector={"line": {"color": "#222"}},
        )
    )

    fig.update_layout(
        title={
            "text": "Full-Year Profit & Loss (BRL)",
            "font": {"size": 32, "color": "#0b1b40"},
            "x": 0.0,
            "y": 0.95,
        },
        margin=dict(l=40, r=40, t=80, b=40),
        template="plotly_white",
        yaxis_title="BRL",
    )
    return fig


def prepare_seller_strategy_data(
    sellers_df: pd.DataFrame,
) -> tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    sorted_sellers = sellers_df.sort_values(by="profits").reset_index(drop=True)
    n_sellers = sorted_sellers.shape[0]

    revenues_total = sellers_df["revenues"].sum()
    review_costs_total = sellers_df["cost_of_reviews"].sum()
    gross_profits_total = sellers_df["profits"].sum()
    items_total = sellers_df["quantity"].sum()

    base_it_cost = ALPHA_IT * np.sqrt(n_sellers) + BETA_IT * np.sqrt(items_total)
    base_net_profit = gross_profits_total - base_it_cost
    base_margin = base_net_profit / revenues_total if revenues_total else 0.0

    records = [
        {
            "sellers_removed": 0,
            "sellers_remaining": n_sellers,
            "revenues": revenues_total,
            "review_costs": review_costs_total,
            "it_costs": base_it_cost,
            "total_costs": review_costs_total + base_it_cost,
            "net_profit": base_net_profit,
            "margin": base_margin,
        }
    ]

    if n_sellers > 1:
        steps = np.arange(1, n_sellers, dtype=int)

        profits_after = gross_profits_total - np.cumsum(sorted_sellers["profits"].values[:-1])
        review_costs_after = review_costs_total - np.cumsum(
            sorted_sellers["cost_of_reviews"].values[:-1]
        )
        revenues_after = revenues_total - np.cumsum(sorted_sellers["revenues"].values[:-1])
        items_after = items_total - np.cumsum(sorted_sellers["quantity"].values[:-1])
        sellers_remaining = n_sellers - steps

        it_costs_after = ALPHA_IT * np.sqrt(sellers_remaining) + BETA_IT * np.sqrt(items_after)
        total_costs_after = review_costs_after + it_costs_after
        net_profit_after = profits_after - it_costs_after
        margin_after = np.divide(
            net_profit_after,
            revenues_after,
            out=np.zeros_like(net_profit_after, dtype=float),
            where=revenues_after != 0,
        )

        for idx, step in enumerate(steps):
            records.append(
                {
                    "sellers_removed": int(step),
                    "sellers_remaining": int(sellers_remaining[idx]),
                    "revenues": float(revenues_after[idx]),
                    "review_costs": float(review_costs_after[idx]),
                    "it_costs": float(it_costs_after[idx]),
                    "total_costs": float(total_costs_after[idx]),
                    "net_profit": float(net_profit_after[idx]),
                    "margin": float(margin_after[idx]),
                }
            )

    strategy_df = pd.DataFrame(records)
    highlights = {
        "baseline": strategy_df.iloc[0].to_dict(),
        "max_profit": strategy_df.loc[strategy_df["net_profit"].idxmax()].to_dict(),
        "max_margin": strategy_df.loc[strategy_df["margin"].idxmax()].to_dict(),
    }

    return strategy_df, highlights


def _build_slider_marks(max_value: int, step_hint: int) -> Dict[int, str]:
    marks: Dict[int, str] = {}
    if max_value <= 10:
        marks = {i: str(i) for i in range(0, max_value + 1)}
    else:
        for value in range(0, max_value + 1, step_hint):
            marks[value] = str(value)

    if max_value not in marks and max_value > 0:
        marks[max_value] = str(max_value)
    return marks


def load_dashboard_data() -> DashboardData:
    """Compute every dataset required by the dashboard and return a single payload."""

    olist_data = Olist().get_data()

    orders_df = olist_data["orders"].copy()
    for column in [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]:
        orders_df[column] = pd.to_datetime(orders_df[column])

    order_items_df = olist_data["order_items"].copy()
    order_items_df["shipping_limit_date"] = pd.to_datetime(
        order_items_df["shipping_limit_date"]
    )

    reviews_df = olist_data["order_reviews"].copy()
    products_df = olist_data["products"].copy()
    translations_df = olist_data["product_category_name_translation"].copy()
    customers_df = olist_data["customers"].copy()

    delivered_orders_df, order_items_delivered_df, order_cost_df = prepare_base_frames(
        orders_df, order_items_df, reviews_df
    )

    monthly_metrics_df = compute_monthly_metrics(
        delivered_orders_df, order_items_delivered_df, order_cost_df
    )
    category_profitability_df = compute_category_profitability(
        order_items_delivered_df, products_df, translations_df, order_cost_df
    )
    state_metrics_df = compute_state_metrics(
        delivered_orders_df, order_items_delivered_df, customers_df, reviews_df
    )

    seller_df = Seller().get_training_data()
    financial_overview = compute_financial_overview(seller_df)
    waterfall_figure = build_waterfall_figure(financial_overview)
    strategy_df, strategy_highlights = prepare_seller_strategy_data(seller_df)

    category_slider_max = max(5, min(20, len(category_profitability_df)))

    max_state_orders = int(state_metrics_df["order_count"].max()) if not state_metrics_df.empty else 0
    state_step = 50 if max_state_orders >= 400 else 10
    state_marks = _build_slider_marks(max_state_orders, state_step)
    default_state_threshold = min(500, max_state_orders) if max_state_orders else 0
    state_slider = SliderConfig(
        max=max_state_orders,
        marks=state_marks,
        default=default_state_threshold,
        step=state_step,
    )

    if not state_metrics_df.empty:
        worst_delay_state = state_metrics_df.sort_values("avg_delay", ascending=False).iloc[0].to_dict()
        best_delay_state = state_metrics_df.sort_values("avg_delay", ascending=True).iloc[0].to_dict()
        best_review_state = state_metrics_df.sort_values("avg_review", ascending=False).iloc[0].to_dict()
        customer_spotlight = {
            "worst_delay": worst_delay_state,
            "best_delay": best_delay_state,
            "best_review": best_review_state,
        }
    else:
        customer_spotlight = {"worst_delay": None, "best_delay": None, "best_review": None}

    strategy_slider_max = int(strategy_df["sellers_removed"].max()) if not strategy_df.empty else 0
    strategy_step = 50 if strategy_slider_max >= 400 else 10
    strategy_marks = _build_slider_marks(strategy_slider_max, strategy_step)
    strategy_default_value = (
        int(strategy_highlights["max_profit"]["sellers_removed"])
        if strategy_slider_max
        else 0
    )
    strategy_slider = SliderConfig(
        max=strategy_slider_max,
        marks=strategy_marks,
        default=strategy_default_value,
        step=strategy_step,
    )

    top_categories = category_profitability_df.head(3)
    top_category_names = top_categories["product_category"].tolist()
    top_category_profit = float(top_categories["net_profit"].sum()) if not top_categories.empty else 0.0

    monthly_sorted = monthly_metrics_df.sort_values("month")
    if len(monthly_sorted) >= 2:
        last_month_row = monthly_sorted.iloc[-1]
        prev_month_row = monthly_sorted.iloc[-2]
        latest_net_revenue = float(last_month_row["net_revenue"])
        net_revenue_change = float(last_month_row["net_revenue"] - prev_month_row["net_revenue"])
    elif not monthly_sorted.empty:
        latest_net_revenue = float(monthly_sorted.iloc[-1]["net_revenue"])
        net_revenue_change = 0.0
    else:
        latest_net_revenue = 0.0
        net_revenue_change = 0.0

    baseline_strategy = strategy_highlights["baseline"]
    profit_strategy = strategy_highlights["max_profit"]
    margin_strategy = strategy_highlights["max_margin"]
    profit_uplift = float(profit_strategy["net_profit"] - baseline_strategy["net_profit"])
    margin_uplift = float(margin_strategy["margin"] - baseline_strategy["margin"])

    monthly_metric_options = [
        {"label": label, "value": key} for key, label in METRIC_LABELS.items()
    ]

    return DashboardData(
        financial_overview=financial_overview,
        waterfall_figure=waterfall_figure,
        monthly_metrics=monthly_metrics_df,
        category_profitability=category_profitability_df,
        category_slider_max=category_slider_max,
        monthly_metric_options=monthly_metric_options,
        state_metrics=state_metrics_df,
        state_slider=state_slider,
        customer_spotlight=customer_spotlight,
        strategy_df=strategy_df,
        strategy_highlights=strategy_highlights,
        strategy_slider=strategy_slider,
        top_category_names=top_category_names,
        top_category_profit=top_category_profit,
        latest_net_revenue=latest_net_revenue,
        net_revenue_change=net_revenue_change,
        baseline_strategy=baseline_strategy,
        profit_strategy=profit_strategy,
        margin_strategy=margin_strategy,
        profit_uplift=profit_uplift,
        margin_uplift=margin_uplift,
    )
