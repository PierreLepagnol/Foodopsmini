"""
Système de fonds de commerce pour FoodOps Pro.
"""

import json
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path

from game_engine.domain.types import RestaurantType
from game_engine.console_ui import print_box

directory = Path("/home/lepagnol/Documents/Perso/Games/Foodopsmini/data/")
PATH_FONDS_DE_COMMERCE = directory / "fond_de_commerces.json"


class LocationType(Enum):
    """Types d'emplacements."""

    CENTRE_VILLE = "centre_ville"
    BANLIEUE = "banlieue"
    ZONE_COMMERCIALE = "zone_commerciale"
    QUARTIER_ETUDIANT = "quartier_etudiant"
    ZONE_INDUSTRIELLE = "zone_industrielle"


class CommerceCondition(Enum):
    """État du fonds de commerce."""

    EXCELLENT = "excellent"
    BON = "bon"
    CORRECT = "correct"
    RENOVATION_LEGERE = "renovation_legere"
    RENOVATION_LOURDE = "renovation_lourde"


@dataclass
class CommerceLocation:
    """
    Fonds de commerce disponible à l'achat.

    Attributes:
        id: Identifiant unique
        name: Nom du commerce
        location_type: Type d'emplacement
        restaurant_type: Type de restaurant recommandé
        price: Prix d'achat du fonds
        size: Nombre de couverts
        condition: État du local
        equipment_included: Équipements inclus
        rent_monthly: Loyer mensuel
        lease_years: Durée du bail restante
        foot_traffic: Niveau de passage
        competition_nearby: Nombre de concurrents proches
        description: Description détaillée
        advantages: Avantages spécifiques
        disadvantages: Inconvénients
        renovation_cost: Coût de rénovation si nécessaire
        special_features: Caractéristiques spéciales
    """

    id: str
    name: str
    location_type: LocationType
    restaurant_type: RestaurantType
    price: Decimal
    size: int  # couverts
    condition: CommerceCondition
    equipment_included: list[str]
    rent_monthly: Decimal
    lease_years: int
    foot_traffic: str  # "low", "medium", "high", "very_high"
    competition_nearby: int
    description: str
    advantages: list[str]
    disadvantages: list[str]
    renovation_cost: Decimal = Decimal("0")
    special_features: list[str] = None

    def __post_init__(self):
        if self.special_features is None:
            self.special_features = []

    @property
    def total_initial_cost(self) -> Decimal:
        """Coût total initial (achat + rénovation)."""
        return self.price + self.renovation_cost

    @property
    def foot_traffic_multiplier(self) -> Decimal:
        """Multiplicateur de clientèle selon le passage."""
        multipliers = {
            "low": Decimal("0.7"),
            "medium": Decimal("1.0"),
            "high": Decimal("1.3"),
            "very_high": Decimal("1.6"),
        }
        return multipliers.get(self.foot_traffic, Decimal("1.0"))

    @property
    def competition_pressure(self) -> Decimal:
        """Pression concurrentielle (0.0 = aucune, 1.0 = très forte)."""
        if self.competition_nearby == 0:
            return Decimal("0.0")
        elif self.competition_nearby <= 2:
            return Decimal("0.3")
        elif self.competition_nearby <= 4:
            return Decimal("0.6")
        else:
            return Decimal("0.9")

    def display_commerce_details(self, index: int):
        """Affiche les détails d'un commerce."""
        details = [
            f"{index}. {self.name.upper()}",
            f"📍 {self.location_type.value.replace('_', ' ').title()}",
            f"💰 Prix: {self.price:.0f}€ + {self.renovation_cost:.0f}€ rénovation",
            f"🏠 {self.size} couverts - État: {self.condition.value}",
            f"📈 Passage: {self.foot_traffic} - Concurrence: {self.competition_nearby}",
            f"🏢 Loyer: {self.rent_monthly:.0f}€/mois - Bail: {self.lease_years} ans",
            f"✅ Avantages: {', '.join(self.advantages[:2])}",
            f"⚠️ Inconvénients: {', '.join(self.disadvantages[:2])}",
        ]
        print_box(details, style="info")

    def display_confirm_commerce_purchase(self, budget: Decimal) -> None:
        """Confirmation d'achat d'un commerce."""
        remaining_budget = budget - self.total_initial_cost

        confirmation_details = [
            "CONFIRMATION D'ACHAT",
            f"Commerce: {self.name}",
            f"Prix d'achat: {self.price:.0f}€",
            f"Rénovation: {self.renovation_cost:.0f}€",
            f"TOTAL: {self.total_initial_cost:.0f}€",
            f"Budget initial: {budget:.0f}€",
            f"Budget restant: {remaining_budget:.0f}€",
            f"Loyer mensuel: {self.rent_monthly:.0f}€",
            f"Autonomie: {remaining_budget / self.rent_monthly:.1f} mois",
        ]

        if remaining_budget < self.rent_monthly * 3:
            confirmation_details.append("")
            confirmation_details.append("⚠️ ATTENTION: Budget restant faible !")
            style = "warning"
        else:
            style = "info"

        print_box(confirmation_details, style=style)


class CommerceManager:
    """Gestionnaire des fonds de commerce."""

    def __init__(self):
        self.available_locations = self._load_locations()

    def _load_locations(self) -> list[CommerceLocation]:
        """Crée la liste des fonds de commerce par défaut."""
        with open(PATH_FONDS_DE_COMMERCE) as file:
            return [CommerceLocation(**location) for location in json.load(file)]

    def get_available_locations(
        self,
        budget: Decimal,
        location_types: list[LocationType] | None = None,
        restaurant_types: list[RestaurantType] | None = None,
    ) -> list[CommerceLocation]:
        """
        Retourne les emplacements disponibles selon les critères.

        Args:
            budget: Budget disponible
            location_types: Types d'emplacements autorisés
            restaurant_types: Types de restaurants autorisés

        Returns:
            Liste des emplacements accessibles
        """

        def _matches_criteria(location: CommerceLocation) -> bool:
            """Vérifie si un emplacement correspond aux critères."""
            if location.total_initial_cost > budget:
                return False
            if location_types and location.location_type not in location_types:
                return False
            if restaurant_types and location.restaurant_type not in restaurant_types:
                return False
            return True

        return [
            location
            for location in self.available_locations
            if _matches_criteria(location)
        ]

    def get_location_by_id(self, location_id: str) -> CommerceLocation | None:
        """Retourne un emplacement par son ID."""
        for location in self.available_locations:
            if location.id == location_id:
                return location
        return None
