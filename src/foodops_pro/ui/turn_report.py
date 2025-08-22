"""Rapport de tour pour FoodOps Pro.

Ce module affiche la répartition des clients et des coûts selon les jours
ouverts, fermés et les journées spéciales. Une section dédiée résume également
les décisions de calendrier et leurs impacts directs sur la demande et les
coûts.
"""

from dataclasses import dataclass
from typing import Dict, List
from decimal import Decimal

from .console_ui import ConsoleUI


@dataclass
class DayStat:
    """Statistiques pour un type de journée."""

    label: str
    clients: int
    costs: Decimal


class TurnReport:
    """Affiche un rapport détaillé pour un tour donné."""

    def __init__(self, ui: ConsoleUI) -> None:
        self.ui = ui

    def show(
        self,
        turn: int,
        open_day: DayStat,
        closed_day: DayStat,
        special_days: List[DayStat],
        calendar_decisions: Dict[str, Dict],
    ) -> None:
        """Affiche le rapport du tour.

        Args:
            turn: Numéro du tour courant.
            open_day: Statistiques agrégées pour les jours ouverts.
            closed_day: Statistiques agrégées pour les jours fermés.
            special_days: Liste de statistiques pour chaque journée spéciale.
            calendar_decisions: Informations sur les décisions de calendrier et
                leurs impacts.
        """

        self.ui.clear_screen()
        self._show_distribution(turn, open_day, closed_day, special_days)
        print()
        self._show_calendar_decisions(calendar_decisions)

    def _show_distribution(
        self,
        turn: int,
        open_day: DayStat,
        closed_day: DayStat,
        special_days: List[DayStat],
    ) -> None:
        """Affiche la répartition des clients et coûts par type de journée."""

        stats = [open_day, closed_day] + special_days
        total_clients = sum(s.clients for s in stats)
        total_costs = sum(s.costs for s in stats)

        lines = [
            "Type de jour                    │ Clients │ Coûts (€) │ % Clients │ % Coûts",
            "─" * 79,
        ]
        for s in stats:
            client_pct = (
                Decimal(s.clients) / total_clients * Decimal("100")
                if total_clients
                else Decimal("0")
            )
            cost_pct = (
                s.costs / total_costs * Decimal("100") if total_costs else Decimal("0")
            )
            lines.append(
                f"{s.label:<30} │ {s.clients:>7} │ {s.costs:>9.2f} │ "
                f"{client_pct:>9.1f}% │ {cost_pct:>7.1f}%"
            )

        self.ui.print_box(
            lines, f"RÉPARTITION CLIENTS/COÛTS - TOUR {turn}", style="info"
        )

    def _show_calendar_decisions(self, decisions: Dict[str, Dict]) -> None:
        """Affiche les conséquences des décisions de calendrier."""

        lines: List[str] = []
        days_closed = decisions.get("days_closed", 0)
        demand_impact = Decimal(decisions.get("demand_impact_pct", 0))
        cost_impact = Decimal(decisions.get("cost_impact_pct", 0))
        lines.append(
            f"• {days_closed} jour(s) fermé(s) = {demand_impact:+.0%} demande, "
            f"{cost_impact:+.0%} coûts"
        )

        for event in decisions.get("special_days", []):
            name = event.get("name", "Journée spéciale")
            d_pct = Decimal(event.get("demand_impact_pct", 0))
            c_pct = Decimal(event.get("cost_impact_pct", 0))
            lines.append(
                f"• {name} = {d_pct:+.0%} demande, {c_pct:+.0%} coûts"
            )

        self.ui.print_box(lines, "DÉCISIONS SUR LE CALENDRIER", style="warning")
