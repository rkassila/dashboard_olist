"""Shared style definitions for the Olist dashboard."""

from __future__ import annotations

from typing import Dict, List

from dash import html


NAV_ITEMS: List[Dict[str, str]] = [
    {"label": "Executive Overview", "path": "/"},
    {"label": "Revenue Drivers", "path": "/drivers"},
    {"label": "Customer Trust", "path": "/customers"},
    {"label": "Seller Strategy", "path": "/strategy"},
    {"label": "CEO Next Moves", "path": "/actions"},
]


container_style: Dict[str, str] = {
    "backgroundColor": "#0f172a",
    "minHeight": "100vh",
    "padding": "32px 0 48px",
    "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
}

content_wrapper_style: Dict[str, str] = {
    "maxWidth": "1200px",
    "margin": "0 auto",
    "padding": "0 32px",
}

header_style: Dict[str, str] = {
    "color": "#f8fafc",
    "marginBottom": "32px",
}

hero_title_style: Dict[str, str] = {
    "fontSize": "3.6rem",
    "fontWeight": "700",
    "marginBottom": "0.5rem",
}

hero_text_style: Dict[str, str] = {
    "fontSize": "1.35rem",
    "maxWidth": "780px",
    "lineHeight": "1.6",
    "color": "rgba(248, 250, 252, 0.85)",
}

nav_style: Dict[str, str] = {
    "display": "flex",
    "gap": "16px",
    "flexWrap": "wrap",
    "marginTop": "24px",
}

nav_link_style: Dict[str, str] = {
    "padding": "10px 18px",
    "borderRadius": "999px",
    "backgroundColor": "rgba(15, 23, 42, 0.25)",
    "color": "#f8fafc",
    "textDecoration": "none",
    "fontWeight": "600",
    "fontSize": "0.95rem",
}

nav_link_active_style: Dict[str, str] = {
    **nav_link_style,
    "backgroundColor": "#38bdf8",
    "color": "#0f172a",
}

page_wrapper_style: Dict[str, str] = {
    "backgroundColor": "#f8fafc",
    "borderRadius": "24px",
    "padding": "40px",
    "boxShadow": "0 25px 50px -12px rgba(15, 23, 42, 0.35)",
}

kpi_grid_style: Dict[str, str] = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
    "gap": "24px",
    "marginBottom": "32px",
}

kpi_card_style: Dict[str, str] = {
    "backgroundColor": "#0f172a",
    "color": "#f8fafc",
    "padding": "24px",
    "borderRadius": "20px",
    "boxShadow": "0 10px 30px rgba(15, 23, 42, 0.4)",
}

kpi_value_style: Dict[str, str] = {
    "fontSize": "3.4rem",
    "fontWeight": "700",
    "marginBottom": "4px",
}

kpi_label_style: Dict[str, str] = {
    "fontSize": "1.05rem",
    "letterSpacing": "0.08em",
    "textTransform": "uppercase",
    "color": "rgba(248, 250, 252, 0.75)",
}

card_style: Dict[str, str] = {
    "backgroundColor": "#ffffff",
    "padding": "32px",
    "marginBottom": "32px",
    "borderRadius": "20px",
    "boxShadow": "0 18px 35px rgba(15, 23, 42, 0.12)",
}

summary_badge_style: Dict[str, str] = {
    "display": "inline-block",
    "padding": "6px 14px",
    "borderRadius": "999px",
    "backgroundColor": "#e0f2fe",
    "color": "#0f172a",
    "fontWeight": "600",
    "fontSize": "0.95rem",
    "marginBottom": "12px",
}

summary_text_style: Dict[str, str] = {
    "fontSize": "1.25rem",
    "lineHeight": "1.75",
    "color": "#1e293b",
}

strategy_summary_style: Dict[str, str] = {
    "backgroundColor": "#0f172a",
    "color": "#f8fafc",
    "padding": "24px",
    "borderRadius": "18px",
    "marginTop": "24px",
    "boxShadow": "0 12px 24px rgba(15, 23, 42, 0.35)",
}

page_content_style: Dict[str, str] = {"marginTop": "0"}

footer_style: Dict[str, str] = {
    "color": "rgba(248, 250, 252, 0.75)",
    "fontSize": "0.85rem",
    "marginTop": "48px",
    "textAlign": "center",
}

recommendation_list_style: Dict[str, str] = {
    "fontSize": "1.35rem",
    "lineHeight": "1.9",
    "color": "#0f172a",
    "paddingLeft": "1.25em",
    "marginTop": "12px",
}

recommendation_item_style: Dict[str, str] = {
    "padding": "10px 0",
}


def create_kpi_card(label: str, value: str, subtitle: str) -> html.Div:
    """Generate a styled KPI card for dashboard header sections."""

    return html.Div(
        [
            html.Div(value, style=kpi_value_style),
            html.Div(label, style=kpi_label_style),
            html.Div(subtitle, style={"fontSize": "0.95rem", "color": "rgba(248, 250, 252, 0.75)"}),
        ],
        style=kpi_card_style,
    )
