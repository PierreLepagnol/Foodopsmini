"""
Modèles de scénarios
"""

from dataclasses import field
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from game_engine.domain.types import RestaurantType


class MarketSegment(BaseModel):
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
    share: Decimal = Field(ge=0, le=1, description="Part de marché entre 0 et 1")
    budget: Decimal = Field(
        gt=0, description="Budget moyen par repas, doit être positif"
    )
    type_affinity: dict[RestaurantType, Decimal] = Field(
        description="Affinité par type de restaurant"
    )
    price_sensitivity: Decimal = Field(
        Decimal("1.0"), ge=0, le=2, description="Sensibilité au prix entre 0 et 2"
    )
    quality_sensitivity: Decimal = Field(
        Decimal("1.0"), ge=0, le=2, description="Sensibilité à la qualité entre 0 et 2"
    )
    seasonality: dict[int, Decimal] = field(default_factory=dict)

    @field_validator("type_affinity")
    @classmethod
    def validate_type_affinity(
        cls, v: dict[RestaurantType, Decimal]
    ) -> dict[RestaurantType, Decimal]:
        """Valide que toutes les affinités sont positives."""
        for _, affinity in v.items():
            if affinity < 0:
                raise ValueError(f"L'affinité doit être positive: {affinity}")
        return v

    @field_validator("seasonality")
    @classmethod
    def validate_seasonality(cls, v: dict[int, Decimal]) -> dict[int, Decimal]:
        """Valide les données de saisonnalité."""
        for month, factor in v.items():
            if not (1 <= month <= 12):
                raise ValueError(f"Le mois doit être entre 1 et 12: {month}")
            if factor < 0:
                raise ValueError(f"Le facteur saisonnier doit être positif: {factor}")
        return v

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


class Scenario(BaseModel):
    """
    Représente un scénario de jeu complet avec tous ses paramètres.

    Attributes:
        name: Nom du scénario
        description: Description du scénario
        turns: Nombre de tours
        base_demand: Demande de base par tour
        demand_noise: Variabilité de la demande (0.0-1.0)
        segments: Segments de marché
        vat_rates: Taux de TVA par catégorie
        social_charges: Charges sociales par type de contrat
        interest_rate: Taux d'intérêt pour emprunts
        ai_competitors: Nombre de concurrents IA
        random_seed: Graine aléatoire pour reproductibilité
    """

    name: str = Field(description="Nom du scénario")
    description: str = Field(description="Description du scénario")
    turns: int = Field(gt=0, description="Nombre de tours")
    base_demand: int = Field(gt=0, description="Demande de base par tour")
    demand_noise: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("1"),
        description="Variabilité de la demande (0.0-1.0)",
    )
    segments: list[MarketSegment] = Field(
        min_length=1, description="Segments de marché"
    )
    vat_rates: dict[str, Decimal] = Field(default_factory=dict)
    social_charges: dict[str, Decimal] = Field(default_factory=dict)
    interest_rate: Decimal = Field(default=Decimal("0.05"))
    ai_competitors: int = Field(ge=0, default=2)
    random_seed: int | None = Field(
        default=None, description="Graine aléatoire pour reproductibilité"
    )

    @field_validator("segments")
    @classmethod
    def validate_segments_shares(cls, v: list[MarketSegment]) -> list[MarketSegment]:
        """Valide que les parts de marché totalisent ~1.0."""
        total_share = sum(segment.share for segment in v)
        if not (Decimal("0.95") <= total_share <= Decimal("1.05")):
            raise ValueError(
                f"Les parts de marché doivent totaliser ~1.0: {total_share}"
            )
        return v

    @field_validator("vat_rates")
    @classmethod
    def validate_vat_rates(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        """Valide que les taux de TVA sont entre 0 et 1."""
        for category, rate in v.items():
            if not (Decimal("0") <= rate <= Decimal("1")):
                raise ValueError(f"Le taux de TVA doit être entre 0 et 1: {rate}")
        return v

    @field_validator("social_charges")
    @classmethod
    def validate_social_charges(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        """Valide que les charges sociales sont entre 0 et 1."""
        for contract_type, rate in v.items():
            if not (Decimal("0") <= rate <= Decimal("1")):
                raise ValueError(
                    f"Les charges sociales doivent être entre 0 et 1: {rate}"
                )
        return v

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

    def get_segment_by_name(self, name: str) -> MarketSegment | None:
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

    def __str__(self) -> str:
        return f"{self.name} ({self.turns} tours, {len(self.segments)} segments)"
