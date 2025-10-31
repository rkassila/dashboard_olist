"""Executive overview page layout."""

from __future__ import annotations

from dash import dcc, html

from dashboard.data import DashboardData
from dashboard.styles import (
    card_style,
    create_kpi_card,
    kpi_grid_style,
    page_wrapper_style,
    summary_badge_style,
    summary_text_style,
)
from dashboard.utils import format_brl, format_percent


def layout(data: DashboardData) -> html.Div:
    """Render the executive overview with financial KPIs and waterfall chart."""

    financials = data.financial_overview
    rev_sales = financials["revenues_sales"]
    rev_subscriptions = financials["revenues_subscription"]
    dominant_stream = "Sales fees" if rev_sales >= rev_subscriptions else "Subscriptions"
    dominant_value = max(rev_sales, rev_subscriptions)
    other_value = min(rev_sales, rev_subscriptions)

    kpi_cards = html.Div(
        [
            create_kpi_card(
                "Total revenue",
                format_brl(financials["revenues_total"]),
                "Past 16 months cumulative",
            ),
            create_kpi_card(
                "Net profit",
                format_brl(financials["profits_net"]),
                "After reputation and IT costs",
            ),
            create_kpi_card(
                "Net margin",
                format_percent(financials["margin"]),
                "Net profit / revenue",
            ),
            create_kpi_card(
                "Active sellers",
                f"{financials['seller_count']:,}",
                "Onboarded during the period",
            ),
        ],
        style=kpi_grid_style,
    )

    insight_copy = html.Div(
        [
            html.Span("Executive focus", style=summary_badge_style),
            html.P(
                (
                    f"{dominant_stream} now contribute {format_brl(dominant_value)}, "
                    f"compared with {format_brl(other_value)} from the complementary stream."
                ),
                style=summary_text_style,
            ),
            html.P(
                (
                    f"Reputation costs eroded {format_brl(financials['costs_reviews'])} of earnings, "
                    "underscoring the need to keep delivery promises tight."
                ),
                style=summary_text_style,
            ),
        ],
        style={"marginTop": "32px"},
    )

    return html.Div(
        [
            kpi_cards,
            html.Div(
                [
                    dcc.Graph(figure=data.waterfall_figure, style={"height": "520px"}),
                    insight_copy,
                ],
                style=card_style,
            ),
        ],
        style=page_wrapper_style,
    )
