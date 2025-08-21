"""
Tests pour le calcul des coûts de recettes.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from src.foodops_pro.domain.ingredient import Ingredient
from src.foodops_pro.domain.recipe import Recipe, RecipeItem
from src.foodops_pro.domain.stock import StockLot
from src.foodops_pro.core.costing import (
    RecipeCostCalculator,
    CostBreakdown,
    IngredientCost,
)


@pytest.fixture
def sample_ingredients():
    """Ingrédients de test."""
    return {
        "beef": Ingredient(
            id="beef",
            name="Steak haché",
            unit="kg",
            cost_ht=Decimal("8.50"),
            vat_rate=Decimal("0.055"),
            shelf_life_days=3,
            category="viande",
        ),
        "bread": Ingredient(
            id="bread",
            name="Pain burger",
            unit="pièce",
            cost_ht=Decimal("0.35"),
            vat_rate=Decimal("0.055"),
            shelf_life_days=3,
            category="boulangerie",
        ),
        "cheese": Ingredient(
            id="cheese",
            name="Fromage",
            unit="kg",
            cost_ht=Decimal("12.50"),
            vat_rate=Decimal("0.055"),
            shelf_life_days=21,
            category="fromage",
        ),
    }


@pytest.fixture
def sample_recipe(sample_ingredients):
    """Recette de test (burger)."""
    return Recipe(
        id="burger_test",
        name="Burger Test",
        items=[
            RecipeItem(
                ingredient_id="beef",
                qty_brute=Decimal("0.125"),  # 125g
                rendement_prepa=Decimal("1.0"),
                rendement_cuisson=Decimal("0.85"),  # 15% de perte à la cuisson
            ),
            RecipeItem(
                ingredient_id="bread",
                qty_brute=Decimal("1"),  # 1 pain
                rendement_prepa=Decimal("1.0"),
                rendement_cuisson=Decimal("1.0"),
            ),
            RecipeItem(
                ingredient_id="cheese",
                qty_brute=Decimal("0.03"),  # 30g
                rendement_prepa=Decimal("1.0"),
                rendement_cuisson=Decimal("1.0"),
            ),
        ],
        temps_prepa_min=8,
        temps_service_min=3,
        portions=1,
        category="plat",
        difficulty=2,
    )


@pytest.fixture
def sample_stock_lots():
    """Lots de stock de test."""
    today = date.today()
    return [
        StockLot(
            ingredient_id="beef",
            quantity=Decimal("5.0"),
            dlc=today + timedelta(days=2),
            unit_cost_ht=Decimal("8.00"),  # Prix inférieur au catalogue
            vat_rate=Decimal("0.055"),
            supplier_id="supplier1",
            received_date=today,
        ),
        StockLot(
            ingredient_id="beef",
            quantity=Decimal("3.0"),
            dlc=today + timedelta(days=1),  # Expire plus tôt (FEFO)
            unit_cost_ht=Decimal("7.50"),  # Prix encore plus bas
            vat_rate=Decimal("0.055"),
            supplier_id="supplier2",
            received_date=today,
        ),
        StockLot(
            ingredient_id="cheese",
            quantity=Decimal("2.0"),
            dlc=today + timedelta(days=15),
            unit_cost_ht=Decimal("13.00"),  # Prix supérieur au catalogue
            vat_rate=Decimal("0.055"),
            supplier_id="supplier1",
            received_date=today,
        ),
    ]


class TestRecipeCostCalculator:
    """Tests du calculateur de coûts de recettes."""

    def test_calculator_initialization(self, sample_ingredients):
        """Test de l'initialisation du calculateur."""
        calculator = RecipeCostCalculator(sample_ingredients)

        assert calculator.ingredients == sample_ingredients
        assert calculator.hourly_labor_cost == Decimal("15.0")  # Valeur par défaut

    def test_calculator_custom_labor_cost(self, sample_ingredients):
        """Test avec coût de main d'œuvre personnalisé."""
        custom_cost = Decimal("20.0")
        calculator = RecipeCostCalculator(sample_ingredients, custom_cost)

        assert calculator.hourly_labor_cost == custom_cost

    def test_basic_recipe_cost_calculation(self, sample_ingredients, sample_recipe):
        """Test de calcul de coût de base sans stock."""
        calculator = RecipeCostCalculator(sample_ingredients)
        breakdown = calculator.calculate_recipe_cost(sample_recipe)

        # Vérifications de base
        assert isinstance(breakdown, CostBreakdown)
        assert breakdown.recipe_id == sample_recipe.id
        assert breakdown.recipe_name == sample_recipe.name
        assert breakdown.portions == sample_recipe.portions
        assert len(breakdown.ingredient_costs) == len(sample_recipe.items)

        # Vérification des coûts
        assert breakdown.total_cost_ht > Decimal("0")
        assert breakdown.cost_per_portion > Decimal("0")
        assert breakdown.preparation_time_cost > Decimal("0")
        assert breakdown.total_cost_with_labor > breakdown.total_cost_ht

    def test_ingredient_cost_calculation(self, sample_ingredients, sample_recipe):
        """Test du calcul détaillé des coûts d'ingrédients."""
        calculator = RecipeCostCalculator(sample_ingredients)
        breakdown = calculator.calculate_recipe_cost(sample_recipe)

        # Vérification des coûts par ingrédient
        beef_cost = None
        bread_cost = None
        cheese_cost = None

        for ingredient_cost in breakdown.ingredient_costs:
            if ingredient_cost.ingredient_id == "beef":
                beef_cost = ingredient_cost
            elif ingredient_cost.ingredient_id == "bread":
                bread_cost = ingredient_cost
            elif ingredient_cost.ingredient_id == "cheese":
                cheese_cost = ingredient_cost

        # Vérifications spécifiques
        assert beef_cost is not None
        assert beef_cost.quantity_used == Decimal("0.125")
        assert beef_cost.unit_cost_ht == sample_ingredients["beef"].cost_ht
        assert beef_cost.total_cost_ht == Decimal("0.125") * Decimal("8.50")

        assert bread_cost is not None
        assert bread_cost.quantity_used == Decimal("1")
        assert bread_cost.total_cost_ht == Decimal("0.35")

        assert cheese_cost is not None
        assert cheese_cost.quantity_used == Decimal("0.03")

    def test_recipe_cost_with_stock(
        self, sample_ingredients, sample_recipe, sample_stock_lots
    ):
        """Test du calcul avec gestion des stocks FEFO."""
        calculator = RecipeCostCalculator(sample_ingredients)
        breakdown = calculator.calculate_recipe_cost(sample_recipe, sample_stock_lots)

        # Le coût du bœuf devrait utiliser le stock (FEFO = lot qui expire en premier)
        beef_cost = next(
            cost for cost in breakdown.ingredient_costs if cost.ingredient_id == "beef"
        )

        # Devrait utiliser le lot à 7.50€ (expire plus tôt)
        assert beef_cost.unit_cost_ht == Decimal("7.50")
        assert beef_cost.supplier_id == "supplier2"

        # Le fromage devrait utiliser le stock même si plus cher
        cheese_cost = next(
            cost
            for cost in breakdown.ingredient_costs
            if cost.ingredient_id == "cheese"
        )
        assert cheese_cost.unit_cost_ht == Decimal("13.00")

    def test_recipe_cost_insufficient_stock(self, sample_ingredients, sample_recipe):
        """Test avec stock insuffisant."""
        # Stock très limité
        limited_stock = [
            StockLot(
                ingredient_id="beef",
                quantity=Decimal("0.05"),  # Moins que nécessaire
                dlc=date.today() + timedelta(days=2),
                unit_cost_ht=Decimal("7.00"),
                vat_rate=Decimal("0.055"),
                supplier_id="supplier1",
                received_date=date.today(),
            )
        ]

        calculator = RecipeCostCalculator(sample_ingredients)
        breakdown = calculator.calculate_recipe_cost(sample_recipe, limited_stock)

        # Devrait utiliser le stock disponible + prix catalogue pour le reste
        beef_cost = next(
            cost for cost in breakdown.ingredient_costs if cost.ingredient_id == "beef"
        )

        # Le coût devrait être un mélange des deux prix
        expected_cost = (
            Decimal("0.05") * Decimal("7.00")  # Stock disponible
            + Decimal("0.075") * Decimal("8.50")  # Complément au prix catalogue
        ) / Decimal("0.125")

        assert abs(beef_cost.unit_cost_ht - expected_cost) < Decimal("0.01")

    def test_labor_cost_calculation(self, sample_ingredients, sample_recipe):
        """Test du calcul du coût de main d'œuvre."""
        hourly_cost = Decimal("18.0")
        calculator = RecipeCostCalculator(sample_ingredients, hourly_cost)
        breakdown = calculator.calculate_recipe_cost(sample_recipe)

        # Temps total : 8 + 3 = 11 minutes = 11/60 heures
        expected_labor_cost = (Decimal("11") / Decimal("60")) * hourly_cost

        assert abs(breakdown.preparation_time_cost - expected_labor_cost) < Decimal(
            "0.01"
        )

    def test_missing_ingredient_error(self, sample_ingredients):
        """Test d'erreur avec ingrédient manquant."""
        # Recette avec ingrédient inexistant
        invalid_recipe = Recipe(
            id="invalid",
            name="Invalid Recipe",
            items=[
                RecipeItem(
                    ingredient_id="nonexistent",
                    qty_brute=Decimal("1.0"),
                    rendement_prepa=Decimal("1.0"),
                    rendement_cuisson=Decimal("1.0"),
                )
            ],
            temps_prepa_min=5,
            temps_service_min=2,
            portions=1,
        )

        calculator = RecipeCostCalculator(sample_ingredients)

        with pytest.raises(ValueError, match="Ingrédient nonexistent non trouvé"):
            calculator.calculate_recipe_cost(invalid_recipe)

    def test_margin_analysis(self, sample_ingredients, sample_recipe):
        """Test de l'analyse de marge."""
        calculator = RecipeCostCalculator(sample_ingredients)

        selling_price_ttc = Decimal("12.50")
        vat_rate = Decimal("0.10")

        analysis = calculator.calculate_margin_analysis(
            sample_recipe, selling_price_ttc, vat_rate
        )

        # Vérifications
        assert "selling_price_ht" in analysis
        assert "cost_per_portion" in analysis
        assert "margin_ht" in analysis
        assert "margin_percentage" in analysis
        assert "food_cost_percentage" in analysis
        assert "labor_cost_per_portion" in analysis

        # Cohérence des calculs
        expected_price_ht = selling_price_ttc / (1 + vat_rate)
        assert abs(analysis["selling_price_ht"] - expected_price_ht) < Decimal("0.01")

        assert analysis["margin_ht"] >= Decimal("0")  # Marge positive attendue
        assert Decimal("0") <= analysis["margin_percentage"] <= Decimal("100")
        assert analysis["food_cost_percentage"] >= Decimal("0")

    def test_recipe_optimization_suggestions(self, sample_ingredients, sample_recipe):
        """Test des suggestions d'optimisation."""
        calculator = RecipeCostCalculator(sample_ingredients)

        suggestions = calculator.optimize_recipe_cost(sample_recipe, Decimal("30"))

        # Vérifications
        assert isinstance(suggestions, dict)
        assert len(suggestions) <= 3  # Top 3 des ingrédients les plus coûteux

        for key, suggestion in suggestions.items():
            assert "name" in suggestion
            assert "current_cost" in suggestion
            assert "percentage_of_total" in suggestion
            assert "reduction_potential" in suggestion

            assert suggestion["current_cost"] >= Decimal("0")
            assert suggestion["percentage_of_total"] >= Decimal("0")
            assert suggestion["reduction_potential"] >= Decimal("0")


