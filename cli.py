"""
Interface en ligne de commande pour FoodOps Pro.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional
from decimal import Decimal

from game_engine.io.data_loader import DataLoader
from game_engine.io.persistence import GameStatePersistence
from game_engine.io.export import ResultsExporter
from game_engine.domain.restaurant import Restaurant, RestaurantType
from game_engine.domain.employee import Employee, EmployeePosition, EmployeeContract
from game_engine.core.market import MarketEngine
from game_engine.core.costing import RecipeCostCalculator


class FoodOpsGame:
    """
    Classe principale du jeu FoodOps Pro.
    """

    def __init__(
        self, scenario_path: Optional[Path] = None, debug: bool = False
    ) -> None:
        """
        Initialise le jeu.

        Args:
            scenario_path: Chemin vers le scénario
            debug: Mode debug activé
        """
        self.debug = debug
        self.data_loader = DataLoader()
        self.persistence = GameStatePersistence()
        self.exporter = ResultsExporter()

        # Chargement des données
        print("Chargement des données...")
        self.game_data = self.data_loader.load_all_data(scenario_path)

        self.scenario = self.game_data["scenario"]
        self.ingredients = self.game_data["ingredients"]
        self.recipes = self.game_data["recipes"]
        self.suppliers = self.game_data["suppliers"]
        self.hr_tables = self.game_data["hr_tables"]

        # Moteurs de jeu
        self.market_engine = MarketEngine(self.scenario, self.scenario.random_seed)
        self.cost_calculator = RecipeCostCalculator(self.ingredients)

        # État du jeu
        self.players: List[Restaurant] = []
        self.ai_competitors: List[Restaurant] = []
        self.current_turn = 1

        print(f"✓ Scénario '{self.scenario.name}' chargé")
        print(f"✓ {len(self.ingredients)} ingrédients, {len(self.recipes)} recettes")

    def start_new_game(self) -> None:
        """Lance une nouvelle partie."""
        print("\n" + "=" * 60)
        print("FOODOPS PRO - Nouvelle Partie")
        print("=" * 60)

        # Configuration des joueurs
        self._setup_players()

        # Création des concurrents IA
        self._create_ai_competitors()

        # Boucle de jeu principale
        self._game_loop()

        # Fin de partie
        self._end_game()

    def _setup_players(self) -> None:
        """Configure les restaurants des joueurs."""
        while True:
            try:
                num_players = int(input("\nNombre de joueurs (1-4) : "))
                if 1 <= num_players <= 4:
                    break
                print("Veuillez entrer un nombre entre 1 et 4.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")

        for i in range(num_players):
            print(f"\n--- Configuration du joueur {i + 1} ---")

            # Nom du restaurant
            name = input("Nom du restaurant : ").strip()
            if not name:
                name = f"Restaurant {i + 1}"

            # Type de restaurant
            print("\nTypes de restaurant disponibles :")
            for j, rest_type in enumerate(RestaurantType, 1):
                print(f"{j}. {rest_type.value.title()}")

            while True:
                try:
                    type_choice = int(input("Choisissez le type (1-4) : "))
                    if 1 <= type_choice <= len(RestaurantType):
                        restaurant_type = list(RestaurantType)[type_choice - 1]
                        break
                    print("Choix invalide.")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")

            # Création du restaurant
            restaurant = self._create_restaurant(name, restaurant_type, is_player=True)
            self.players.append(restaurant)

            print(f"✓ Restaurant '{name}' créé ({restaurant_type.value})")

    def _create_restaurant(
        self, name: str, rest_type: RestaurantType, is_player: bool = True
    ) -> Restaurant:
        """
        Crée un restaurant avec configuration de base.

        Args:
            name: Nom du restaurant
            rest_type: Type de restaurant
            is_player: True si c'est un joueur humain

        Returns:
            Restaurant configuré
        """
        # Paramètres par type
        type_config = {
            RestaurantType.FAST: {
                "capacity": 120,
                "speed": Decimal("1.4"),
                "cash": Decimal("15000"),
                "rent": Decimal("3500"),
            },
            RestaurantType.CLASSIC: {
                "capacity": 80,
                "speed": Decimal("1.0"),
                "cash": Decimal("20000"),
                "rent": Decimal("4500"),
            },
            RestaurantType.GASTRONOMIQUE: {
                "capacity": 40,
                "speed": Decimal("0.7"),
                "cash": Decimal("30000"),
                "rent": Decimal("6000"),
            },
            RestaurantType.BRASSERIE: {
                "capacity": 100,
                "speed": Decimal("1.1"),
                "cash": Decimal("25000"),
                "rent": Decimal("5000"),
            },
        }

        config = type_config[rest_type]

        restaurant = Restaurant(
            id=name.lower().replace(" ", "_"),
            name=name,
            type=rest_type,
            capacity_base=config["capacity"],
            speed_service=config["speed"],
            cash=config["cash"],
            rent_monthly=config["rent"],
            fixed_costs_monthly=Decimal("2000"),
            equipment_value=Decimal("50000"),
        )

        # Ajout d'employés de base
        self._add_base_employees(restaurant)

        # Menu de base avec quelques recettes
        self._setup_base_menu(restaurant)

        return restaurant

    def _add_base_employees(self, restaurant: Restaurant) -> None:
        """Ajoute les employés de base à un restaurant."""
        base_employees = [
            Employee(
                id=f"{restaurant.id}_chef",
                name="Chef Cuisinier",
                position=EmployeePosition.CUISINE,
                contract=EmployeeContract.CDI,
                salary_gross_monthly=Decimal("2500"),
                productivity=Decimal("1.2"),
                experience_months=36,
            ),
            Employee(
                id=f"{restaurant.id}_serveur",
                name="Serveur",
                position=EmployeePosition.SALLE,
                contract=EmployeeContract.CDI,
                salary_gross_monthly=Decimal("2000"),
                productivity=Decimal("1.0"),
                experience_months=12,
            ),
        ]

        for employee in base_employees:
            restaurant.add_employee(employee)

    def _setup_base_menu(self, restaurant: Restaurant) -> None:
        """Configure le menu de base d'un restaurant."""
        # Sélection de recettes selon le type
        base_recipes = {
            RestaurantType.FAST: [
                ("burger_classic", Decimal("12.50")),
                ("burger_chicken", Decimal("13.00")),
                ("menu_enfant", Decimal("8.50")),
                ("wrap_chicken", Decimal("9.50")),
            ],
            RestaurantType.CLASSIC: [
                ("pasta_bolognese", Decimal("16.00")),
                ("steak_frites", Decimal("22.00")),
                ("salad_caesar", Decimal("14.00")),
                ("fish_chips", Decimal("18.50")),
            ],
            RestaurantType.GASTRONOMIQUE: [
                ("bowl_salmon", Decimal("28.00")),
                ("risotto_mushroom", Decimal("24.00")),
                ("quiche_lorraine", Decimal("19.00")),
            ],
            RestaurantType.BRASSERIE: [
                ("croque_monsieur", Decimal("11.50")),
                ("omelet_cheese", Decimal("13.00")),
                ("soup_tomato", Decimal("8.50")),
                ("salad_goat", Decimal("15.50")),
            ],
        }

        recipes_for_type = base_recipes.get(
            restaurant.type, base_recipes[RestaurantType.CLASSIC]
        )

        for recipe_id, price in recipes_for_type:
            if recipe_id in self.recipes:
                restaurant.set_recipe_price(recipe_id, price)
                restaurant.activate_recipe(recipe_id)

    def _create_ai_competitors(self) -> None:
        """Crée les concurrents IA."""
        ai_configs = [
            ("Chez Mario", RestaurantType.CLASSIC),
            ("Quick Burger", RestaurantType.FAST),
        ]

        for i, (name, rest_type) in enumerate(
            ai_configs[: self.scenario.ai_competitors]
        ):
            ai_restaurant = self._create_restaurant(name, rest_type, is_player=False)
            self.ai_competitors.append(ai_restaurant)
            print(f"✓ Concurrent IA '{name}' créé")

    def _game_loop(self) -> None:
        """Boucle principale du jeu."""
        print(f"\n🎮 Début de la partie - {self.scenario.turns} tours")

        for turn in range(1, self.scenario.turns + 1):
            self.current_turn = turn
            print(f"\n{'=' * 60}")
            print(f"TOUR {turn}/{self.scenario.turns}")
            print(f"{'=' * 60}")

            # Décisions des joueurs
            self._player_decisions()

            # Décisions de l'IA
            self._ai_decisions()

            # Simulation du marché
            all_restaurants = self.players + self.ai_competitors
            results = self.market_engine.allocate_demand(all_restaurants, turn)

            # Affichage des résultats
            self._display_turn_results(results)

            # Pause entre les tours
            if turn < self.scenario.turns:
                input("\nAppuyez sur Entrée pour continuer...")

    def _player_decisions(self) -> None:
        """Gère les décisions des joueurs pour le tour."""
        for i, player in enumerate(self.players):
            print(f"\n--- Décisions pour {player.name} ---")

            # Affichage du statut
            print(f"Trésorerie : {player.cash:.0f} €")
            print(f"Capacité actuelle : {player.capacity_current} couverts")

            # Menu actuel
            print("\nMenu actuel :")
            active_menu = player.get_active_menu()
            if active_menu:
                for recipe_id, price in active_menu.items():
                    recipe_name = self.recipes[recipe_id].name
                    print(f"  - {recipe_name} : {price:.2f} €")
            else:
                print("  Aucune recette active !")

            # Décision de staffing
            print(f"\nNiveau de staffing actuel : {player.staffing_level}")
            print("0=Fermé, 1=Léger, 2=Normal, 3=Renforcé")

            while True:
                try:
                    staffing = int(input("Nouveau niveau de staffing : "))
                    if 0 <= staffing <= 3:
                        player.staffing_level = staffing
                        break
                    print("Niveau invalide (0-3).")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")

            # Ajustement des prix (simplifié)
            if active_menu:
                adjust_prices = (
                    input("Ajuster les prix ? (o/N) : ").lower().startswith("o")
                )
                if adjust_prices:
                    self._adjust_menu_prices(player)

    def _adjust_menu_prices(self, restaurant: Restaurant) -> None:
        """Permet d'ajuster les prix du menu."""
        active_menu = restaurant.get_active_menu()

        for recipe_id, current_price in active_menu.items():
            recipe_name = self.recipes[recipe_id].name
            print(f"\n{recipe_name} (actuellement {current_price:.2f} €)")

            while True:
                try:
                    new_price_str = input(
                        "Nouveau prix (Entrée pour garder) : "
                    ).strip()
                    if not new_price_str:
                        break

                    new_price = Decimal(new_price_str.replace(",", "."))
                    if new_price > 0:
                        restaurant.set_recipe_price(recipe_id, new_price)
                        print(f"✓ Prix mis à jour : {new_price:.2f} €")
                        break
                    else:
                        print("Le prix doit être positif.")
                except (ValueError, TypeError):
                    print("Prix invalide.")

    def _ai_decisions(self) -> None:
        """Gère les décisions des IA."""
        for ai in self.ai_competitors:
            # Stratégie simple : staffing normal, prix stables
            ai.staffing_level = 2

            # Ajustement léger des prix selon la performance
            if hasattr(ai, "_last_utilization"):
                if ai._last_utilization > 0.9:
                    # Augmentation des prix si très demandé
                    for recipe_id, price in ai.menu.items():
                        ai.set_recipe_price(recipe_id, price * Decimal("1.05"))
                elif ai._last_utilization < 0.5:
                    # Baisse des prix si peu demandé
                    for recipe_id, price in ai.menu.items():
                        ai.set_recipe_price(recipe_id, price * Decimal("0.95"))

    def _display_turn_results(self, results: Dict) -> None:
        """Affiche les résultats du tour."""
        print(f"\n📊 Résultats du tour {self.current_turn}")
        print("-" * 80)
        print(
            f"{'Restaurant':<20} {'Demande':<8} {'Servi':<8} {'Capacité':<10} {'Util.':<6} {'CA €':<10}"
        )
        print("-" * 80)

        all_restaurants = self.players + self.ai_competitors

        for restaurant in all_restaurants:
            if restaurant.id in results:
                result = results[restaurant.id]

                # Sauvegarde pour l'IA
                restaurant._last_utilization = float(result.utilization_rate)

                # Mise à jour de la trésorerie (simplifié)
                profit = result.revenue * Decimal("0.15")  # Marge approximative
                restaurant.update_cash(profit)

                utilization_pct = f"{result.utilization_rate:.1%}"
                print(
                    f"{restaurant.name:<20} "
                    f"{result.allocated_demand:<8} "
                    f"{result.served_customers:<8} "
                    f"{result.capacity:<10} "
                    f"{utilization_pct:<6} "
                    f"{result.revenue:<10.0f}"
                )

        print("-" * 80)

        # Analyse du marché
        market_analysis = self.market_engine.get_market_analysis()
        print(
            f"Marché total : {market_analysis['total_served']} clients servis, "
            f"{market_analysis['total_revenue']:.0f} € de CA"
        )

    def _end_game(self) -> None:
        """Gère la fin de partie."""
        print("\n🏁 FIN DE PARTIE")
        print("=" * 60)

        # Classement final
        ranking = []
        for restaurant in self.players + self.ai_competitors:
            ranking.append(
                {
                    "name": restaurant.name,
                    "cash": restaurant.cash,
                    "is_player": restaurant in self.players,
                }
            )

        ranking.sort(key=lambda x: x["cash"], reverse=True)

        print("CLASSEMENT FINAL :")
        for i, entry in enumerate(ranking, 1):
            player_mark = "👤" if entry["is_player"] else "🤖"
            print(f"{i}. {player_mark} {entry['name']:<20} {entry['cash']:>10.0f} €")

        # Proposition d'export
        export_choice = (
            input("\nExporter les résultats ? (o/N) : ").lower().startswith("o")
        )
        if export_choice:
            self._export_results()

    def _export_results(self) -> None:
        """Exporte les résultats de la partie."""
        try:
            output_dir = Path("exports")
            output_dir.mkdir(exist_ok=True)

            # Création d'un état de jeu pour l'export
            game_state = self.persistence.create_game_state(
                self.scenario, self.players, self.ai_competitors
            )

            # Export JSON
            json_file = output_dir / f"results_{game_state.game_id}.json"
            self.exporter.export_to_json(game_state, json_file)

            print(f"✓ Résultats exportés vers {json_file}")

        except Exception as e:
            print(f"❌ Erreur lors de l'export : {e}")


def main() -> None:
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="FoodOps Pro - Jeu de gestion de restaurant"
    )
    parser.add_argument(
        "--scenario", type=Path, help="Chemin vers le fichier de scénario"
    )
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    parser.add_argument("--seed", type=int, help="Graine aléatoire")

    args = parser.parse_args()

    try:
        game = FoodOpsGame(args.scenario, args.debug)
        game.start_new_game()

    except KeyboardInterrupt:
        print("\n\n👋 Partie interrompue. À bientôt !")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
