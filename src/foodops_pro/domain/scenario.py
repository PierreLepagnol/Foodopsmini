"""
Modèles de scénarios pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal

from .restaurant import RestaurantType


@dataclass(frozen=True)
class MarketSegment:
    """
    Représente un segment de clientèle avec ses caractéristiques.

    Attributes:
        name: Nom du segment
        share: Part de marché (0.0-1.0)
        budget: Budget moyen par repas
        type_affinity: Affinité par type de restaurant
        price_sensitivity: Sensibilité au prix (0.0-2.0)
        quality_sensitivity: Sensibilité à la qualité (0.0-2.0)
        seasonality: Variations saisonnières par mois (1-12)
    """

    name: str
    share: Decimal
    budget: Decimal
    type_affinity: Dict[RestaurantType, Decimal]
    price_sensitivity: Decimal = Decimal("1.0")
    quality_sensitivity: Decimal = Decimal("1.0")
    seasonality: Dict[int, Decimal] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validation des données."""
        if not (0 <= self.share <= 1):
            raise ValueError(f"La part de marché doit être entre 0 et 1: {self.share}")
        if self.budget <= 0:
            raise ValueError(f"Le budget doit être positif: {self.budget}")
        if not (0 <= self.price_sensitivity <= 2):
            raise ValueError(
                f"La sensibilité prix doit être entre 0 et 2: {self.price_sensitivity}"
            )
        if not (0 <= self.quality_sensitivity <= 2):
            raise ValueError(
                f"La sensibilité qualité doit être entre 0 et 2: {self.quality_sensitivity}"
            )

        # Validation des affinités
        for restaurant_type, affinity in self.type_affinity.items():
            if affinity < 0:
                raise ValueError(f"L'affinité doit être positive: {affinity}")

        # Validation de la saisonnalité
        for month, factor in self.seasonality.items():
            if not (1 <= month <= 12):
                raise ValueError(f"Le mois doit être entre 1 et 12: {month}")
            if factor < 0:
                raise ValueError(f"Le facteur saisonnier doit être positif: {factor}")

    def get_seasonal_factor(self, month: int) -> Decimal:
        """
        Retourne le facteur saisonnier pour un mois donné.

        Args:
            month: Mois (1-12)

        Returns:
            Facteur saisonnier (1.0 = normal)
        """
        return self.seasonality.get(month, Decimal("1.0"))

    def get_type_affinity(self, restaurant_type: RestaurantType) -> Decimal:
        """
        Retourne l'affinité pour un type de restaurant.

        Args:
            restaurant_type: Type de restaurant

        Returns:
            Coefficient d'affinité
        """
        return self.type_affinity.get(restaurant_type, Decimal("1.0"))


@dataclass
class Scenario:
    """
    Représente un scénario de jeu complet avec tous ses paramètres.

    Attributes:
        name: Nom du scénario
        description: Description du scénario
        turns: Nombre de tours
        turn_scale: Unité de temps des tours ("month" = mois de 4 semaines)
        base_demand: Demande de base par tour
        demand_noise: Variabilité de la demande (0.0-1.0)
        segments: Segments de marché
        vat_rates: Taux de TVA par catégorie
        social_charges: Charges sociales par type de contrat
        interest_rate: Taux d'intérêt pour emprunts
        ai_competitors: Nombre de concurrents IA
        random_seed: Graine aléatoire pour reproductibilité
    """

    name: str
    description: str
    turns: int
    base_demand: int
    demand_noise: Decimal
    segments: List[MarketSegment]
    turn_scale: str = "month"
    vat_rates: Dict[str, Decimal] = field(default_factory=dict)
    social_charges: Dict[str, Decimal] = field(default_factory=dict)
    interest_rate: Decimal = Decimal("0.05")
    ai_competitors: int = 2
    random_seed: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.turns <= 0:
            raise ValueError(f"Le nombre de tours doit être positif: {self.turns}")
        if self.base_demand <= 0:
            raise ValueError(
                f"La demande de base doit être positive: {self.base_demand}"
            )
        if not (0 <= self.demand_noise <= 1):
            raise ValueError(
                f"Le bruit de demande doit être entre 0 et 1: {self.demand_noise}"
            )
        if not self.segments:
            raise ValueError("Le scénario doit avoir au moins un segment")
        if self.ai_competitors < 0:
            raise ValueError(
                f"Le nombre de concurrents IA doit être positif: {self.ai_competitors}"
            )

        # Validation que les parts de marché totalisent ~1.0
        total_share = sum(segment.share for segment in self.segments)
        if not (0.95 <= total_share <= 1.05):
            raise ValueError(
                f"Les parts de marché doivent totaliser ~1.0: {total_share}"
            )

        # Validation des taux de TVA
        for category, rate in self.vat_rates.items():
            if not (0 <= rate <= 1):
                raise ValueError(f"Le taux de TVA doit être entre 0 et 1: {rate}")

        # Validation des charges sociales
        for contract_type, rate in self.social_charges.items():
            if not (0 <= rate <= 1):
                raise ValueError(
                    f"Les charges sociales doivent être entre 0 et 1: {rate}"
                )

    def get_vat_rate(self, category: str) -> Decimal:
        """
        Retourne le taux de TVA pour une catégorie.

        Args:
            category: Catégorie (food_onsite, food_takeaway, alcohol, etc.)

        Returns:
            Taux de TVA
        """
        return self.vat_rates.get(category, Decimal("0.10"))  # 10% par défaut

    def get_social_charges_rate(self, contract_type: str) -> Decimal:
        """
        Retourne le taux de charges sociales pour un type de contrat.

        Args:
            contract_type: Type de contrat

        Returns:
            Taux de charges sociales
        """
        return self.social_charges.get(contract_type, Decimal("0.42"))  # 42% par défaut

    def get_segment_by_name(self, name: str) -> Optional[MarketSegment]:
        """
        Retourne un segment par son nom.

        Args:
            name: Nom du segment

        Returns:
            Segment trouvé ou None
        """
        for segment in self.segments:
            if segment.name == name:
                return segment
        return None

    def calculate_total_demand(self, turn: int, month: int = 1) -> int:
        """
        Calcule la demande totale pour un tour donné.

        Args:
            turn: Numéro du tour (1 tour = 1 mois standard de 4 semaines)
            month: Mois de l'année (pour saisonnalité)

        Returns:
            Demande totale ajustée
        """
        # Facteur saisonnier moyen
        seasonal_factor = Decimal("0")
        for segment in self.segments:
            segment_seasonal = segment.get_seasonal_factor(month)
            seasonal_factor += segment_seasonal * segment.share

        # Demande ajustée
        adjusted_demand = self.base_demand * seasonal_factor
        return int(adjusted_demand)

    def __str__(self) -> str:
        return f"{self.name} ({self.turns} tours, {len(self.segments)} segments)"