class TestIngredientCost:
    """Tests de la classe IngredientCost."""

    def test_ingredient_cost_creation(self):
        """Test de création d'un coût d'ingrédient."""
        cost = IngredientCost(
            ingredient_id="test",
            ingredient_name="Test Ingredient",
            quantity_used=Decimal("0.5"),
            unit_cost_ht=Decimal("10.0"),
            total_cost_ht=Decimal("5.0"),
            waste_percentage=Decimal("15.0"),
            supplier_id="supplier1",
        )

        assert cost.ingredient_id == "test"
        assert cost.ingredient_name == "Test Ingredient"
        assert cost.quantity_used == Decimal("0.5")
        assert cost.unit_cost_ht == Decimal("10.0")
        assert cost.total_cost_ht == Decimal("5.0")
        assert cost.waste_percentage == Decimal("15.0")
        assert cost.supplier_id == "supplier1"


class TestCostBreakdown:
    """Tests de la classe CostBreakdown."""

    def test_cost_breakdown_creation(self):
        """Test de création d'une décomposition de coûts."""
        ingredient_costs = [
            IngredientCost(
                ingredient_id="ing1",
                ingredient_name="Ingredient 1",
                quantity_used=Decimal("1.0"),
                unit_cost_ht=Decimal("5.0"),
                total_cost_ht=Decimal("5.0"),
            ),
            IngredientCost(
                ingredient_id="ing2",
                ingredient_name="Ingredient 2",
                quantity_used=Decimal("0.5"),
                unit_cost_ht=Decimal("8.0"),
                total_cost_ht=Decimal("4.0"),
            ),
        ]

        breakdown = CostBreakdown(
            recipe_id="test_recipe",
            recipe_name="Test Recipe",
            portions=2,
            ingredient_costs=ingredient_costs,
            preparation_time_cost=Decimal("3.0"),
        )

        # Vérification des calculs automatiques
        assert breakdown.total_cost_ht == Decimal("9.0")  # 5.0 + 4.0
        assert breakdown.cost_per_portion == Decimal("4.5")  # 9.0 / 2
        assert breakdown.total_cost_with_labor == Decimal("12.0")  # 9.0 + 3.0

    def test_cost_breakdown_empty_ingredients(self):
        """Test avec liste d'ingrédients vide."""
        breakdown = CostBreakdown(
            recipe_id="empty",
            recipe_name="Empty Recipe",
            portions=1,
            ingredient_costs=[],
            preparation_time_cost=Decimal("2.0"),
        )

        assert breakdown.total_cost_ht == Decimal("0")
        assert breakdown.cost_per_portion == Decimal("0")
        assert breakdown.total_cost_with_labor == Decimal("2.0")


