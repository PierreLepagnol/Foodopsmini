"""Génération de rapports de fin de tour."""

from __future__ import annotations

from ..core.production import ProductionPlan


def render_turn_report(plan: ProductionPlan) -> list[str]:
    """Construit les lignes de rapport pour le tour courant.

    Met en avant l'impact des éventuels événements spéciaux.
    """
    lines: list[str] = []
    if plan.special_day is not None:
        sd = plan.special_day
        lines.append(
            f"📅 Journée spéciale: {sd.event_type} (impact attendu x{sd.expected_impact})"
        )
    return lines
