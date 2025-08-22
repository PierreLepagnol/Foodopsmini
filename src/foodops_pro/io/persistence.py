"""
Gestion de la persistance des parties pour FoodOps Pro.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from decimal import Decimal

from ..domain.restaurant import Restaurant
from ..domain.scenario import Scenario


class DecimalEncoder(json.JSONEncoder):
    """Encodeur JSON pour les objets Decimal."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@dataclass
class GameState:
    """
    État complet d'une partie de FoodOps Pro.

    Attributes:
        game_id: Identifiant unique de la partie
        scenario_name: Nom du scénario
        current_turn: Tour actuel
        max_turns: Nombre total de tours
        players: Liste des restaurants des joueurs
        ai_competitors: Liste des concurrents IA
        turn_history: Historique des tours
        created_at: Date de création
        last_saved: Dernière sauvegarde
    """

    game_id: str
    scenario_name: str
    current_turn: int
    max_turns: int
    players: List[Dict]  # Restaurants sérialisés
    ai_competitors: List[Dict]  # Concurrents IA sérialisés
    turn_history: List[Dict]  # Historique des résultats
    created_at: str
    last_saved: str

    def to_dict(self) -> Dict:
        """Convertit l'état en dictionnaire."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "GameState":
        """Crée un état depuis un dictionnaire."""
        return cls(**data)


class GameStatePersistence:
    """
    Gestionnaire de persistance des parties.
    """

    def __init__(self, save_directory: Optional[Path] = None) -> None:
        """
        Initialise le gestionnaire de persistance.

        Args:
            save_directory: Répertoire de sauvegarde
        """
        if save_directory is None:
            self.save_directory = Path.home() / ".foodops_pro" / "saves"
        else:
            self.save_directory = save_directory

        # Création du répertoire si nécessaire
        self.save_directory.mkdir(parents=True, exist_ok=True)

    def save_game(self, game_state: GameState) -> Path:
        """
        Sauvegarde une partie.

        Args:
            game_state: État de la partie

        Returns:
            Chemin du fichier de sauvegarde
        """
        # Mise à jour de la date de sauvegarde
        game_state.last_saved = datetime.now().isoformat()

        # Nom du fichier
        filename = f"game_{game_state.game_id}.json"
        filepath = self.save_directory / filename

        # Sauvegarde
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(
                game_state.to_dict(),
                file,
                cls=DecimalEncoder,
                indent=2,
                ensure_ascii=False,
            )

        return filepath

    def load_game(self, game_id: str) -> Optional[GameState]:
        """
        Charge une partie sauvegardée.

        Args:
            game_id: Identifiant de la partie

        Returns:
            État de la partie ou None si non trouvée
        """
        filename = f"game_{game_id}.json"
        filepath = self.save_directory / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
            return GameState.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def list_saved_games(self) -> List[Dict[str, str]]:
        """
        Liste les parties sauvegardées.

        Returns:
            Liste des informations des parties
        """
        games = []

        for filepath in self.save_directory.glob("game_*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    data = json.load(file)

                games.append(
                    {
                        "game_id": data["game_id"],
                        "scenario_name": data["scenario_name"],
                        "current_turn": data["current_turn"],
                        "max_turns": data["max_turns"],
                        "created_at": data["created_at"],
                        "last_saved": data["last_saved"],
                        "players_count": len(data["players"]),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue

        # Tri par date de dernière sauvegarde
        games.sort(key=lambda x: x["last_saved"], reverse=True)
        return games

    def delete_game(self, game_id: str) -> bool:
        """
        Supprime une partie sauvegardée.

        Args:
            game_id: Identifiant de la partie

        Returns:
            True si supprimée avec succès
        """
        filename = f"game_{game_id}.json"
        filepath = self.save_directory / filename

        if filepath.exists():
            try:
                filepath.unlink()
                return True
            except OSError:
                return False

        return False

    def create_game_state(
        self,
        scenario: Scenario,
        players: List[Restaurant],
        ai_competitors: List[Restaurant] = None,
    ) -> GameState:
        """
        Crée un nouvel état de partie.

        Args:
            scenario: Scénario de jeu
            players: Restaurants des joueurs
            ai_competitors: Concurrents IA

        Returns:
            Nouvel état de partie
        """
        game_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        now = datetime.now().isoformat()

        # Sérialisation des restaurants
        players_data = [self._serialize_restaurant(player) for player in players]
        ai_data = [self._serialize_restaurant(ai) for ai in (ai_competitors or [])]

        return GameState(
            game_id=game_id,
            scenario_name=scenario.name,
            current_turn=1,
            max_turns=scenario.turns,
            players=players_data,
            ai_competitors=ai_data,
            turn_history=[],
            created_at=now,
            last_saved=now,
        )

    def _serialize_restaurant(self, restaurant: Restaurant) -> Dict:
        """
        Sérialise un restaurant en dictionnaire.

        Args:
            restaurant: Restaurant à sérialiser

        Returns:
            Dictionnaire représentant le restaurant
        """
        # Conversion des employés
        employees_data = []
        for employee in restaurant.employees:
            emp_data = {
                "id": employee.id,
                "name": employee.name,
                "position": employee.position.value,
                "contract": employee.contract.value,
                "salary_gross_monthly": float(employee.salary_gross_monthly),
                "productivity": float(employee.productivity),
                "experience_months": employee.experience_months,
                "is_part_time": employee.is_part_time,
                "part_time_ratio": float(employee.part_time_ratio),
                "sunday_work": employee.sunday_work,
                "overtime_eligible": employee.overtime_eligible,
            }
            employees_data.append(emp_data)

        return {
            "id": restaurant.id,
            "name": restaurant.name,
            "type": restaurant.type.value,
            "capacity_base": restaurant.capacity_base,
            "speed_service": float(restaurant.speed_service),
            "menu": {k: float(v) for k, v in restaurant.menu.items()},
            "employees": employees_data,
            "cash": float(restaurant.cash),
            "equipment_value": float(restaurant.equipment_value),
            "rent_monthly": float(restaurant.rent_monthly),
            "fixed_costs_monthly": float(restaurant.fixed_costs_monthly),
            "staffing_level": restaurant.staffing_level,
            "active_recipes": restaurant.active_recipes.copy(),
        }

    def update_turn_history(self, game_state: GameState, turn_results: Dict) -> None:
        """
        Met à jour l'historique des tours.

        Args:
            game_state: État de la partie
            turn_results: Résultats du tour
        """
        # Conversion des résultats en format sérialisable
        serializable_results = {}
        for restaurant_id, result in turn_results.items():
            serializable_results[restaurant_id] = {
                "allocated_demand": result.allocated_demand,
                "served_customers": result.served_customers,
                "capacity": result.capacity,
                "utilization_rate": float(result.utilization_rate),
                "lost_customers": result.lost_customers,
                "revenue": float(result.revenue),
                "average_ticket": float(result.average_ticket),
                "waiting_time": float(result.waiting_time),
                "waiting_factor": float(result.waiting_factor),
            }

        turn_data = {
            "turn": game_state.current_turn,
            "timestamp": datetime.now().isoformat(),
            "results": serializable_results,
        }

        game_state.turn_history.append(turn_data)

    def export_game_summary(self, game_state: GameState, output_path: Path) -> None:
        """
        Exporte un résumé de partie en JSON.

        Args:
            game_state: État de la partie
            output_path: Chemin de sortie
        """
        summary = {
            "game_info": {
                "id": game_state.game_id,
                "scenario": game_state.scenario_name,
                "turns_played": len(game_state.turn_history),
                "total_turns": game_state.max_turns,
                "created_at": game_state.created_at,
                "completed": len(game_state.turn_history) >= game_state.max_turns,
            },
            "players": game_state.players,
            "turn_history": game_state.turn_history,
        }

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(summary, file, cls=DecimalEncoder, indent=2, ensure_ascii=False)


@dataclass
class CampaignProgress:
    """Représente la progression d'une campagne de scénarios."""

    campaign_name: str
    scenario_names: List[str]
    current_index: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "CampaignProgress":
        return cls(**data)


class CampaignPersistence:
    """Gestion de la persistance des campagnes."""

    def __init__(self, save_directory: Optional[Path] = None) -> None:
        if save_directory is None:
            self.save_directory = Path.home() / ".foodops_pro" / "campaigns"
        else:
            self.save_directory = save_directory
        self.save_directory.mkdir(parents=True, exist_ok=True)

    def _get_path(self, campaign_name: str) -> Path:
        return self.save_directory / f"campaign_{campaign_name}.json"

    def save_progress(self, progress: CampaignProgress) -> Path:
        """Sauvegarde la progression de campagne."""
        filepath = self._get_path(progress.campaign_name)
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(progress.to_dict(), file, indent=2, ensure_ascii=False)
        return filepath

    def load_progress(self, campaign_name: str) -> Optional[CampaignProgress]:
        """Charge la progression d'une campagne."""
        filepath = self._get_path(campaign_name)
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
            return CampaignProgress.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