class TestRecipeItemWaste:
    """Tests spécifiques aux pertes dans les recettes."""

    def test_waste_calculation_in_costing(self, sample_ingredients):
        """Test de prise en compte des pertes dans le calcul."""
        # Recette avec pertes importantes
        recipe_with_waste = Recipe(
            id="waste_test",
            name="Recipe with Waste",
            items=[
                RecipeItem(
                    ingredient_id="beef",
                    qty_brute=Decimal("1.0"),
                    rendement_prepa=Decimal("0.8"),  # 20% de perte à la préparation
                    rendement_cuisson=Decimal("0.7"),  # 30% de perte à la cuisson
                )
            ],
            temps_prepa_min=10,
            temps_service_min=5,
            portions=1,
        )

        calculator = RecipeCostCalculator(sample_ingredients)
        breakdown = calculator.calculate_recipe_cost(recipe_with_waste)

        beef_cost = breakdown.ingredient_costs[0]

        # Vérification du calcul des pertes
        expected_waste = (1 - Decimal("0.8") * Decimal("0.7")) * 100
        assert abs(beef_cost.waste_percentage - expected_waste) < Decimal("0.1")

        # Le coût devrait être basé sur la quantité brute
        assert beef_cost.quantity_used == Decimal("1.0")
        assert beef_cost.total_cost_ht == Decimal("8.50")  # 1.0 * 8.50
