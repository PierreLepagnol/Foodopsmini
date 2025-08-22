"""
Tests d'intégration pour FoodOps Pro.
"""

import pytest
from pathlib import Path
from decimal import Decimal

from src.foodops_pro.io.data_loader import DataLoader
from src.foodops_pro.core.market import MarketEngine
from src.foodops_pro.core.costing import RecipeCostCalculator
from src.foodops_pro.core.payroll import PayrollCalculator
from src.foodops_pro.core.ledger import Ledger
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType


@pytest.mark.integration
class TestGameIntegration:
    """Tests d'intégration du jeu complet."""

    def test_data_loading_integration(self):
        """Test de chargement complet des données."""
        loader = DataLoader()

        # Chargement de toutes les données
        try:
            data = loader.load_all_data()
        except Exception as e:
            pytest.fail(f"Échec du chargement des données : {e}")

        # Vérifications
        assert "ingredients" in data
        assert "recipes" in data
        assert "suppliers" in data
        assert "hr_tables" in data
        assert "scenario" in data

        # Vérification de la cohérence des données
        ingredients = data["ingredients"]
        recipes = data["recipes"]

        # Toutes les recettes doivent avoir des ingrédients valides
        for recipe in recipes.values():
            for item in recipe.items:
                assert item.ingredient_id in ingredients, (
                    f"Ingrédient {item.ingredient_id} manquant pour la recette {recipe.id}"
                )

    def test_market_and_costing_integration(self):
        """Test d'intégration marché et calcul de coûts."""
        loader = DataLoader()
        data = loader.load_all_data()

        # Création d'un restaurant
        restaurant = Restaurant(
            id="integration_test",
            name="Restaurant Intégration",
            type=RestaurantType.CLASSIC,
            capacity_base=50,
            speed_service=Decimal("1.0"),
            staffing_level=2,
        )

        # Configuration du menu avec des recettes réelles
        available_recipes = list(data["recipes"].keys())[:3]
        for recipe_id in available_recipes:
            restaurant.set_recipe_price(recipe_id, Decimal("15.00"))
            restaurant.activate_recipe(recipe_id)

        # Test du moteur de marché
        scenario = data["scenario"]
        market_engine = MarketEngine(scenario, random_seed=42)

        results = market_engine.allocate_demand([restaurant], turn=1)

        # Vérifications
        assert restaurant.id in results
        result = results[restaurant.id]
        assert result.served_customers >= 0
        assert result.revenue >= Decimal("0")

        # Test du calcul de coûts
        cost_calculator = RecipeCostCalculator(data["ingredients"])

        for recipe_id in available_recipes:
            if recipe_id in data["recipes"]:
                recipe = data["recipes"][recipe_id]
                try:
                    breakdown = cost_calculator.calculate_recipe_cost(recipe)
                    assert breakdown.total_cost_ht > Decimal("0")
                    assert breakdown.cost_per_portion > Decimal("0")
                except Exception as e:
                    pytest.fail(f"Échec du calcul de coût pour {recipe_id} : {e}")

    def test_payroll_and_ledger_integration(self, sample_restaurant):
        """Test d'intégration paie et comptabilité."""
        loader = DataLoader()
        data = loader.load_all_data()

        # Configuration de la paie
        hr_config = data["hr_tables"]["social_charges"]
        payroll_calculator = PayrollCalculator(hr_config)

        # Calcul de la paie pour les employés
        payroll_results = payroll_calculator.calculate_team_payroll(
            sample_restaurant.employees, period="2024-01"
        )

        # Vérifications
        assert len(payroll_results) == len(sample_restaurant.employees)

        # Intégration avec la comptabilité
        ledger = Ledger()

        # Enregistrement des paies
        for result in payroll_results:
            ledger.record_payroll(
                result.gross_salary,
                result.social_charges_employer,
                payroll_date=None,  # Utilise la date du jour
                description=f"Paie {result.employee_name}",
            )

        # Vérifications comptables
        total_gross = sum(r.gross_salary for r in payroll_results)
        total_charges = sum(r.social_charges_employer for r in payroll_results)

        assert ledger.get_balance("641") == total_gross  # Rémunérations
        assert ledger.get_balance("645") == total_charges  # Charges sociales

        # Génération du compte de résultat
        pnl = ledger.get_profit_loss()
        assert pnl["expenses"] == total_gross + total_charges

    def test_complete_turn_simulation(self):
        """Test de simulation d'un tour complet."""
        loader = DataLoader()
        data = loader.load_all_data()

        # Création de restaurants
        restaurants = [
            Restaurant(
                id="resto1",
                name="Restaurant 1",
                type=RestaurantType.FAST,
                capacity_base=80,
                speed_service=Decimal("1.3"),
                staffing_level=2,
                cash=Decimal("15000"),
            ),
            Restaurant(
                id="resto2",
                name="Restaurant 2",
                type=RestaurantType.CLASSIC,
                capacity_base=60,
                speed_service=Decimal("1.0"),
                staffing_level=2,
                cash=Decimal("20000"),
            ),
        ]

        # Configuration des menus
        fast_recipes = ["burger_classic", "burger_chicken", "menu_enfant"]
        classic_recipes = ["pasta_bolognese", "steak_frites", "salad_caesar"]

        for recipe_id in fast_recipes:
            if recipe_id in data["recipes"]:
                restaurants[0].set_recipe_price(recipe_id, Decimal("11.50"))
                restaurants[0].activate_recipe(recipe_id)

        for recipe_id in classic_recipes:
            if recipe_id in data["recipes"]:
                restaurants[1].set_recipe_price(recipe_id, Decimal("17.00"))
                restaurants[1].activate_recipe(recipe_id)

        # Simulation du marché
        scenario = data["scenario"]
        market_engine = MarketEngine(scenario, random_seed=42)

        # Simulation de plusieurs tours
        for turn in range(1, 4):
            results = market_engine.allocate_demand(restaurants, turn=turn)

            # Vérifications pour chaque restaurant
            for restaurant in restaurants:
                result = results[restaurant.id]

                # Mise à jour de la trésorerie (simulation simplifiée)
                if result.revenue > Decimal("0"):
                    # Profit approximatif (15% de marge)
                    profit = result.revenue * Decimal("0.15")
                    restaurant.update_cash(profit)

                # Vérifications
                assert result.served_customers <= result.capacity
                assert result.utilization_rate <= Decimal("1.0")

                if result.served_customers > 0:
                    assert result.revenue > Decimal("0")
                    assert result.average_ticket > Decimal("0")

        # Vérification de l'historique
        assert len(market_engine.turn_history) == 3

        # Analyse finale
        final_analysis = market_engine.get_market_analysis()
        assert final_analysis["total_served"] > 0
        assert final_analysis["total_revenue"] > 0

    def test_recipe_costing_with_real_data(self):
        """Test de calcul de coûts avec données réelles."""
        loader = DataLoader()
        data = loader.load_all_data()

        cost_calculator = RecipeCostCalculator(data["ingredients"])

        # Test sur toutes les recettes disponibles
        successful_calculations = 0

        for recipe_id, recipe in data["recipes"].items():
            try:
                breakdown = cost_calculator.calculate_recipe_cost(recipe)

                # Vérifications de base
                assert breakdown.recipe_id == recipe_id
                assert breakdown.total_cost_ht > Decimal("0")
                assert breakdown.cost_per_portion > Decimal("0")
                assert len(breakdown.ingredient_costs) == len(recipe.items)

                # Vérification de la cohérence des coûts
                manual_total = sum(
                    ic.total_cost_ht for ic in breakdown.ingredient_costs
                )
                assert abs(breakdown.total_cost_ht - manual_total) < Decimal("0.01")

                # Test d'analyse de marge
                selling_price = Decimal("20.00")
                margin_analysis = cost_calculator.calculate_margin_analysis(
                    recipe, selling_price, Decimal("0.10")
                )

                assert "margin_percentage" in margin_analysis
                assert "food_cost_percentage" in margin_analysis

                successful_calculations += 1

            except Exception as e:
                # Log de l'erreur mais ne fait pas échouer le test
                print(f"Erreur pour la recette {recipe_id}: {e}")

        # Au moins 80% des recettes doivent être calculables
        success_rate = successful_calculations / len(data["recipes"])
        assert success_rate >= 0.8, f"Taux de succès trop faible: {success_rate:.2%}"

    def test_vat_integration_with_sales(self):
        """Test d'intégration TVA avec les ventes."""
        loader = DataLoader()
        data = loader.load_all_data()

        ledger = Ledger()
        scenario = data["scenario"]

        # Simulation de ventes avec différents taux de TVA
        sales_data = [
            (Decimal("110.00"), scenario.get_vat_rate("food_onsite")),  # 10%
            (Decimal("121.00"), scenario.get_vat_rate("alcohol")),  # 20%
            (Decimal("105.50"), scenario.get_vat_rate("food_takeaway")),  # 5.5%
        ]

        total_vat_collected = Decimal("0")

        for amount_ttc, vat_rate in sales_data:
            ledger.record_sale(amount_ttc, vat_rate, None, "Vente test")

            # Calcul manuel de la TVA
            amount_ht = amount_ttc / (1 + vat_rate)
            vat_amount = amount_ttc - amount_ht
            total_vat_collected += vat_amount

        # Vérification du solde TVA collectée
        ledger_vat_collected = ledger.get_balance("44571")
        assert abs(ledger_vat_collected - total_vat_collected) < Decimal("0.01")

        # Simulation d'achats avec TVA déductible
        purchases_data = [
            (Decimal("100.00"), Decimal("0.055")),  # Produits alimentaires
            (Decimal("200.00"), Decimal("0.20")),  # Services
        ]

        total_vat_deductible = Decimal("0")

        for amount_ht, vat_rate in purchases_data:
            ledger.record_purchase(amount_ht, vat_rate, None, "Achat test")
            total_vat_deductible += amount_ht * vat_rate

        # Vérification du solde TVA déductible
        ledger_vat_deductible = ledger.get_balance("44566")
        assert abs(ledger_vat_deductible - total_vat_deductible) < Decimal("0.01")

        # Calcul de la TVA à payer
        vat_to_pay = total_vat_collected - total_vat_deductible
        ledger_vat_to_pay = ledger_vat_collected - ledger_vat_deductible

        assert abs(vat_to_pay - ledger_vat_to_pay) < Decimal("0.01")

    @pytest.mark.slow
    def test_performance_large_simulation(self):
        """Test de performance avec simulation importante."""
        loader = DataLoader()
        data = loader.load_all_data()

        # Création de nombreux restaurants
        restaurants = []
        for i in range(10):
            restaurant = Restaurant(
                id=f"resto_{i}",
                name=f"Restaurant {i}",
                type=RestaurantType.CLASSIC if i % 2 == 0 else RestaurantType.FAST,
                capacity_base=50 + i * 10,
                speed_service=Decimal("1.0"),
                staffing_level=2,
            )

            # Menu aléatoire
            recipes = list(data["recipes"].keys())[:5]
            for recipe_id in recipes:
                restaurant.set_recipe_price(recipe_id, Decimal("15.00") + i)
                restaurant.activate_recipe(recipe_id)

            restaurants.append(restaurant)

        # Simulation de marché
        scenario = data["scenario"]
        market_engine = MarketEngine(scenario, random_seed=42)

        # Mesure du temps (test de performance basique)
        import time

        start_time = time.time()

        # Simulation de 20 tours
        for turn in range(1, 21):
            results = market_engine.allocate_demand(restaurants, turn=turn)

            # Vérification rapide
            assert len(results) == len(restaurants)

        end_time = time.time()
        execution_time = end_time - start_time

        # Le test ne devrait pas prendre plus de 5 secondes
        assert execution_time < 5.0, f"Simulation trop lente: {execution_time:.2f}s"

        # Vérification de l'historique
        assert len(market_engine.turn_history) == 20
