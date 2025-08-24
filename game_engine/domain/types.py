"""
Types communs pour FoodOps Pro.
"""

from decimal import Decimal
from enum import Enum


class RestaurantType(Enum):
    """Types de restaurants avec leurs caractéristiques."""

    FAST = "fast"
    CLASSIC = "classic"
    BRASSERIE = "brasserie"
    GASTRONOMIQUE = "gastronomique"

    @property
    def display_name(self) -> str:
        """Nom d'affichage du type de restaurant."""
        names = {
            self.FAST: "Fast Food",
            self.CLASSIC: "Restaurant Classique",
            self.BRASSERIE: "Brasserie",
            self.GASTRONOMIQUE: "Restaurant Gastronomique",
        }
        return names[self]

    @property
    def labor_cost_multiplier(self) -> float:
        """Multiplicateur de coût de main-d'œuvre selon le type."""
        multipliers = {
            self.FAST: 0.85,  # -15%
            self.CLASSIC: 1.0,  # base
            self.BRASSERIE: 1.10,  # +10%
            self.GASTRONOMIQUE: 1.40,  # +40%
        }
        return multipliers[self]

    @staticmethod
    def get_service_speed(restaurant_type: "RestaurantType") -> Decimal:
        """Retourne la vitesse de service selon le type."""
        speeds = {
            RestaurantType.FAST: Decimal("1.4"),
            RestaurantType.CLASSIC: Decimal("1.0"),
            RestaurantType.GASTRONOMIQUE: Decimal("0.7"),
            RestaurantType.BRASSERIE: Decimal("1.1"),
        }
        return speeds.get(restaurant_type, Decimal("1.0"))
