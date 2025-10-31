"""Seller strategy what-if analysis section."""

from __future__ import annotations

import plotly.express as px
import pandas as pd
from dash import Input, Output, dcc, html

from dashboard.data import DashboardData
from dashboard.styles import (
    card_style,
    create_kpi_card,
    kpi_grid_style,
    page_wrapper_style,
    strategy_summary_style,
    summary_badge_style,
    summary_text_style,
)
from dashboard.utils import format_brl, format_percent


def layout(data: DashboardData) -> html.Div:
    """Render the seller strategy what-if analysis."""

    profit_highlight = data.strategy_highlights["max_profit"]
    margin_highlight = data.strategy_highlights["max_margin"]
    slider = data.strategy_slider

    highlight_cards = html.Div(
        [
            create_kpi_card(
                "Profit-max scenario",
                f"+{format_brl(profit_highlight['net_profit'])}",
                f"Remove {int(profit_highlight['sellers_removed']):,} sellers (retain {int(profit_highlight['sellers_remaining']):,})",
            ),
            create_kpi_card(
                "Margin-max scenario",
                format_percent(margin_highlight["margin"]),
                f"Remove {int(margin_highlight['sellers_removed']):,} sellers",
            ),
        ],
        style=kpi_grid_style,
    )

    return html.Div(
        [
            highlight_cards,
            html.Div(
                [
                    html.Span("Scenario planning", style=summary_badge_style),
                    html.H2(
                        "What if we trim long-tail sellers?",
                        style={"fontSize": "2.3rem", "color": "#0f172a", "marginBottom": "12px"},
                    ),
                    html.Div(
                        dcc.Slider(
                            id="seller-strategy-slider",
                            min=0,
                            max=slider.max,
                            step=slider.step if slider.max else 1,
                            value=slider.default,
                            marks=slider.marks,
                            tooltip={"placement": "bottom"},
                            updatemode="drag",
                        ),
                        style={"marginTop": "28px"},
                    ),
                    dcc.Graph(id="seller-strategy-graph", style={"marginTop": "28px"}),
                    html.P(
                        "Once the preferred scenario is visible, use the panel below to brief the exec team.",
                        style={**summary_text_style, "marginTop": "28px"},
                    ),
                    html.Div(id="seller-strategy-summary", style=strategy_summary_style),
                ],
                style=card_style,
            ),
        ],
        style=page_wrapper_style,
    )


def register_callbacks(app, data: DashboardData) -> None:
    """Attach seller strategy callbacks to the Dash app."""

    strategy_df = data.strategy_df.copy()
    highlights = data.strategy_highlights

    @app.callback(
        Output("seller-strategy-graph", "figure"),
        Output("seller-strategy-summary", "children"),
        Input("seller-strategy-slider", "value"),
    )
    def update_seller_strategy(selected_value: int | float):
        if strategy_df.empty:
            return px.line(), html.Div("Seller analytics unavailable.", style={"fontSize": "1rem"})

        selected = 0 if selected_value is None else int(selected_value)
        if selected not in strategy_df["sellers_removed"].values:
            nearest_idx = (strategy_df["sellers_removed"] - selected).abs().idxmin()
            selected_row = strategy_df.loc[nearest_idx]
            selected = int(selected_row["sellers_removed"])
        else:
            selected_row = strategy_df.loc[strategy_df["sellers_removed"] == selected].iloc[0]

        plot_df = strategy_df.melt(
            id_vars=["sellers_removed"],
            value_vars=["net_profit", "revenues", "total_costs"],
            var_name="Metric",
            value_name="BRL",
        )

        fig = px.line(
            plot_df,
            x="sellers_removed",
            y="BRL",
            color="Metric",
            template="plotly_white",
            markers=True,
            color_discrete_map={
                "net_profit": "#2563eb",
                "revenues": "#14b8a6",
                "total_costs": "#f97316",
            },
        )
        fig.add_vline(
            x=selected,
            line_dash="dash",
            line_color="#f97316",
            annotation_text="Scenario",
            annotation_position="top right",
        )
        fig.update_layout(
            title={"text": "Financial impact by sellers removed", "x": 0.02, "font": {"size": 22}},
            xaxis_title="Sellers removed",
            yaxis_title="BRL",
            legend_title="",
            hovermode="x unified",
            font={"size": 16, "family": "Inter, sans-serif"},
        )

        profit_highlight = highlights["max_profit"]
        margin_highlight = highlights["max_margin"]

        summary_children = [
            html.H3(
                f"Scenario: remove {selected:,} sellers",
                style={"marginBottom": "8px", "fontSize": "1.6rem", "fontWeight": "700"},
            ),
            html.P(
                f"Net profit: {format_brl(selected_row['net_profit'])}",
                style={"fontSize": "1.1rem"},
            ),
            html.P(
                f"Revenue retained: {format_brl(selected_row['revenues'])}",
                style={"fontSize": "1.1rem"},
            ),
            html.P(
                f"Total costs: {format_brl(selected_row['total_costs'])}",
                style={"fontSize": "1.1rem"},
            ),
            html.P(
                f"Remaining sellers: {int(selected_row['sellers_remaining']):,}",
                style={"fontSize": "1.1rem"},
            ),
            html.P(
                f"Net margin: {format_percent(selected_row['margin'])}",
                style={"fontSize": "1.1rem"},
            ),
            html.Hr(style={"borderColor": "rgba(248, 250, 252, 0.2)", "margin": "20px 0"}),
            html.P(
                (
                    f"Profit-max: remove {int(profit_highlight['sellers_removed']):,} sellers "
                    f"→ {format_brl(profit_highlight['net_profit'])} net profit."
                ),
                style={"fontSize": "1rem"},
            ),
            html.P(
                (
                    f"Margin-max: remove {int(margin_highlight['sellers_removed']):,} sellers "
                    f"→ margin {format_percent(margin_highlight['margin'])}."
                ),
                style={"fontSize": "1rem"},
            ),
        ]

        return fig, summary_children
