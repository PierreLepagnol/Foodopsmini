"""
Modèles du domaine métier pour FoodOps Pro.

Ce module contient toutes les classes représentant les entités
métier du jeu de gestion de restaurant.
"""

from .ingredient import Ingredient
from .recipe import Recipe, RecipeItem
from .supplier import Supplier
from .stock import StockLot
from .restaurant import Restaurant, RestaurantType
from .employee import Employee, EmployeeContract, EmployeePosition
from .scenario import Scenario, MarketSegment
from .campaign import CampaignManager

__all__ = [
    "Ingredient",
    "Recipe",
    "RecipeItem",
    "Supplier",
    "StockLot",
    "Restaurant",
    "RestaurantType",
    "Employee",
    "EmployeeContract",
    "EmployeePosition",
    "Scenario",
    "MarketSegment",
    "CampaignManager",
]
