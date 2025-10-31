"""Customer trust section with delivery vs satisfaction view."""

from __future__ import annotations

from typing import Dict

import plotly.express as px
from dash import Input, Output, dcc, html

from dashboard.data import DashboardData
from dashboard.styles import (
    card_style,
    page_wrapper_style,
    summary_badge_style,
    summary_text_style,
)


def _spotlight_card(title: str, subtitle: str, colors: Dict[str, str]) -> html.Div:
    return html.Div(
        [
            html.H3(title, style={"fontSize": "1.5rem", "fontWeight": "700", "color": colors["title"]}),
            html.P(subtitle, style={"color": colors["text"], "fontSize": "1rem"}),
        ],
        style={"backgroundColor": colors["background"], "padding": "18px", "borderRadius": "16px"},
    )


def layout(data: DashboardData) -> html.Div:
    """Render the customer trust page with spotlight and scatter plot."""

    spotlight = data.customer_spotlight
    spotlight_boxes = []

    worst_state = spotlight.get("worst_delay")
    best_delay_state = spotlight.get("best_delay")
    best_review_state = spotlight.get("best_review")

    if worst_state:
        spotlight_boxes.append(
            _spotlight_card(
                f"{worst_state['customer_state_name']}: +{worst_state['avg_delay']:.1f} days",
                "Heaviest delivery delays; prioritize logistics review and proactive comms.",
                {"background": "#fee2e2", "title": "#b91c1c", "text": "#991b1b"},
            )
        )
    if best_delay_state:
        spotlight_boxes.append(
            _spotlight_card(
                f"{best_delay_state['customer_state_name']}: {best_delay_state['avg_delay']:.1f} days",
                "Fastest fulfilment; capture learnings for broader rollout.",
                {"background": "#d1fae5", "title": "#047857", "text": "#065f46"},
            )
        )
    if best_review_state:
        spotlight_boxes.append(
            _spotlight_card(
                f"{best_review_state['customer_state_name']}: {best_review_state['avg_review']:.2f} ★",
                "Highest customer advocacy; consider local upsell pilots.",
                {"background": "#bfdbfe", "title": "#0f172a", "text": "#1e293b"},
            )
        )

    slider = data.state_slider

    return html.Div(
        [
            html.Div(
                [
                    html.Span("Customer trust", style=summary_badge_style),
                    html.H2(
                        "Delivery reliability vs. satisfaction",
                        style={"fontSize": "2.3rem", "color": "#0f172a", "marginBottom": "12px"},
                    ),
                    html.Div(
                        spotlight_boxes,
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                            "gap": "18px",
                            "marginTop": "24px",
                        },
                    ),
                    html.Div(
                        dcc.Slider(
                            id="state-min-orders-slider",
                            min=0,
                            max=slider.max,
                            step=slider.step if slider.max else 1,
                            value=slider.default,
                            marks=slider.marks,
                            tooltip={"placement": "bottom"},
                            updatemode="drag",
                        ),
                        style={"marginTop": "32px"},
                    ),
                    dcc.Graph(id="state-delay-review-graph", style={"marginTop": "28px"}),
                    html.P(
                        "After spotting the outliers, review the guidance below to align ops, CX, and finance priorities.",
                        style={**summary_text_style, "marginTop": "28px"},
                    ),
                ],
                style=card_style,
            ),
        ],
        style=page_wrapper_style,
    )


def register_callbacks(app, data: DashboardData) -> None:
    """Attach customer trust callbacks to the Dash app."""

    state_metrics_df = data.state_metrics.copy()

    @app.callback(
        Output("state-delay-review-graph", "figure"),
        Input("state-min-orders-slider", "value"),
    )
    def update_state_scatter(min_orders: int):
        min_orders = 0 if min_orders is None else int(min_orders)
        filtered = state_metrics_df[state_metrics_df["order_count"] >= min_orders].copy()

        if filtered.empty:
            filtered = state_metrics_df.nlargest(10, "order_count").copy()

        fig = px.scatter(
            filtered,
            x="avg_delay",
            y="avg_review",
            size="olist_commission",
            color="avg_delay",
            hover_name="customer_state_name",
            hover_data={
                "avg_delay": ":.1f",
                "avg_review": ":.2f",
                "order_count": True,
                "olist_commission": ":,.0f",
            },
            template="plotly_white",
            color_continuous_scale="RdYlGn_r",
        )
        fig.update_layout(
            coloraxis_colorbar_title="Avg delay (days)",
            xaxis_title="Average delivery delay (days)",
            yaxis_title="Average review score",
            yaxis=dict(range=[2.5, 5.1]),
            font={"size": 16, "family": "Inter, sans-serif"},
        )
        return fig
