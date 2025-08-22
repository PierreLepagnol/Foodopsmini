"""Module de production (MVP): planifie les unités prêtes à servir."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from ..domain.recipe import Recipe
from ..domain.schedule import SpecialDay, WeeklySchedule


@dataclass
class ProductionPlan:
    servings_by_recipe: dict[str, int]
    cost_by_recipe_ht: dict[str, Decimal] | None = None
    consumed_by_recipe: dict[str, dict[str, Decimal]] | None = None
    special_day: SpecialDay | None = None


class ProductionPlanner:
    """Planificateur de production très simple (phase 1)."""

    def compute_ingredient_need_for_servings(
        self, recipe: Recipe, servings: int, size: str = "S"
    ) -> dict[str, Decimal]:
        """Calcule les besoins ingrédients pour un nombre de portions (taille S/L).

        Convention: S = 0.5x ingrédients, L = 1.0x (portion standard).
        """
        factor = Decimal("0.5") if size == "S" else Decimal("1.0")
        needs: dict[str, Decimal] = {}
        for item in recipe.items:
            needs[item.ingredient_id] = item.qty_brute * Decimal(servings) * factor
        return needs

    def compute_max_servings_from_stock(
        self, recipe: Recipe, stock_manager: Any
    ) -> int:
        """Calcule le nombre maximum de portions réalisables selon le stock disponible."""
        # Si pas de stock manager, pas de contrainte
        if stock_manager is None:
            return 999999
        # Par ingrédient: available / qty_brute
        max_servings = None
        for item in recipe.items:
            needed_per_serving = item.qty_brute
            if needed_per_serving <= 0:
                continue
            available = stock_manager.get_available_quantity(item.ingredient_id)
            if available <= 0:
                return 0
            possible = int(
                (available / needed_per_serving).to_integral_value(
                    rounding="ROUND_FLOOR"
                )
            )
            max_servings = (
                possible if max_servings is None else min(max_servings, possible)
            )
        return max_servings or 0

    def plan(
        self,
        restaurant: Any,
        recipes_by_id: dict[str, Recipe],
        schedule: WeeklySchedule | None = None,
        current_day: date | None = None,
    ) -> ProductionPlan:
        """Crée un plan par recette active, borné par stock et capacité.

        Si une ``WeeklySchedule`` est fournie avec ``current_day``, la capacité
        et les besoins sont ajustés selon l'impact attendu de cette journée.
        """
        active = [
            rid
            for rid in getattr(restaurant, "active_recipes", [])
            if rid in recipes_by_id
        ]
        if not active:
            return ProductionPlan(servings_by_recipe={})

        capacity = max(0, int(getattr(restaurant, "capacity_current", 0)))
        stock_manager = getattr(restaurant, "stock_manager", None)

        special_day = None
        if schedule is not None and current_day is not None:
            special_day = schedule.get_special_day(current_day)
            if special_day is not None:
                impact = special_day.expected_impact
                capacity = int(Decimal(capacity) * impact)

        # Cap max réalisable par stock pour chaque recette
        max_by_recipe: dict[str, int] = {}
        total_max = 0
        for rid in active:
            smax = self.compute_max_servings_from_stock(
                recipes_by_id[rid], stock_manager
            )
            max_by_recipe[rid] = smax
            total_max += smax

        if total_max == 0 or capacity == 0:
            return ProductionPlan(
                servings_by_recipe=dict.fromkeys(active, 0),
                special_day=special_day,
            )

        # Répartition simple de la capacité proportionnellement au max réalisable
        plan: dict[str, int] = {}
        remaining_capacity = capacity
        for rid in sorted(active):
            share = (max_by_recipe[rid] / total_max) if total_max > 0 else 0
            target = min(max_by_recipe[rid], int(share * capacity))
            plan[rid] = target
            remaining_capacity -= target
        # Distribuer le reliquat en round-robin
        if remaining_capacity > 0:
            for rid in sorted(active):
                if remaining_capacity <= 0:
                    break
                if plan[rid] < max_by_recipe[rid]:
                    plan[rid] += 1
                    remaining_capacity -= 1

        # Consommer les ingrédients selon le plan (FEFO géré côté StockManager)
        consumed_by_recipe: dict[str, dict[str, Decimal]] = {}
        cost_by_recipe: dict[str, Decimal] = {}

        if stock_manager is not None:
            for rid, servings in plan.items():
                if servings <= 0:
                    continue
                recipe = recipes_by_id[rid]
                consumed: dict[str, Decimal] = {}
                for item in recipe.items:
                    total_qty = item.qty_brute * Decimal(servings)
                    stock_manager.consume_ingredient(item.ingredient_id, total_qty)
                    consumed[item.ingredient_id] = total_qty
                    # estimation coût de revient HT: moyenne pondérée des lots n'est pas
                    # dispo ici, on approxime par coût unitaire moyen du dernier lot
                    # Pour MVP, on ne remonte pas le coût exact; on laissera l'exécution
                    # manuelle calculer plus tard.
                consumed_by_recipe[rid] = consumed
                # coût par portion: calculé plus tard si besoin
                cost_by_recipe[rid] = Decimal("0")

        return ProductionPlan(
            servings_by_recipe=plan,
            cost_by_recipe_ht=cost_by_recipe,
            consumed_by_recipe=consumed_by_recipe,
            special_day=special_day,
        )


def apply_production_plan(restaurant: Any, plan: ProductionPlan) -> None:
    """Stocke les unités prêtes à servir dans le restaurant pour le tour."""
    restaurant.production_units_ready = dict(plan.servings_by_recipe)


def clear_previous_production(restaurant: Any) -> None:
    """Purge les unités prêtes du tour précédent (DLC=1 tour)."""
    restaurant.production_units_ready = {}
    restaurant.production_quality_score = {}


def execute_manual_production_plan(
    restaurant: Any, recipes_by_id: dict[str, Recipe]
) -> None:
    """Exécute le brouillon de production saisi par le joueur: consomme ingrédients et crée des unités prêtes.

    draft entry format: {recipe_id: {"qty": int, "size": "S"|"L", "quality": Decimal}}
    """
    draft = getattr(restaurant, "production_plan_draft", {}) or {}
    if not draft:
        return
    stock_manager = getattr(restaurant, "stock_manager", None)
    if stock_manager is None:
        return

    # Préparer une carte unités prêtes
    units_ready = dict(getattr(restaurant, "production_units_ready", {}) or {})
    quality_scores = dict(getattr(restaurant, "production_quality_score", {}) or {})
    consumed_ings: dict[str, dict[str, Decimal]] = {}
    cost_per_portion: dict[str, Decimal] = {}
    produced_units: dict[str, int] = {}

    for recipe_id, params in draft.items():
        if recipe_id not in recipes_by_id:
            continue
        recipe = recipes_by_id[recipe_id]
        qty = int(params.get("qty", 0))
        size = params.get("size", "S")
        quality = Decimal(str(params.get("quality", "1.0")))
        if qty <= 0:
            continue
        # Calculer besoins
        needs = ProductionPlanner().compute_ingredient_need_for_servings(
            recipe, qty, size
        )
        # Vérifier disponibilité et consommer
        # Si pas assez d'un ingrédient: on réduit la quantité à ce qui est faisable
        max_servings = None
        for ing_id, need in needs.items():
            if need <= 0:
                continue
            per_serving = need / Decimal(qty)
            available = stock_manager.get_available_quantity(
                ing_id, exclude_expired=True
            )
            possible = (
                int((available / per_serving).to_integral_value(rounding="ROUND_FLOOR"))
                if per_serving > 0
                else qty
            )
            max_servings = (
                possible if max_servings is None else min(max_servings, possible)
            )
        if not max_servings or max_servings <= 0:
            continue
        # Consommer ingrédients pour max_servings
        final_needs = ProductionPlanner().compute_ingredient_need_for_servings(
            recipe, max_servings, size
        )
        total_cost_ht = Decimal("0")
        consumed_map: dict[str, Decimal] = {}
        for ing_id, qty_need in final_needs.items():
            if qty_need > 0:
                lots_used = stock_manager.consume_ingredient(ing_id, qty_need)
                consumed_map[ing_id] = qty_need
                # Coût exact: somme lots consommés
                for lot in lots_used:
                    total_cost_ht += lot.total_value_ht
        # Créer unités prêtes
        units_ready[recipe_id] = units_ready.get(recipe_id, 0) + max_servings
        quality_scores[recipe_id] = quality
        consumed_ings[recipe_id] = consumed_map
        produced_units[recipe_id] = produced_units.get(recipe_id, 0) + max_servings
        if max_servings > 0:
            cost_per_portion[recipe_id] = (
                total_cost_ht / Decimal(max_servings)
            ).quantize(Decimal("0.01"))

    restaurant.production_units_ready = units_ready
    restaurant.production_quality_score = quality_scores
    restaurant.production_consumed_ingredients = consumed_ings
    restaurant.production_produced_units = produced_units
    restaurant.production_cost_per_portion = cost_per_portion
    # On laisse le draft en place pour édition tour suivant; on pourrait aussi le vider.
