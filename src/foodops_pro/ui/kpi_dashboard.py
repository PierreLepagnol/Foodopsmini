"""Vue de tableau de bord des KPIs pour FoodOps Pro."""

from decimal import Decimal
from typing import Dict, List, Optional

from ..domain.restaurant import Restaurant
from ..core.market import AllocationResult
from .console_ui import ConsoleUI

# Indicateurs essentiels pour le suivi des performances
ESSENTIAL_KPIS = ["revenue", "cost_of_sales", "margin", "satisfaction"]


class KPIDashboard:
    """Construit et affiche un tableau de bord de KPIs.

    Ce module regroupe les indicateurs clés pour le tour courant et
    calcule leur évolution par rapport au tour précédent. Il offre
    également un classement optionnel des restaurants selon un indicateur
    donné.
    """

    def __init__(self, ui: ConsoleUI) -> None:
        self.ui = ui

    def build_kpis(
        self,
        restaurants: List[Restaurant],
        current_results: Dict[str, AllocationResult],
        previous_results: Optional[Dict[str, AllocationResult]],
        current_turn: int,
    ) -> List[Dict[str, Decimal]]:
        """Calcule les KPIs pour chaque restaurant.

        Args:
            restaurants: Liste des restaurants
            current_results: Résultats du tour en cours
            previous_results: Résultats du tour précédent (si disponibles)
            current_turn: Numéro du tour actuel

        Returns:
            Liste de dictionnaires contenant les KPIs et leurs évolutions
        """
        data: List[Dict[str, Decimal]] = []

        for r in restaurants:
            res = current_results.get(r.id)
            if not res:
                continue

            ca = Decimal(res.revenue)

            # Coût des ventes pour le tour courant
            produced_costs = getattr(r, "production_cost_per_portion", {}) or {}
            sales_map = res.recipe_sales or {}
            cost_sold = Decimal("0")
            for rid, sold in sales_map.items():
                cpp = produced_costs.get(rid)
                if cpp is not None:
                    cost_sold += cpp * Decimal(int(sold))
            margin = ca - cost_sold

            sat_hist = getattr(r, "customer_satisfaction_history", [])
            satisfaction = sat_hist[-1] if sat_hist else Decimal("0")

            # Données du tour précédent
            prev_res = previous_results.get(r.id) if previous_results else None
            prev_ca = Decimal(prev_res.revenue) if prev_res else Decimal("0")

            prev_stats = (
                getattr(r, "production_stats_history", {}).get(current_turn - 1, {})
            )
            prev_cost = Decimal("0")
            for d in prev_stats.values():
                cpp = d.get("cost_per_portion")
                sold = d.get("sold", 0)
                if cpp is not None:
                    prev_cost += cpp * Decimal(int(sold))
            prev_margin = prev_ca - prev_cost

            prev_satisfaction = sat_hist[-2] if len(sat_hist) >= 2 else Decimal("0")

            data.append(
                {
                    "restaurant": r.name,
                    "revenue": ca,
                    "revenue_change": ca - prev_ca,
                    "cost_of_sales": cost_sold,
                    "cost_of_sales_change": cost_sold - prev_cost,
                    "margin": margin,
                    "margin_change": margin - prev_margin,
                    "satisfaction": satisfaction,
                    "satisfaction_change": satisfaction - prev_satisfaction,
                }
            )

        return data

    def display(self, data: List[Dict[str, Decimal]], ranking: str = "revenue") -> None:
        """Affiche les KPIs et un classement optionnel."""
        lines = ["📌 KPIs (tour vs précédent):"]
        for d in data:
            lines.append(
                "• {name}: CA {ca:.0f}€ ({ca_d:+.0f}) | Coût {cv:.0f}€ ({cv_d:+.0f}) | "
                "Marge {m:.0f}€ ({m_d:+.0f}) | Satisf. {s:.1f} ({s_d:+.1f})".format(
                    name=d["restaurant"],
                    ca=d["revenue"],
                    ca_d=d["revenue_change"],
                    cv=d["cost_of_sales"],
                    cv_d=d["cost_of_sales_change"],
                    m=d["margin"],
                    m_d=d["margin_change"],
                    s=d["satisfaction"],
                    s_d=d["satisfaction_change"],
                )
            )
        self.ui.print_box(lines, style="info")

        metric = ranking if ranking in ESSENTIAL_KPIS else "revenue"
        sorted_data = sorted(data, key=lambda x: x[metric], reverse=True)
        rank_lines = [f"🏆 Classement ({metric})"]
        for idx, d in enumerate(sorted_data, 1):
            value = d[metric]
            if metric == "satisfaction":
                rank_lines.append(f"{idx}. {d['restaurant']} - {value:.1f}")
            else:
                rank_lines.append(f"{idx}. {d['restaurant']} - {value:.0f}€")
        self.ui.print_box(rank_lines, style="success")
