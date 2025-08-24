"""
Interface CLI professionnelle pour FoodOps Pro.
"""

from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from creation_scenario import AdminSettings
from game_engine.core.costing import RecipeCostCalculator
from game_engine.core.market import MarketEngine
from game_engine.domain.commerce import CommerceLocation, CommerceManager
from game_engine.domain.employee import Employee, EmployeeContract, EmployeePosition
from game_engine.domain.restaurant import Restaurant, RestaurantType
from game_engine.io.data_loader import DataLoader
from game_engine.io.export import ResultsExporter
from game_engine.io.persistence import GameStatePersistence
from game_engine.ui.console_ui import (
    clear_screen,
    print_box,
    show_error,
    show_progress_bar,
    show_welcome_screen,
    show_success,
    show_info,
    show_menu,
    pause,
    confirm,
    get_input,
)
from game_engine.ui.decision_menu import DecisionMenu


class FoodOpsProGame:
    """
    Jeu FoodOps Pro avec interface professionnelle.
    """

    def __init__(self, scenario_path: Optional[Path] = None, admin_mode: bool = False):
        """
        Initialise le jeu.

        Args:
            scenario_path: Chemin vers le scénario
            admin_mode: Mode administrateur activé
        """
        self.admin_settings = self.load_settings(
            "/home/lepagnol/Documents/Perso/Games/Foodopsmini/admin_configs/preset_demo.yaml"
        )

        # Chargement des données
        show_progress_bar(0, 5, "Initialisation")

        self.data_loader = DataLoader()
        show_progress_bar(1, 5, "Chargement des données")

        self.game_data = self.data_loader.load_all_data(scenario_path)
        show_progress_bar(2, 5, "Configuration du marché")

        self.scenario = self.game_data["scenario"]
        self.ingredients = self.game_data["ingredients"]
        self.recipes = self.game_data["recipes"]
        self.suppliers = self.game_data["suppliers"]
        self.suppliers_catalog = self.game_data.get("suppliers_catalog", {})
        self.ingredient_gammes = self.game_data.get("ingredient_gammes", {})
        self.hr_tables = self.game_data["hr_tables"]

        # Gestionnaires
        self.commerce_manager = CommerceManager()
        show_progress_bar(3, 5, "Initialisation des moteurs")

        self.market_engine = MarketEngine(self.scenario, self.scenario.random_seed)
        self.cost_calculator = RecipeCostCalculator(self.ingredients)
        self.decision_menu = DecisionMenu(self.ui, self.cost_calculator)
        # Injection des catalogues et paramètres admin
        self.decision_menu.set_suppliers_catalog(self.suppliers_catalog)
        self.decision_menu.set_admin_settings(
            "/home/lepagnol/Documents/Perso/Games/Foodopsmini/admin_configs/Session_FoodOps_Pro_2025.json"
        )

        show_progress_bar(4, 5, "Finalisation")

        # État du jeu
        self.players: List[Restaurant] = []
        self.ai_competitors: List[Restaurant] = []
        self.current_turn = 1

        show_progress_bar(5, 5, "Prêt !")
        # Ligne vide après la barre de progression

    def load_settings(self, config_path: str) -> AdminSettings:
        """Charge les paramètres administrateur depuis un fichier JSON."""
        with open(config_path, "r", encoding="utf-8") as f:
            settings_data = yaml.safe_load(f)
        return AdminSettings(**settings_data)

    def start_game(self) -> None:
        """Lance le jeu principal."""
        # Écran d'accueil avec scénario
        show_welcome_screen(self.scenario)
        pause()
        # Sélection et achat des fonds de commerce
        self._commerce_selection_phase()

        # Configuration des restaurants
        self._setup_players()

        # Création des concurrents IA
        self._create_ai_competitors()

        # Boucle de jeu principale
        self._game_loop()

        # Fin de partie
        self._end_game()

    def _commerce_selection_phase(self) -> None:
        """Phase de sélection et achat des fonds de commerce."""
        clear_screen()

        intro = [
            "🏪 PHASE D'ACQUISITION",
            "",
            "Avant de commencer votre aventure entrepreneuriale,",
            "vous devez choisir et acheter un fonds de commerce.",
            "",
            "Chaque emplacement a ses avantages et inconvénients.",
            "Analysez bien votre budget et votre stratégie !",
        ]
        print_box(intro, "ACQUISITION DE FONDS DE COMMERCE", "header")
        pause()

        # Détermination du nombre de joueurs
        max_players = self.admin_settings.max_players

        num_players = get_input(
            f"Nombre de joueurs (1-{max_players})",
            int,
            min_val=1,
            max_val=max_players,
            default=1,
        )

        # Sélection des commerces pour chaque joueur
        for i in range(num_players):
            self._select_commerce_for_player(i + 1)

    def _select_commerce_for_player(self, player_num: int) -> None:
        """Sélection du commerce pour un joueur."""
        clear_screen()

        # Budget du joueur
        budget = get_input(
            f"Budget du joueur {player_num} (€)",
            Decimal,
            min_val=self.admin_settings.starting_budget_min,
            max_val=self.admin_settings.starting_budget_max,
            default=(
                self.admin_settings.starting_budget_min
                + self.admin_settings.starting_budget_max
            )
            / 2,
        )

        # Affichage des commerces disponibles
        available_locations = self.commerce_manager.get_available_locations(budget)

        if not available_locations:
            show_error(f"Aucun commerce disponible avec un budget de {budget:.0f}€")
            return
        clear_screen()

        # Affichage détaillé des options
        for i, location in enumerate(available_locations):
            location.display_commerce_details(i + 1)

        # Sélection
        location_options = [
            f"{loc.name} - {loc.price:.0f}€ ({loc.location_type.value})"
            for loc in available_locations
        ]

        choice = show_menu(
            f"JOUEUR {player_num} - Choisissez votre fonds de commerce",
            location_options,
        )
        selected_location = available_locations[choice - 1]

        # Confirmation d'achat
        selected_location.display_confirm_commerce_purchase(budget)
        if confirm("Confirmer l'achat de ce fonds de commerce ?"):
            # Création du restaurant
            restaurant = self._create_restaurant_from_commerce(
                selected_location, budget, player_num
            )
            self.players.append(restaurant)

            show_success("Félicitations !")
            show_info(
                f"Vous êtes maintenant propriétaire de '{selected_location.name}'"
            )
            pause()

    def _create_restaurant_from_commerce(
        self, location: CommerceLocation, budget: Decimal, player_num: int
    ) -> Restaurant:
        """Crée un restaurant à partir d'un commerce acheté."""
        # Nom du restaurant
        restaurant_name = get_input(
            "Nom de votre restaurant", default=f"Restaurant {player_num}"
        )

        # Création du restaurant
        remaining_budget = budget - location.total_initial_cost

        restaurant = Restaurant(
            id=f"player_{player_num}",
            name=restaurant_name,
            type=location.restaurant_type,
            capacity_base=location.size,
            speed_service=self._get_speed_for_type(location.restaurant_type),
            cash=remaining_budget,
            rent_monthly=location.rent_monthly,
            fixed_costs_monthly=location.rent_monthly * Decimal("0.3"),  # Estimation
            equipment_value=Decimal("50000"),  # Valeur standard
            staffing_level=2,
        )

        # Ajout d'employés de base
        self._add_base_employees(restaurant, location.restaurant_type)

        # Menu de base
        self._setup_base_menu(restaurant, location.restaurant_type)

        return restaurant

    def _get_speed_for_type(self, restaurant_type: RestaurantType) -> Decimal:
        """Retourne la vitesse de service selon le type."""
        speeds = {
            RestaurantType.FAST: Decimal("1.4"),
            RestaurantType.CLASSIC: Decimal("1.0"),
            RestaurantType.GASTRONOMIQUE: Decimal("0.7"),
            RestaurantType.BRASSERIE: Decimal("1.1"),
        }
        return speeds.get(restaurant_type, Decimal("1.0"))

    def _add_base_employees(
        self, restaurant: Restaurant, restaurant_type: RestaurantType
    ) -> None:
        """Ajoute les employés de base selon le type de restaurant."""
        base_configs = {
            RestaurantType.FAST: [
                (EmployeePosition.CUISINE, 2000),
                (EmployeePosition.CAISSE, 1700),
            ],
            RestaurantType.CLASSIC: [
                (EmployeePosition.CUISINE, 2300),
                (EmployeePosition.SALLE, 2000),
            ],
            RestaurantType.GASTRONOMIQUE: [
                (EmployeePosition.CUISINE, 2800),
                (EmployeePosition.SALLE, 2200),
            ],
            RestaurantType.BRASSERIE: [
                (EmployeePosition.CUISINE, 2200),
                (EmployeePosition.SALLE, 1900),
            ],
        }

        employee_configs = base_configs.get(
            restaurant_type, base_configs[RestaurantType.CLASSIC]
        )

        for i, (position, salary) in enumerate(employee_configs):
            employee = Employee(
                id=f"{restaurant.id}_emp_{i + 1}",
                name=f"{position.value.title()} {i + 1}",
                position=position,
                contract=EmployeeContract.CDI,
                salary_gross_monthly=Decimal(str(salary)),
                productivity=Decimal("1.0"),
                experience_months=12,
            )
            restaurant.add_employee(employee)

    def _setup_base_menu(
        self, restaurant: Restaurant, restaurant_type: RestaurantType
    ) -> None:
        """Configure le menu de base selon le type de restaurant."""
        menu_configs = {
            RestaurantType.FAST: [
                ("burger_classic", 10.50),
                ("burger_chicken", 11.00),
                ("menu_enfant", 8.50),
            ],
            RestaurantType.CLASSIC: [
                ("pasta_bolognese", 16.00),
                ("steak_frites", 22.00),
                ("salad_caesar", 14.00),
            ],
            RestaurantType.GASTRONOMIQUE: [
                ("bowl_salmon", 28.00),
                ("risotto_mushroom", 24.00),
            ],
            RestaurantType.BRASSERIE: [
                ("croque_monsieur", 11.50),
                ("omelet_cheese", 13.00),
                ("soup_tomato", 8.50),
            ],
        }

        recipes_for_type = menu_configs.get(
            restaurant_type, menu_configs[RestaurantType.CLASSIC]
        )

        for recipe_id, price in recipes_for_type:
            if recipe_id in self.recipes:
                restaurant.set_recipe_price(recipe_id, Decimal(str(price)))
                restaurant.activate_recipe(recipe_id)

    def _setup_players(self) -> None:
        """Configuration finale des joueurs (si nécessaire)."""
        # Les joueurs sont déjà configurés dans la phase commerce
        if not self.players:
            show_error("Aucun joueur configuré !")
            return

        show_success(f"{len(self.players)} restaurant(s) prêt(s) à ouvrir !")
        pause()

    def _create_ai_competitors(self) -> None:
        """Crée les concurrents IA."""
        for i in range(self.admin_settings.ai_count):
            ai_configs = [
                ("Chez Mario", RestaurantType.CLASSIC),
                ("Quick Burger", RestaurantType.FAST),
                ("Le Gourmet", RestaurantType.GASTRONOMIQUE),
                ("Brasserie du Port", RestaurantType.BRASSERIE),
            ]

            if i < len(ai_configs):
                name, rest_type = ai_configs[i]
            else:
                name, _rest_type = f"Concurrent {i + 1}", RestaurantType.CLASSIC

            # Sélection d'un commerce pour l'IA
            available_locations = self.commerce_manager.get_available_locations(
                Decimal("50000")  # Budget standard pour l'IA
            )

            if available_locations:
                location = available_locations[0]  # Premier disponible
                ai_restaurant = self._create_restaurant_from_commerce(
                    location, Decimal("50000"), f"ai_{i + 1}"
                )
                ai_restaurant.name = name
                ai_restaurant.id = f"ai_{i + 1}"
                self.ai_competitors.append(ai_restaurant)

    def _game_loop(self) -> None:
        """Boucle principale du jeu avec menu de décisions enrichi."""
        total_turns = self.admin_settings.total_turns

        for turn in range(1, total_turns + 1):
            self.current_turn = turn

            # Décisions des joueurs avec menu enrichi
            for player in self.players:
                decisions = self.decision_menu.show_decision_menu(
                    player, turn, self.recipes
                )
                self._apply_player_decisions(player, decisions)

            # Décisions de l'IA (simplifiées)
            self._ai_decisions()

            # Simulation du marché
            all_restaurants = self.players + self.ai_competitors
            results = self.market_engine.allocate_demand(all_restaurants, turn)

            # Affichage des résultats
            self._display_turn_results(results, turn)

            # Mise à jour des restaurants
            self._update_restaurants(results)

            # Pause entre les tours
            if turn < total_turns:
                pause("Appuyez sur Entrée pour continuer au tour suivant...")

    def _apply_player_decisions(self, restaurant: Restaurant, decisions: Dict) -> None:
        """Applique les décisions du joueur au restaurant."""
        # Changements de prix
        if "price_changes" in decisions:
            for recipe_id, new_price in decisions["price_changes"].items():
                restaurant.set_recipe_price(recipe_id, new_price)

        # Recrutements
        if "recruitments" in decisions:
            for recruit_data in decisions["recruitments"]:
                employee = Employee(
                    id=f"{restaurant.id}_new_{len(restaurant.employees) + 1}",
                    name=f"Nouveau {recruit_data['position'].value}",
                    position=recruit_data["position"],
                    contract=recruit_data["contract"],
                    salary_gross_monthly=recruit_data["salary"],
                    productivity=Decimal("1.0"),
                    experience_months=0,
                )
                restaurant.add_employee(employee)

        # Campagnes marketing
        if "marketing_campaigns" in decisions:
            for campaign in decisions["marketing_campaigns"]:
                # Déduction du coût
                restaurant.update_cash(-Decimal(str(campaign["cost"])))
                # L'effet sera appliqué dans la simulation de marché

    def _ai_decisions(self) -> None:
        """Décisions simplifiées de l'IA."""
        for ai in self.ai_competitors:
            # Stratégie simple selon la difficulté
            if self.admin_settings.ai_difficulty == "easy":
                ai.staffing_level = 2  # Niveau fixe
            elif self.admin_settings.ai_difficulty == "medium":
                # Ajustement selon la performance
                if hasattr(ai, "_last_utilization"):
                    if ai._last_utilization > 0.8:
                        ai.staffing_level = min(3, ai.staffing_level + 1)
                    elif ai._last_utilization < 0.5:
                        ai.staffing_level = max(1, ai.staffing_level - 1)
            # Mode "hard" : IA plus agressive (à implémenter)

    def _display_turn_results(self, results: Dict, turn: int) -> None:
        """Affiche les résultats du tour."""
        clear_screen()

        header = [
            f"📊 RÉSULTATS DU TOUR {turn}/{self.admin_settings.total_turns}",
            f"Période simulée: {self.admin_settings.turn_duration_description}",
        ]
        print_box(header, style="header")

        # Tableau des résultats
        results_lines = [
            f"{'Restaurant':<25} {'Demande':<8} {'Servi':<8} {'Capacité':<10} {'Util.':<8} {'CA €':<12}"
        ]
        results_lines.append("-" * 80)

        all_restaurants = self.players + self.ai_competitors

        for restaurant in all_restaurants:
            if restaurant.id in results:
                result = results[restaurant.id]
                utilization_pct = f"{result.utilization_rate:.1%}"

                # Marqueur pour les joueurs
                marker = "👤" if restaurant in self.players else "🤖"

                results_lines.append(
                    f"{marker} {restaurant.name:<23} "
                    f"{result.allocated_demand:<8} "
                    f"{result.served_customers:<8} "
                    f"{result.capacity:<10} "
                    f"{utilization_pct:<8} "
                    f"{result.revenue:<12.0f}"
                )

        print_box(results_lines, "PERFORMANCE", "info")

        # Analyse du marché
        market_analysis = self.market_engine.get_market_analysis()
        analysis_lines = [
            "📈 ANALYSE DU MARCHÉ",
            f"• Total clients servis: {market_analysis['total_served']}",
            f"• Chiffre d'affaires total: {market_analysis['total_revenue']:.0f}€",
            f"• Taux d'utilisation marché: {market_analysis['market_utilization']:.1%}",
            f"• Satisfaction de la demande: {market_analysis['demand_satisfaction']:.1%}",
        ]

        print_box(analysis_lines, style="warning")

    def _update_restaurants(self, results: Dict) -> None:
        """Met à jour l'état des restaurants après le tour."""
        for restaurant in self.players + self.ai_competitors:
            if restaurant.id in results:
                result = results[restaurant.id]

                # Sauvegarde pour l'IA
                restaurant._last_utilization = float(result.utilization_rate)
                restaurant._last_customers_served = result.served_customers

                # Mise à jour de la trésorerie (profit approximatif)
                # Calcul simplifié : CA - coûts variables (30%) - coûts fixes
                variable_costs = result.revenue * Decimal("0.30")
                fixed_costs = restaurant.rent_monthly + restaurant.fixed_costs_monthly

                # Coûts de personnel
                personnel_costs = sum(
                    emp.salary_gross_monthly * Decimal("1.42")  # Avec charges
                    for emp in restaurant.employees
                )

                profit = (
                    result.revenue
                    - variable_costs
                    - (fixed_costs / 4)
                    - (personnel_costs / 4)
                )
                restaurant.update_cash(profit)

    def _end_game(self) -> None:
        """Gestion de la fin de partie."""
        clear_screen()

        # Classement final
        all_restaurants = self.players + self.ai_competitors
        ranking = sorted(all_restaurants, key=lambda r: r.cash, reverse=True)

        final_ranking = ["🏆 CLASSEMENT FINAL:"]

        for i, restaurant in enumerate(ranking, 1):
            marker = "👤" if restaurant in self.players else "🤖"
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."

            final_ranking.append(
                f"{medal} {marker} {restaurant.name:<25} {restaurant.cash:>12.0f}€"
            )

        print_box(final_ranking, style="success")

        # Félicitations au gagnant
        winner = ranking[0]
        if winner in self.players:
            show_success(f"🎉 Félicitations ! '{winner.name}' remporte la partie !")
        else:
            show_info(f"🤖 L'IA '{winner.name}' remporte cette partie. Réessayez !")

        # Proposition d'export
        if confirm("Exporter les résultats de la partie ?"):
            self._export_results()

        pause("Merci d'avoir joué à FoodOps Pro !")

    def _export_results(self) -> None:
        """Exporte les résultats de la partie."""
        try:
            from pathlib import Path

            output_dir = Path("exports")
            output_dir.mkdir(exist_ok=True)

            # Création d'un état de jeu pour l'export
            persistence = GameStatePersistence()
            game_state = persistence.create_game_state(
                self.scenario, self.players, self.ai_competitors
            )

            # Export JSON
            exporter = ResultsExporter()
            json_file = output_dir / f"results_{game_state.game_id}.json"
            exporter.export_to_json(game_state, json_file)

            show_success(f"✅ Résultats exportés vers {json_file}")

        except Exception as e:
            show_error(f"❌ Erreur lors de l'export : {e}")


def main() -> None:
    """Point d'entrée principal."""
    print("🍽️ LANCEMENT FOODOPS PRO")
    print("=" * 40)
    print("Version Pro avec interface enrichie")
    print("Achat de fonds de commerce, décisions avancées")
    print("=" * 40)
    scenario_path = Path(
        "/home/lepagnol/Documents/Perso/Games/Foodopsmini/examples/scenarios/base.yaml"
    )
    game = FoodOpsProGame(scenario_path)
    # Passer les recettes au DecisionMenu pour Achats & Stocks
    game.decision_menu.cache_available_recipes(game.recipes)
    game.start_game()


if __name__ == "__main__":
    main()
