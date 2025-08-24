"""Export des résultats et calcul des KPIs"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from game_engine.io.save_manager import DecimalEncoder, GameState


class KPICalculator:
    """
    Calculateur de KPIs métier pour l'analyse des performances.
    """

    @staticmethod
    def calculate_restaurant_kpis(
        restaurant_data: dict, turn_history: list[dict]
    ) -> dict[str, Any]:
        """
        Calcule les KPIs d'un restaurant.

        Args:
            restaurant_data: Données du restaurant
            turn_history: Historique des tours

        Returns:
            KPIs calculés
        """
        restaurant_id = restaurant_data["id"]

        # Extraction des données du restaurant dans l'historique
        restaurant_turns = []
        for turn_data in turn_history:
            if restaurant_id in turn_data["results"]:
                result = turn_data["results"][restaurant_id]
                result["turn"] = turn_data["turn"]
                restaurant_turns.append(result)

        if not restaurant_turns:
            return {}

        # Calculs des KPIs
        total_revenue = sum(turn["revenue"] for turn in restaurant_turns)
        total_customers = sum(turn["served_customers"] for turn in restaurant_turns)
        sum(turn["capacity"] for turn in restaurant_turns)

        # Ticket moyen
        average_ticket = total_revenue / total_customers if total_customers > 0 else 0

        # Taux d'utilisation moyen
        avg_utilization = sum(
            turn["utilization_rate"] for turn in restaurant_turns
        ) / len(restaurant_turns)

        # Évolution du chiffre d'affaires
        revenue_trend = []
        for turn in restaurant_turns:
            revenue_trend.append(turn["revenue"])

        # Croissance du CA (premier vs dernier tour)
        revenue_growth = 0
        if len(revenue_trend) > 1 and revenue_trend[0] > 0:
            revenue_growth = (
                (revenue_trend[-1] - revenue_trend[0]) / revenue_trend[0] * 100
            )

        # Régularité de la fréquentation
        utilization_rates = [turn["utilization_rate"] for turn in restaurant_turns]
        utilization_std = KPICalculator._calculate_std(utilization_rates)

        # Performance par tour
        best_turn = max(restaurant_turns, key=lambda x: x["revenue"])
        worst_turn = min(restaurant_turns, key=lambda x: x["revenue"])

        return {
            "total_revenue": total_revenue,
            "total_customers": total_customers,
            "average_ticket": average_ticket,
            "avg_utilization_rate": avg_utilization,
            "revenue_growth_percent": revenue_growth,
            "utilization_consistency": 1
            - utilization_std,  # Plus proche de 1 = plus régulier
            "best_turn": {
                "turn": best_turn["turn"],
                "revenue": best_turn["revenue"],
                "customers": best_turn["served_customers"],
            },
            "worst_turn": {
                "turn": worst_turn["turn"],
                "revenue": worst_turn["revenue"],
                "customers": worst_turn["served_customers"],
            },
            "turns_played": len(restaurant_turns),
        }

    @staticmethod
    def calculate_market_kpis(turn_history: list[dict]) -> dict[str, Any]:
        """
        Calcule les KPIs du marché global.

        Args:
            turn_history: Historique des tours

        Returns:
            KPIs du marché
        """
        if not turn_history:
            return {}

        # Agrégation par tour
        market_turns = []
        for turn_data in turn_history:
            turn_total = {
                "turn": turn_data["turn"],
                "total_demand": 0,
                "total_served": 0,
                "total_capacity": 0,
                "total_revenue": 0,
                "restaurants_count": len(turn_data["results"]),
            }

            for result in turn_data["results"].values():
                turn_total["total_demand"] += result["allocated_demand"]
                turn_total["total_served"] += result["served_customers"]
                turn_total["total_capacity"] += result["capacity"]
                turn_total["total_revenue"] += result["revenue"]

            # Calculs dérivés
            turn_total["market_utilization"] = (
                turn_total["total_served"] / turn_total["total_capacity"]
                if turn_total["total_capacity"] > 0
                else 0
            )
            turn_total["demand_satisfaction"] = (
                turn_total["total_served"] / turn_total["total_demand"]
                if turn_total["total_demand"] > 0
                else 0
            )
            turn_total["average_ticket"] = (
                turn_total["total_revenue"] / turn_total["total_served"]
                if turn_total["total_served"] > 0
                else 0
            )

            market_turns.append(turn_total)

        # KPIs globaux
        total_revenue = sum(turn["total_revenue"] for turn in market_turns)
        total_customers = sum(turn["total_served"] for turn in market_turns)
        avg_market_utilization = sum(
            turn["market_utilization"] for turn in market_turns
        ) / len(market_turns)
        avg_demand_satisfaction = sum(
            turn["demand_satisfaction"] for turn in market_turns
        ) / len(market_turns)

        # Évolution de la demande
        demand_trend = [turn["total_demand"] for turn in market_turns]
        demand_growth = 0
        if len(demand_trend) > 1 and demand_trend[0] > 0:
            demand_growth = (demand_trend[-1] - demand_trend[0]) / demand_trend[0] * 100

        return {
            "total_market_revenue": total_revenue,
            "total_market_customers": total_customers,
            "avg_market_utilization": avg_market_utilization,
            "avg_demand_satisfaction": avg_demand_satisfaction,
            "demand_growth_percent": demand_growth,
            "turns_analyzed": len(market_turns),
            "turn_details": market_turns,
        }

    @staticmethod
    def _calculate_std(values: list[float]) -> float:
        """Calcule l'écart-type d'une liste de valeurs."""
        if len(values) < 2:
            return 0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance**0.5


class ResultsExporter:
    """
    Exporteur de résultats vers différents formats.
    """

    def __init__(self) -> None:
        self.kpi_calculator = KPICalculator()

    def export_to_csv(self, game_state: GameState, output_dir: Path) -> list[Path]:
        """
        Exporte les résultats vers des fichiers CSV.

        Args:
            game_state: État de la partie
            output_dir: Répertoire de sortie

        Returns:
            Liste des fichiers créés
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        created_files = []

        # Export des résultats par tour
        turns_file = output_dir / f"turns_{game_state.game_id}.csv"
        with open(turns_file, "w", newline="", encoding="utf-8") as file:
            if game_state.turn_history:
                # En-têtes
                fieldnames = ["turn", "restaurant_id", "restaurant_name"]
                first_result = list(game_state.turn_history[0]["results"].values())[0]
                fieldnames.extend(first_result.keys())

                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                # Données
                restaurant_names = {r["id"]: r["name"] for r in game_state.players}
                restaurant_names.update(
                    {r["id"]: r["name"] for r in game_state.ai_competitors}
                )

                for turn_data in game_state.turn_history:
                    for restaurant_id, result in turn_data["results"].items():
                        row = {
                            "turn": turn_data["turn"],
                            "restaurant_id": restaurant_id,
                            "restaurant_name": restaurant_names.get(
                                restaurant_id, "Unknown"
                            ),
                            **result,
                        }
                        writer.writerow(row)

        created_files.append(turns_file)

        # Export des KPIs par restaurant
        kpis_file = output_dir / f"kpis_{game_state.game_id}.csv"
        with open(kpis_file, "w", newline="", encoding="utf-8") as file:
            fieldnames = [
                "restaurant_id",
                "restaurant_name",
                "restaurant_type",
                "total_revenue",
                "total_customers",
                "average_ticket",
                "avg_utilization_rate",
                "revenue_growth_percent",
                "utilization_consistency",
                "turns_played",
            ]

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            all_restaurants = game_state.players + game_state.ai_competitors
            for restaurant in all_restaurants:
                kpis = self.kpi_calculator.calculate_restaurant_kpis(
                    restaurant, game_state.turn_history
                )

                if kpis:
                    row = {
                        "restaurant_id": restaurant["id"],
                        "restaurant_name": restaurant["name"],
                        "restaurant_type": restaurant["type"],
                        **{
                            k: v
                            for k, v in kpis.items()
                            if k not in ["best_turn", "worst_turn"]
                        },
                    }
                    writer.writerow(row)

        created_files.append(kpis_file)

        return created_files

    def export_to_json(self, game_state: GameState, output_path: Path) -> None:
        """
        Exporte les résultats vers un fichier JSON complet.

        Args:
            game_state: État de la partie
            output_path: Chemin du fichier de sortie
        """
        # Calcul des KPIs pour tous les restaurants
        restaurant_kpis = {}
        all_restaurants = game_state.players + game_state.ai_competitors

        for restaurant in all_restaurants:
            kpis = self.kpi_calculator.calculate_restaurant_kpis(
                restaurant, game_state.turn_history
            )
            restaurant_kpis[restaurant["id"]] = kpis

        # KPIs du marché
        market_kpis = self.kpi_calculator.calculate_market_kpis(game_state.turn_history)

        # Rapport complet
        report = {
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "game_id": game_state.game_id,
                "scenario_name": game_state.scenario_name,
            },
            "game_summary": {
                "turns_played": len(game_state.turn_history),
                "total_turns": game_state.max_turns,
                "players_count": len(game_state.players),
                "ai_competitors_count": len(game_state.ai_competitors),
                "completed": len(game_state.turn_history) >= game_state.max_turns,
            },
            "restaurants": all_restaurants,
            "restaurant_kpis": restaurant_kpis,
            "market_kpis": market_kpis,
            "turn_history": game_state.turn_history,
        }

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(report, file, cls=DecimalEncoder, indent=2, ensure_ascii=False)

    def generate_ranking(self, game_state: GameState) -> list[dict[str, Any]]:
        """
        Génère le classement final des restaurants.

        Args:
            game_state: État de la partie

        Returns:
            Liste des restaurants classés
        """
        all_restaurants = game_state.players + game_state.ai_competitors
        ranking = []

        for restaurant in all_restaurants:
            kpis = self.kpi_calculator.calculate_restaurant_kpis(
                restaurant, game_state.turn_history
            )

            ranking_entry = {
                "restaurant_id": restaurant["id"],
                "restaurant_name": restaurant["name"],
                "restaurant_type": restaurant["type"],
                "total_revenue": kpis.get("total_revenue", 0),
                "total_customers": kpis.get("total_customers", 0),
                "average_ticket": kpis.get("average_ticket", 0),
                "avg_utilization": kpis.get("avg_utilization_rate", 0),
                "cash": restaurant.get("cash", 0),
                "is_player": restaurant in game_state.players,
            }
            ranking.append(ranking_entry)

        # Classement par chiffre d'affaires total
        ranking.sort(key=lambda x: x["total_revenue"], reverse=True)

        # Ajout des positions
        for i, entry in enumerate(ranking, 1):
            entry["position"] = i

        return ranking
