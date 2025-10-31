"""Dash entry point assembling multi-page CEO dashboard."""

from __future__ import annotations

from dash import Dash, Input, Output, dcc, html

from dashboard.data import load_dashboard_data
from dashboard.styles import (
    NAV_ITEMS,
    card_style,
    container_style,
    content_wrapper_style,
    footer_style,
    header_style,
    hero_text_style,
    hero_title_style,
    nav_link_active_style,
    nav_link_style,
    nav_style,
    page_content_style,
    page_wrapper_style,
    summary_text_style,
)
from sections import actions, customer_trust, overview, revenue_drivers, seller_strategy


# Prepare all data at start-up (expensive operations happen once).
dashboard_data = load_dashboard_data()

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Olist CFO Dashboard"
server = app.server


# Register interactive callbacks supplied by dedicated sections.
revenue_drivers.register_callbacks(app, dashboard_data)
customer_trust.register_callbacks(app, dashboard_data)
seller_strategy.register_callbacks(app, dashboard_data)


def render_navigation(pathname: str | None) -> html.Header:
    path = pathname or "/"
    nav_links = []
    for item in NAV_ITEMS:
        is_active = path == item["path"]
        style = nav_link_active_style if is_active else nav_link_style
        nav_links.append(dcc.Link(item["label"], href=item["path"], style=style))

    subtitle = (
        f"{dashboard_data.financial_overview['seller_count']:,} sellers • "
        f"{dashboard_data.financial_overview['item_count']:,} items delivered"
    )

    return html.Header(
        [
            html.H1("Olist Growth Briefing", style=hero_title_style),
            html.P(
                "A CEO-ready view of the marketplace's revenue engine, customer trust, and seller mix.",
                style=hero_text_style,
            ),
            html.Div(subtitle, style={"marginTop": "12px", "fontSize": "1rem", "color": "rgba(248, 250, 252, 0.65)"}),
            html.Div(nav_links, style=nav_style),
        ],
        style=header_style,
    )


def render_page(pathname: str | None) -> html.Div:
    path = pathname or "/"

    if path in ("/", "/overview"):
        return overview.layout(dashboard_data)
    if path == "/drivers":
        return revenue_drivers.layout(dashboard_data)
    if path == "/customers":
        return customer_trust.layout(dashboard_data)
    if path == "/strategy":
        return seller_strategy.layout(dashboard_data)
    if path == "/actions":
        return actions.layout(dashboard_data)

    return html.Div(
        [
            html.Div(
                [
                    html.H2("Page not found", style={"fontSize": "2.5rem", "color": "#0f172a"}),
                    html.P(
                        "We redirected you to the executive overview. Use the navigation above to explore other chapters.",
                        style=summary_text_style,
                    ),
                ],
                style=card_style,
            ),
            overview.layout(dashboard_data),
        ],
        style=page_wrapper_style,
    )


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(
            [
                html.Div(id="nav-container"),
                html.Div(id="page-content", style=page_content_style),
            ],
            style=content_wrapper_style,
        ),
        html.Footer(
            "Data source: Olist public dataset. Revenue assumes 10% commission on delivered orders and 80 BRL subscription per active seller.",
            style=footer_style,
        ),
    ],
    style=container_style,
)


@app.callback(
    Output("nav-container", "children"),
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def update_shell(pathname: str | None):
    navigation = render_navigation(pathname)
    content = render_page(pathname)
    return navigation, content


if __name__ == "__main__":
    app.run(debug=True)
