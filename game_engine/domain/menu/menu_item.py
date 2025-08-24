"""Modèles des articles de menu vendables"""

from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from game_engine.domain.menu.types import MenuCategory, PricingStrategy
from game_engine.domain.menu.recipe import Recipe
from game_engine.domain.types import RestaurantType


class PlatStatus(Enum):
    """
    Énumération des statuts possibles pour un article de menu.

    Définit tous les états possibles d'un article dans le cycle de vie
    du menu, de sa création à sa suppression.

    Values:
        AVAILABLE: Article disponible à la commande
        UNAVAILABLE: Temporairement indisponible (rupture stock)
        SEASONAL: Disponible selon la saison
        DISCONTINUED: Définitivement arrêté
        COMING_SOON: Annoncé mais pas encore disponible
    """

    AVAILABLE = "available"  # Disponible
    UNAVAILABLE = "unavailable"  # Indisponible (rupture de stock)
    SEASONAL = "seasonal"  # Saisonnier
    DISCONTINUED = "discontinued"  # Arrêté
    COMING_SOON = "coming_soon"  # Bientôt disponible


class Plat(BaseModel):
    """
    Article de menu vendable avec tarification et positionnement.

    Attributes:
        id: Identifiant unique de l'article
        name: Nom commercial de l'article
        description: Description pour les clients
        recipe: Recette associée
        category: Catégorie de menu
        price_ttc: Prix de vente TTC
        vat_rate: Taux de TVA applicable
        status: Statut de disponibilité
        pricing_strategy: Stratégie de tarification
        target_margin_percentage: Marge cible en pourcentage
        position_in_menu: Position dans le menu (pour l'affichage)
        is_signature: Article signature du restaurant
        allergens: Liste des allergènes
        dietary_info: Informations diététiques (végétarien, etc.)
    """

    id: str = Field(description="Identifiant unique de l'article")
    name: str = Field(description="Nom commercial de l'article")
    description: str = Field(default="", description="Description pour les clients")
    recipe: Recipe = Field(description="Recette associée")
    category: MenuCategory = Field(description="Catégorie de menu")
    price_ttc: Decimal = Field(gt=0, description="Prix de vente TTC")
    vat_rate: Decimal = Field(default=Decimal("0.10"), description="Taux de TVA")
    status: PlatStatus = Field(
        default=PlatStatus.AVAILABLE, description="Disponibilité"
    )
    pricing_strategy: PricingStrategy = Field(
        default=PricingStrategy.COST_PLUS, description="Stratégie de tarification"
    )
    target_margin_percentage: Decimal = Field(
        default=Decimal("70"), ge=0, le=100, description="Marge cible en pourcentage"
    )
    position_in_menu: int = Field(
        default=0, ge=0, description="Position dans le menu (pour l'affichage)"
    )
    is_signature: bool = Field(
        default=False, description="Article signature du restaurant"
    )
    allergens: list[str] = Field(
        default_factory=list, description="Liste des allergènes"
    )
    dietary_info: list[str] = Field(
        default_factory=list, description="Informations diététiques (végétarien, etc.)"
    )

    @property
    def price_ht(self) -> Decimal:
        """Prix hors taxes."""
        return self.price_ttc / (1 + self.vat_rate)

    @property
    def display_name(self) -> str:
        """Nom d'affichage avec indicateurs."""
        name = self.name
        if self.is_signature:
            name = f"⭐ {name}"
        if self.status == PlatStatus.SEASONAL:
            name = f"{name} 🍂"
        return name

    @property
    def is_available(self) -> bool:
        """Vérifie si l'article est disponible à la vente."""
        return self.status in [PlatStatus.AVAILABLE, PlatStatus.SEASONAL]

    @property
    def margin_ht(self) -> Decimal:
        """
        Marge brute hors taxes par unité vendue.
        """

        return self.price_ht - self.recipe.cost_per_portion

    def calculate_food_cost_percentage(
        self, recipe_cost_per_portion: Decimal
    ) -> Decimal:
        """
        Calcule le ratio food cost, indicateur clé de rentabilité.

        Le food cost exprime le coût des matières premières en pourcentage
        du prix de vente HT. C'est un KPI fondamental en restauration.

        Args:
            recipe_cost_per_portion: Coût des ingrédients par portion

        Returns:
            Pourcentage du food cost (0-100%)
            Retourne 100% si le prix HT est nul ou négatif

        Example:
            Si coût = 3€ et prix HT = 10€
            Retourne 30% (food cost acceptable)
        """
        if self.price_ht <= 0:
            return Decimal("100")
        return (recipe_cost_per_portion / self.price_ht) * 100

    def suggest_price_for_target_margin(
        self,
        recipe_cost_per_portion: Decimal,
        target_food_cost_percentage: Decimal = Decimal("30"),
    ) -> Decimal:
        """
        Calcule le prix de vente optimal pour un objectif de food cost.

        Applique la formule inverse du food cost pour déterminer le prix
        qui permettra d'atteindre l'objectif de rentabilité souhaité.

        Args:
            recipe_cost_per_portion: Coût des ingrédients par portion
            target_food_cost_percentage: Objectif de food cost (défaut: 30%)

        Returns:
            Prix TTC suggéré pour atteindre l'objectif

        Raises:
            ValueError: Si le pourcentage cible est négatif ou nul

        Example:
            Coût = 3€, objectif = 30%
            Prix HT = 3€ / 0.30 = 10€
            Prix TTC = 10€ * 1.10 = 11€
        """
        if target_food_cost_percentage <= 0:
            raise ValueError("Le pourcentage de food cost cible doit être positif")

        suggested_price_ht = recipe_cost_per_portion / (
            target_food_cost_percentage / 100
        )
        return suggested_price_ht * (1 + self.vat_rate)

    def get_competitive_price_range(
        self, market_low: Decimal, market_high: Decimal
    ) -> tuple[Decimal, Decimal]:
        """
        Calcule la fourchette de prix compétitive.

        Args:
            market_low: Prix le plus bas du marché
            market_high: Prix le plus haut du marché

        Returns:
            Tuple (prix_min, prix_max) pour rester compétitif
        """
        # Stratégie selon le positionnement
        if self.pricing_strategy == PricingStrategy.PENETRATION:
            return market_low * Decimal("0.9"), market_low * Decimal("1.1")
        elif self.pricing_strategy == PricingStrategy.PREMIUM:
            return market_high * Decimal("0.9"), market_high * Decimal("1.2")
        else:  # COMPETITIVE ou VALUE
            market_mid = (market_low + market_high) / 2
            return market_mid * Decimal("0.9"), market_mid * Decimal("1.1")

    def adapt_to_restaurant_type(self, restaurant_type: RestaurantType) -> None:
        """
        Adapte l'article selon le type de restaurant.

        Args:
            restaurant_type: Type de restaurant
        """
        # Ajustements selon le type de restaurant
        if restaurant_type == RestaurantType.FAST:
            self.pricing_strategy = PricingStrategy.VALUE
            self.target_margin_percentage = Decimal("60")
        elif restaurant_type == RestaurantType.GASTRONOMIQUE:
            self.pricing_strategy = PricingStrategy.PREMIUM
            self.target_margin_percentage = Decimal("80")
        elif restaurant_type == RestaurantType.BRASSERIE:
            self.pricing_strategy = PricingStrategy.COMPETITIVE
            self.target_margin_percentage = Decimal("70")
        else:  # CLASSIC
            self.pricing_strategy = PricingStrategy.COST_PLUS
            self.target_margin_percentage = Decimal("70")

    def __str__(self) -> str:
        return f"{self.display_name} - {self.price_ttc:.2f}€ ({self.category.value})"
