"""CEO action page summarising next steps."""

from __future__ import annotations

from typing import List

from dash import html

from dashboard.data import DashboardData
from dashboard.styles import (
    card_style,
    create_kpi_card,
    kpi_grid_style,
    page_wrapper_style,
    recommendation_item_style,
    recommendation_list_style,
    summary_badge_style,
)
from dashboard.utils import format_brl, format_category_name, format_percent


def _format_revenue_trend(change: float) -> str:
    abs_change = abs(change)
    if change > 0:
        return f"▲ {format_brl(abs_change)} vs. last month"
    if change < 0:
        return f"▼ {format_brl(abs_change)} vs. last month"
    return "Flat vs. last month"


def layout(data: DashboardData) -> html.Div:
    """Render the CEO next steps page."""

    top_category_labels = [format_category_name(name) for name in data.top_category_names]
    if len(top_category_labels) > 1:
        categories_text = ", ".join(top_category_labels[:-1]) + f" and {top_category_labels[-1]}"
    elif top_category_labels:
        categories_text = top_category_labels[0]
    else:
        categories_text = "key categories"

    revenue_trend_text = _format_revenue_trend(data.net_revenue_change)
    profit_phrase = (
        f"unlocks {format_brl(data.profit_uplift)} incremental profit"
        if data.profit_uplift >= 0
        else f"reduces profit by {format_brl(abs(data.profit_uplift))}"
    )
    margin_phrase = (
        f"Margin would move from {format_percent(data.baseline_strategy['margin'])} to {format_percent(data.margin_strategy['margin'])}"
        if data.margin_uplift >= 0
        else f"Margin would decline by {format_percent(abs(data.margin_uplift))}"
    )

    key_numbers = html.Div(
        [
            create_kpi_card(
                "Latest monthly net revenue",
                format_brl(data.latest_net_revenue),
                revenue_trend_text,
            ),
            create_kpi_card(
                "Profit uplift on table",
                format_brl(data.profit_uplift),
                f"Remove {int(data.profit_strategy['sellers_removed']):,} low performers",
            ),
            create_kpi_card(
                "Lean margin scenario",
                format_percent(data.margin_strategy["margin"]),
                margin_phrase,
            ),
        ],
        style=kpi_grid_style,
    )

    recommendations: List[html.Li] = []

    recommendations.append(
        html.Li(
            (
                f"Keep revenue momentum: {format_brl(data.latest_net_revenue)} in the latest month "
                f"({revenue_trend_text}). Lock the growth calendar with marketing and CRM leads before discussing trade-offs."
            ),
            style=recommendation_item_style,
        )
    )

    worst_state = data.customer_spotlight.get("worst_delay")
    best_delay_state = data.customer_spotlight.get("best_delay")
    if worst_state and best_delay_state:
        recommendations.append(
            html.Li(
                (
                    f"Stabilize delivery promise in {worst_state['customer_state_name']} (currently +{worst_state['avg_delay']:.1f} days) "
                    f"by applying the playbook from {best_delay_state['customer_state_name']} (at {best_delay_state['avg_delay']:.1f} days)."
                ),
                style=recommendation_item_style,
            )
        )

    recommendations.append(
        html.Li(
            (
                f"Double down on hero categories: {categories_text} deliver {format_brl(data.top_category_profit)} net profit after reputation costs. "
                "Align merchandising, paid media, and supply ops on this shortlist."
            ),
            style=recommendation_item_style,
        )
    )

    recommendations.append(
        html.Li(
            (
                f"Initiate the pruning plan: removing {int(data.profit_strategy['sellers_removed']):,} underperforming sellers {profit_phrase} "
                f"while keeping {int(data.profit_strategy['sellers_remaining']):,} partners engaged."
            ),
            style=recommendation_item_style,
        )
    )

    best_review_state = data.customer_spotlight.get("best_review")
    if best_review_state:
        recommendations.append(
            html.Li(
                (
                    f"Amplify promoters: {best_review_state['customer_state_name']} averages {best_review_state['avg_review']:.2f}★. "
                    "Capture the CX rituals there and export them to the delayed states."
                ),
                style=recommendation_item_style,
            )
        )

    actions_block = html.Div(
        [
            html.Span("Recommended next steps", style=summary_badge_style),
            html.H2("CEO action plan", style={"fontSize": "2.6rem", "color": "#0f172a", "marginBottom": "16px"}),
            html.Ol(recommendations, style=recommendation_list_style),
        ],
        style=card_style,
    )

    return html.Div(
        [
            key_numbers,
            actions_block,
        ],
        style=page_wrapper_style,
    )
