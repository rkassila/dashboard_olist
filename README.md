# Olist CEO Dashboard

This project turns the Olist public datasets into a Dash multi-page dashboard designed for a CEO audience. The analysis highlights revenue dynamics, reputation risk, customer experience, and seller optimisation levers.

## Key Questions Addressed

- **How healthy is the marketplace P&L?** The `Executive Overview` page shows gross vs. net revenue, waterfalls the costs (including reputation and IT), and surfaces headline KPIs.
- **What drives revenue and profitability?** The `Revenue Drivers` page tracks monthly performance, lets you focus on specific signals (net revenue, reputation cost, total sales), and ranks categories by net profit.
- **Where do we win or lose customer trust?** The `Customer Trust` page compares delivery delays with review scores, highlighting states that need intervention or can serve as benchmarks.
- **Which sellers should we retain or prune?** The `Seller Strategy` page simulates removing under-performing sellers and visualises the impact on revenue, cost, and net profit.
- **What should the CEO do next?** The `CEO Next Moves` page summarises the current month, profit uplift opportunities, category focus areas, and concrete cross-functional actions.

## Repository Layout

```
├── app.py                  # Dash entry point
├── dashboard/
│   ├── data.py             # Data loading and aggregation
│   ├── styles.py           # Shared styles and layout helpers
│   └── utils.py            # Formatting utilities and constants
├── sections/
│   ├── overview.py
│   ├── revenue_drivers.py
│   ├── customer_trust.py
│   ├── seller_strategy.py
│   └── actions.py          # Layouts and callbacks per dashboard page
└── olist_ceo_deck.ipynb    # Notebook reproducing the dashboard visuals
```

## How to Run the Dashboard

1. Install dependencies (Dash, Plotly, Pandas, NumPy).

2. From this directory, run:

   ```bash
   python3 app.py
   ```

3. Open the displayed URL (default `http://127.0.0.1:8050`). Use the navigation pills to move across sections.

## Notebook Companion

The notebook `olist_ceo_deck.ipynb` recreates every chart shown in the dashboard. It is intended for sharing static analysis or exporting visuals to presentations.

Sections mirror the dashboard:

1. Financial overview waterfall and KPIs.
2. Monthly trend line chart with selectable metrics.
3. Category profitability bar chart (Top N configurable).
4. Customer trust scatter plot with delay vs. review score.
5. Seller strategy what-if line plot plus highlight metrics.

Run the notebook top-to-bottom to regenerate the figures. Each cell describes the transformations applied, ensuring full traceability outside the Dash UI.
