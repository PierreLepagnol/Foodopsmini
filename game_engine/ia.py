from decimal import Decimal

from creation_scenario import AdminSettings
from game_engine.domain.commerce import CommerceManager
from game_engine.domain.restaurant import (
    Restaurant,
    RestaurantType,
    create_restaurant_from_commerce,
)


def create_ai_competitors(nombre_ai_concurrents: int) -> None:
    """Crée les concurrents IA."""

    commerce_manager = CommerceManager()
    for i in range(nombre_ai_concurrents):
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
        available_locations = commerce_manager.get_available_locations(
            Decimal("50000")  # Budget standard pour l'IA
        )

        if available_locations:
            location = available_locations[0]  # Premier disponible
            ai_restaurant = create_restaurant_from_commerce(
                location, Decimal("50000"), f"ai_{i + 1}"
            )
            ai_restaurant.name = name
            ai_restaurant.id = f"ai_{i + 1}"


# def _create_ai_competitors(self) -> None:
#     """Crée les concurrents IA."""
#     for i in range(self.admin_settings.ai_count):
#         ai_configs = [
#             ("Chez Mario", RestaurantType.CLASSIC),
#             ("Quick Burger", RestaurantType.FAST),
#             ("Le Gourmet", RestaurantType.GASTRONOMIQUE),
#             ("Brasserie du Port", RestaurantType.BRASSERIE),
#         ]

#         if i < len(ai_configs):
#             name, rest_type = ai_configs[i]
#         else:
#             name, _rest_type = f"Concurrent {i + 1}", RestaurantType.CLASSIC

#         # Sélection d'un commerce pour l'IA
#         available_locations = self.commerce_manager.get_available_locations(
#             Decimal("50000")  # Budget standard pour l'IA
#         )

#         if available_locations:
#             location = available_locations[0]  # Premier disponible
#             ai_restaurant = self._create_restaurant_from_commerce(
#                 location, Decimal("50000"), f"ai_{i + 1}"
#             )
#             ai_restaurant.name = name
#             ai_restaurant.id = f"ai_{i + 1}"
#             self.ai_competitors.append(ai_restaurant)


def ai_decisions(
    ai_competitors: list[Restaurant], admin_settings: AdminSettings
) -> None:
    """Décisions simplifiées de l'IA."""
    for ai in ai_competitors:
        # Stratégie simple selon la difficulté
        if admin_settings.ai_difficulty == "easy":
            ai.staffing_level = 2  # Niveau fixe
        elif admin_settings.ai_difficulty == "medium":
            # Ajustement selon la performance
            if hasattr(ai, "_last_utilization"):
                if ai._last_utilization > 0.8:
                    ai.staffing_level = min(3, ai.staffing_level + 1)
                elif ai._last_utilization < 0.5:
                    ai.staffing_level = max(1, ai.staffing_level - 1)
        # Mode "hard" : IA plus agressive (à implémenter)
