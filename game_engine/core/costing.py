"""
Calcul des coûts de recettes pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from game_engine.domain.ingredient import Ingredient
from game_engine.domain.recipe import Recipe
from game_engine.domain.restaurant import RestaurantType
from game_engine.domain.stock import StockLot


@dataclass
class IngredientCost:
    """
    Coût détaillé d'un ingrédient dans une recette.

    Attributes:
        ingredient_id: ID de l'ingrédient
        ingredient_name: Nom de l'ingrédient
        quantity_used: Quantité utilisée
        unit_cost_ht: Coût unitaire HT
        total_cost_ht: Coût total HT
        waste_percentage: Pourcentage de perte
        supplier_id: ID du fournisseur
    """

    ingredient_id: str
    ingredient_name: str
    quantity_used: Decimal
    unit_cost_ht: Decimal
    total_cost_ht: Decimal
    waste_percentage: Decimal = Decimal("0")
    supplier_id: str = ""


@dataclass
class CostBreakdown:
    """
    Décomposition complète du coût d'une recette.

    Attributes:
        recipe_id: ID de la recette
        recipe_name: Nom de la recette
        portions: Nombre de portions
        ingredient_costs: Coûts par ingrédient
        total_cost_ht: Coût total HT
        cost_per_portion: Coût par portion
        preparation_time_cost: Coût du temps de préparation
        total_cost_with_labor: Coût total incluant main d'œuvre
    """

    recipe_id: str
    recipe_name: str
    portions: int
    ingredient_costs: list[IngredientCost] = field(default_factory=list)
    total_cost_ht: Decimal = Decimal("0")
    cost_per_portion: Decimal = Decimal("0")
    preparation_time_cost: Decimal = Decimal("0")
    total_cost_with_labor: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        """Calcule les totaux après initialisation."""
        self.total_cost_ht = sum(cost.total_cost_ht for cost in self.ingredient_costs)
        if self.portions > 0:
            self.cost_per_portion = self.total_cost_ht / self.portions
        self.total_cost_with_labor = self.total_cost_ht + self.preparation_time_cost


class RecipeCostCalculator:
    """
    Calculateur de coûts de recettes avec gestion des stocks FEFO.
    """

    def __init__(
        self,
        ingredients: dict[str, Ingredient],
        hourly_labor_cost: Decimal = Decimal("12.0"),
    ) -> None:
        """
        Initialise le calculateur.

        Args:
            ingredients: Dictionnaire des ingrédients par ID
            hourly_labor_cost: Coût horaire de la main d'œuvre
        """
        self.ingredients = ingredients
        self.base_hourly_labor_cost = hourly_labor_cost

    def get_hourly_labor_cost(
        self, restaurant_type: RestaurantType | None = None
    ) -> Decimal:
        """
        Calcule le coût horaire de main d'œuvre selon le type de restaurant.

        Args:
            restaurant_type: Type de restaurant (optionnel)

        Returns:
            Coût horaire ajusté
        """
        if restaurant_type is None:
            return self.base_hourly_labor_cost

        # Facteurs de coût par type de restaurant
        cost_factors = {
            RestaurantType.FAST: Decimal("0.85"),  # -15% (moins qualifié)
            RestaurantType.CLASSIC: Decimal("1.0"),  # Base
            RestaurantType.BRASSERIE: Decimal("1.1"),  # +10% (service plus élaboré)
            RestaurantType.GASTRONOMIQUE: Decimal("1.4"),  # +40% (chefs qualifiés)
        }

        factor = cost_factors.get(restaurant_type, Decimal("1.0"))
        return self.base_hourly_labor_cost * factor

    def calculate_recipe_cost(
        self, recipe: Recipe, stock_lots: list[StockLot] | None = None
    ) -> CostBreakdown:
        """
        Calcule le coût complet d'une recette.

        Args:
            recipe: Recette à calculer
            stock_lots: Lots de stock disponibles (optionnel)

        Returns:
            Décomposition complète des coûts

        Raises:
            ValueError: Si un ingrédient est manquant
        """
        ingredient_costs = []

        for item in recipe.items:
            if item.ingredient_id not in self.ingredients:
                raise ValueError(f"Ingrédient {item.ingredient_id} non trouvé")

            ingredient = self.ingredients[item.ingredient_id]

            # Calcul du coût avec gestion des pertes
            effective_quantity = item.qty_brute
            waste_percentage = item.perte_totale

            # Utilisation du stock si disponible, sinon prix catalogue
            unit_cost = self._get_ingredient_cost(
                ingredient, stock_lots, effective_quantity
            )
            total_cost = effective_quantity * unit_cost

            ingredient_cost = IngredientCost(
                ingredient_id=ingredient.id,
                ingredient_name=ingredient.name,
                quantity_used=effective_quantity,
                unit_cost_ht=unit_cost,
                total_cost_ht=total_cost,
                waste_percentage=waste_percentage * 100,  # Conversion en pourcentage
                supplier_id=self._get_best_supplier(ingredient, stock_lots),
            )

            ingredient_costs.append(ingredient_cost)

        # Calcul du coût de main d'œuvre
        labor_cost = self._calculate_labor_cost(recipe)

        return CostBreakdown(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            portions=recipe.portions,
            ingredient_costs=ingredient_costs,
            preparation_time_cost=labor_cost,
        )

    def _get_ingredient_cost(
        self,
        ingredient: Ingredient,
        stock_lots: list[StockLot] | None,
        quantity_needed: Decimal,
    ) -> Decimal:
        """
        Détermine le coût d'un ingrédient selon le stock disponible.

        Args:
            ingredient: Ingrédient concerné
            stock_lots: Lots de stock
            quantity_needed: Quantité nécessaire

        Returns:
            Coût unitaire HT
        """
        if not stock_lots:
            return ingredient.cost_ht

        # Recherche des lots de cet ingrédient (FEFO)
        available_lots = [
            lot
            for lot in stock_lots
            if lot.ingredient_id == ingredient.id and not lot.is_expired
        ]

        if not available_lots:
            return ingredient.cost_ht

        # Tri par DLC (FEFO)
        available_lots.sort(key=lambda x: x.dlc)

        # Calcul du coût moyen pondéré pour la quantité nécessaire
        total_cost = Decimal("0")
        remaining_quantity = quantity_needed

        for lot in available_lots:
            if remaining_quantity <= 0:
                break

            used_quantity = min(remaining_quantity, lot.quantity)
            total_cost += used_quantity * lot.unit_cost_ht
            remaining_quantity -= used_quantity

        if remaining_quantity > 0:
            # Complément au prix catalogue si stock insuffisant
            total_cost += remaining_quantity * ingredient.cost_ht

        return total_cost / quantity_needed

    def _get_best_supplier(
        self, ingredient: Ingredient, stock_lots: list[StockLot] | None
    ) -> str:
        """
        Détermine le meilleur fournisseur pour un ingrédient.

        Args:
            ingredient: Ingrédient concerné
            stock_lots: Lots de stock

        Returns:
            ID du fournisseur
        """
        if not stock_lots:
            return ""

        # Recherche du lot le moins cher disponible
        available_lots = [
            lot
            for lot in stock_lots
            if lot.ingredient_id == ingredient.id and not lot.is_expired
        ]

        if not available_lots:
            return ""

        best_lot = min(available_lots, key=lambda x: x.unit_cost_ht)
        return best_lot.supplier_id

    def _calculate_labor_cost(self, recipe: Recipe) -> Decimal:
        """
        Calcule le coût de main d'œuvre pour une recette.

        Args:
            recipe: Recette concernée

        Returns:
            Coût de main d'œuvre
        """
        total_time_hours = Decimal(recipe.temps_total_min) / 60
        return total_time_hours * self.get_hourly_labor_cost()

    def calculate_margin_analysis(
        self,
        recipe: Recipe,
        selling_price_ttc: Decimal,
        vat_rate: Decimal = Decimal("0.10"),
        stock_lots: list[StockLot] | None = None,
    ) -> dict[str, Decimal]:
        """
        Analyse de marge pour une recette.

        Args:
            recipe: Recette à analyser
            selling_price_ttc: Prix de vente TTC
            vat_rate: Taux de TVA
            stock_lots: Lots de stock

        Returns:
            Dict avec analyse de marge
        """
        cost_breakdown = self.calculate_recipe_cost(recipe, stock_lots)

        selling_price_ht = selling_price_ttc / (1 + vat_rate)
        cost_per_portion = cost_breakdown.total_cost_with_labor / recipe.portions

        margin_ht = selling_price_ht - cost_per_portion
        margin_percentage = (
            (margin_ht / selling_price_ht) if selling_price_ht > 0 else Decimal("0")
        )

        food_cost_percentage = (
            (cost_per_portion / selling_price_ht)
            if selling_price_ht > 0
            else Decimal("0")
        )

        return {
            "selling_price_ht": selling_price_ht,
            "cost_per_portion": cost_per_portion,
            "margin_ht": margin_ht,
            "margin_percentage": margin_percentage,
            "food_cost_percentage": food_cost_percentage,
            "labor_cost_per_portion": cost_breakdown.preparation_time_cost
            / recipe.portions,
        }

    def optimize_recipe_cost(
        self, recipe: Recipe, target_food_cost_percentage: Decimal = Decimal("30")
    ) -> dict[str, Decimal]:
        """
        Optimise le coût d'une recette pour atteindre un objectif de food cost.

        Args:
            recipe: Recette à optimiser
            target_food_cost_percentage: Objectif de food cost en %

        Returns:
            Suggestions d'optimisation
        """
        cost_breakdown = self.calculate_recipe_cost(recipe)

        # Analyse des ingrédients les plus coûteux
        sorted_costs = sorted(
            cost_breakdown.ingredient_costs, key=lambda x: x.total_cost_ht, reverse=True
        )

        optimization_suggestions = {}

        for i, ingredient_cost in enumerate(sorted_costs[:3]):  # Top 3 des plus coûteux
            percentage_of_total = (
                ingredient_cost.total_cost_ht / cost_breakdown.total_cost_ht * 100
            )

            optimization_suggestions[f"ingredient_{i + 1}"] = {
                "name": ingredient_cost.ingredient_name,
                "current_cost": ingredient_cost.total_cost_ht,
                "percentage_of_total": percentage_of_total,
                "reduction_potential": ingredient_cost.total_cost_ht
                * Decimal("0.1"),  # 10% de réduction potentielle
            }

        return optimization_suggestions
