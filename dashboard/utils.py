"""Utility helpers for the Olist dashboard."""

from __future__ import annotations

from typing import Dict


def format_brl(value: float) -> str:
    """Return a human-readable BRL string with non-breaking space grouping."""

    return f"{value:,.0f} BRL".replace(",", " ")


def format_percent(value: float) -> str:
    """Return a formatted percentage with one decimal point."""

    return f"{value:.1%}"


def format_category_name(name: str) -> str:
    """Convert snake_case category labels to title case for storytelling."""

    return name.replace("_", " ").title()


STATE_NAME_MAP: Dict[str, str] = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


METRIC_LABELS: Dict[str, str] = {
    "net_revenue": "Net revenue after reputation cost",
    "olist_revenue": "Total platform revenue",
    "reputation_cost": "Reputation costs",
    "gmv": "Total marketplace sales",
}
