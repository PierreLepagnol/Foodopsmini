"""Modèles des articles de menu vendables"""

from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from game_engine.domain.menu.recipe import Recipe
from game_engine.domain.types import RestaurantType


class MenuItemStatus(Enum):
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


class MenuCategory(Enum):
    """Catégories d'articles de menu."""

    APPETIZER = "entree"
    MAIN_COURSE = "plat"
    DESSERT = "dessert"
    BEVERAGE = "boisson"
    SIDE = "accompagnement"
    SPECIAL = "special"


class PricingStrategy(Enum):
    """Stratégies de tarification."""

    COST_PLUS = "cost_plus"  # Coût + marge fixe
    COMPETITIVE = "competitive"  # Aligné sur la concurrence
    PREMIUM = "premium"  # Prix premium
    PENETRATION = "penetration"  # Prix d'appel
    VALUE = "value"  # Rapport qualité-prix


class MenuItem(BaseModel):
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

    id: str
    name: str
    description: str = ""
    recipe: Recipe
    category: MenuCategory
    price_ttc: Decimal = Field(gt=0, description="Le prix doit être positif")
    vat_rate: Decimal = Field(default=Decimal("0.10"), description="Taux de TVA")
    status: MenuItemStatus = MenuItemStatus.AVAILABLE
    pricing_strategy: PricingStrategy = PricingStrategy.COST_PLUS
    target_margin_percentage: Decimal = Field(
        default=Decimal("70"), ge=0, le=100, description="Marge cible en pourcentage"
    )
    position_in_menu: int = Field(default=0, ge=0)
    is_signature: bool = False
    allergens: list[str] = Field(default_factory=list)
    dietary_info: list[str] = Field(default_factory=list)

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
        if self.status == MenuItemStatus.SEASONAL:
            name = f"{name} 🍂"
        return name

    @property
    def is_available(self) -> bool:
        """Vérifie si l'article est disponible à la vente."""
        return self.status in [MenuItemStatus.AVAILABLE, MenuItemStatus.SEASONAL]

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

    def calculate_margin_ht(self, recipe_cost_per_portion: Decimal) -> Decimal:
        """
        Calcule la marge brute hors taxes par unité vendue.

        La marge représente le bénéfice brut avant déduction des charges
        variables et fixes (personnel, loyer, etc.).

        Args:
            recipe_cost_per_portion: Coût des ingrédients par portion

        Returns:
            Marge en euros HT

        Note:
            Cette marge ne tient compte que du coût des ingrédients,
            pas des coûts de main-d'œuvre ou autres charges.
        """
        return self.price_ht - recipe_cost_per_portion

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


class MenuItemBuilder:
    """Constructeur d'articles de menu."""

    @staticmethod
    def from_recipe(
        recipe: Recipe, base_price_ttc: Decimal, category: Optional[MenuCategory] = None
    ) -> MenuItem:
        """
        Crée un article de menu à partir d'une recette.

        Args:
            recipe: Recette de base
            base_price_ttc: Prix de base TTC
            category: Catégorie (déduite si non fournie)

        Returns:
            Article de menu créé
        """
        # Déduction de la catégorie si non fournie
        if category is None:
            category_mapping = {
                "entree": MenuCategory.APPETIZER,
                "plat": MenuCategory.MAIN_COURSE,
                "dessert": MenuCategory.DESSERT,
                "boisson": MenuCategory.BEVERAGE,
                "accompagnement": MenuCategory.SIDE,
            }
            category = category_mapping.get(recipe.category, MenuCategory.MAIN_COURSE)

        return MenuItem(
            id=f"menu_{recipe.id}",
            name=recipe.name,
            description=recipe.description,
            recipe=recipe,
            category=category,
            price_ttc=base_price_ttc,
        )

    @staticmethod
    def create_signature_item(
        recipe: Recipe,
        name: str,
        description: str,
        price_ttc: Decimal,
        category: MenuCategory,
    ) -> MenuItem:
        """
        Crée un article signature.

        Args:
            recipe: Recette de base
            name: Nom commercial
            description: Description marketing
            price_ttc: Prix TTC
            category: Catégorie

        Returns:
            Article signature
        """
        item = MenuItem(
            id=f"signature_{recipe.id}",
            name=name,
            description=description,
            recipe=recipe,
            category=category,
            price_ttc=price_ttc,
            is_signature=True,
            pricing_strategy=PricingStrategy.PREMIUM,
            target_margin_percentage=Decimal("80"),
        )
        return item
