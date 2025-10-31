"""Revenue driver section with trend and category visuals."""

from __future__ import annotations

from typing import List

import plotly.express as px
import pandas as pd
from dash import Input, Output, dcc, html

from dashboard.data import DashboardData
from dashboard.styles import (
    card_style,
    page_wrapper_style,
    summary_badge_style,
    summary_text_style,
)
from dashboard.utils import METRIC_LABELS


def layout(data: DashboardData) -> html.Div:
    """Render revenue drivers page layout."""

    default_metrics = [opt["value"] for opt in data.monthly_metric_options if opt["value"] != "gmv"]

    return html.Div(
        [
            html.Div(
                [
                    html.Span("Monthly pulse", style=summary_badge_style),
                    html.H2(
                        "Revenue trend vs. reputation drag",
                        style={"fontSize": "2.3rem", "color": "#0f172a", "marginBottom": "12px"},
                    ),
                    dcc.Checklist(
                        id="monthly-metric-checklist",
                        options=data.monthly_metric_options,
                        value=default_metrics,
                        inline=True,
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "16px", "fontWeight": "600", "color": "#0f172a"},
                        style={"marginTop": "20px"},
                    ),
                    dcc.Graph(id="monthly-metrics-graph", style={"marginTop": "24px"}),
                    html.P(
                        "Use the legend to focus on the signal first; interpretation follows once the curve is clear.",
                        style={**summary_text_style, "marginTop": "28px"},
                    ),
                ],
                style=card_style,
            ),
            html.Div(
                [
                    html.Span("Category mix", style=summary_badge_style),
                    html.H2(
                        "Where profitability concentrates",
                        style={"fontSize": "2.3rem", "color": "#0f172a", "marginBottom": "12px"},
                    ),
                    html.Div(
                        dcc.Slider(
                            id="category-topn-slider",
                            min=5,
                            max=data.category_slider_max,
                            step=1,
                            value=min(10, data.category_slider_max),
                            marks={i: str(i) for i in range(5, data.category_slider_max + 1, 5)},
                            tooltip={"placement": "bottom"},
                            updatemode="drag",
                        ),
                        style={"marginTop": "28px"},
                    ),
                    dcc.Graph(id="category-profit-graph", style={"marginTop": "24px"}),
                    html.P(
                        "Slide to reveal the leaders, then dive into the narrative on how these categories support gross profit.",
                        style={**summary_text_style, "marginTop": "28px"},
                    ),
                ],
                style=card_style,
            ),
        ],
        style=page_wrapper_style,
    )


def register_callbacks(app, data: DashboardData) -> None:
    """Attach revenue driver callbacks to the Dash app."""

    monthly_metrics_df = data.monthly_metrics.copy()
    category_profitability_df = data.category_profitability.copy()

    @app.callback(
        Output("monthly-metrics-graph", "figure"),
        Input("monthly-metric-checklist", "value"),
    )
    def update_monthly_metrics(selected_metrics: List[str]):
        if not selected_metrics:
            selected_metrics = ["net_revenue"]

        rename_map = {metric: METRIC_LABELS.get(metric, metric) for metric in selected_metrics}
        y_columns = [rename_map[metric] for metric in selected_metrics]

        plot_df = monthly_metrics_df[["month"] + selected_metrics].rename(columns=rename_map)

        fig = px.line(
            plot_df,
            x="month",
            y=y_columns,
            markers=True,
            template="plotly_white",
        )
        fig.update_layout(
            legend_title="Metric",
            yaxis_title="BRL",
            xaxis_title="Month",
            hovermode="x unified",
            font={"size": 16, "family": "Inter, sans-serif"},
        )
        return fig

    @app.callback(
        Output("category-profit-graph", "figure"),
        Input("category-topn-slider", "value"),
    )
    def update_category_profit(top_n: int):
        top_n = max(1, int(top_n))
        limited_df = category_profitability_df.nlargest(top_n, "net_profit").iloc[::-1].copy()
        limited_df["profit_margin"] = (
            limited_df["net_profit"] / limited_df["olist_commission"].replace(0, pd.NA)
        ).fillna(0.0)

        fig = px.bar(
            limited_df,
            x="net_profit",
            y="product_category",
            orientation="h",
            text_auto=".2s",
            hover_data={
                "net_profit": ":,.0f",
                "olist_commission": ":,.0f",
                "reputation_cost": ":,.0f",
                "order_count": True,
                "profit_margin": ":.1%",
            },
            template="plotly_white",
            color="profit_margin",
            color_continuous_scale="Blues",
        )
        fig.update_layout(
            coloraxis_colorbar_title="Profit margin",
            xaxis_title="Net profit (BRL)",
            yaxis_title="Product category",
            margin=dict(l=0, r=20, t=40, b=40),
            font={"size": 16, "family": "Inter, sans-serif"},
        )
        return fig
