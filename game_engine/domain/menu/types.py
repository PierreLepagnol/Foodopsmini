"""
Types et énumérations spécifiques au domaine menu.

Ce module centralise tous les types personnalisés, énumérations
et structures de données spécifiques au systéme de gestion de menus.
Il compléte les types généraux du systéme avec des définitions
métier propres au domaine culinaire et commercial.

Responsabilities:
    - Définitions de types métier pour le menu
    - énumérations spécialisées pour la restauration
    - Types composites pour analyses avancées
    - Alias de types pour clarifier l'intention du code

Usage:
    from game_engine.domain.menu.types import (
        MenuPricingMatrix,
        SeasonalAvailability
    )
"""

from enum import Enum


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


# class MarketSegmentPreference(Enum):
#     """
#     Préférences des segments de clientéle pour les types de plats.

#     Caractérise les goéts et attentes de chaque segment de marché
#     pour optimiser l'offre et la tarification du menu.

#     Values:
#         STUDENTS: Prix bas, portions généreuses, simplicité
#         FAMILIES: Rapport qualité-prix, variété, plats familiaux
#         FOODIES: Qualité, originalité, expérience culinaire
#         BUSINESS: Rapidité, présentation, sophistication
#         TOURISTS: Authenticité, spécialités locales, découverte
#     """

#     STUDENTS = "students"  # Budget serré, simplicité, quantité
#     FAMILIES = "families"  # équilibre prix-qualité, choix variés
#     FOODIES = "foodies"  # Qualité, créativité, expérience
#     BUSINESS = "business"  # Efficacité, présentation, standing
#     TOURISTS = "tourists"  # Authenticité, découverte, spécialités


# class ProfitabilityTier(Enum):
#     """
#     Niveaux de rentabilité des articles de menu.

#     Classification des articles selon leur contribution
#     é la rentabilité globale du restaurant.

#     Values:
#         LOSS_LEADER: Article d'appel (marge faible/nulle)
#         LOW_MARGIN: Marge réduite (< 60%)
#         STANDARD: Marge normale (60-75%)
#         HIGH_MARGIN: Marge élevée (75-85%)
#         PREMIUM: Marge premium (> 85%)
#     """

#     LOSS_LEADER = "loss_leader"  # Prix d'appel, marge sacrifiée
#     LOW_MARGIN = "low_margin"  # Rentabilité faible mais volume
#     STANDARD = "standard"  # Rentabilité équilibrée
#     HIGH_MARGIN = "high_margin"  # Bonne rentabilité
#     PREMIUM = "premium"  # Rentabilité exceptionnelle


# class MenuPricingMatrix(BaseModel):
#     """
#     Matrice de tarification multicritéres pour un article de menu.

#     Encapsule tous les facteurs influenéant le prix d'un article :
#     coéts, positionnement, concurrence, saisonnalité.
#     Permet une tarification dynamique et optimisée.

#     Attributes:
#         base_cost: Coét de base (ingrédients + main-d'Suvre)
#         target_margin_percentage: Marge cible en pourcentage
#         competitive_price_range: Fourchette de prix concurrentielle
#         seasonal_adjustment: Ajustement saisonnier (-1.0 é +1.0)
#         demand_multiplier: Multiplicateur de demande (0.5 é 2.0)
#         premium_factor: Facteur premium pour articles signature
#     """

#     base_cost: Decimal
#     target_margin_percentage: Decimal
#     competitive_price_range: Tuple[Decimal, Decimal]
#     seasonal_adjustment: Decimal = Decimal("0")
#     demand_multiplier: Decimal = Decimal("1.0")
#     premium_factor: Decimal = Decimal("1.0")

#     def calculate_optimal_price(self) -> Decimal:
#         """
#         Calcule le prix optimal selon tous les critéres.

#         Returns:
#             Prix optimal TTC aprés tous ajustements
#         """
#         # Prix de base selon marge cible
#         base_price = self.base_cost / (1 - self.target_margin_percentage / 100)

#         # Application des ajustements
#         adjusted_price = base_price * (1 + self.seasonal_adjustment)
#         adjusted_price *= self.demand_multiplier
#         adjusted_price *= self.premium_factor

#         # Respect des limites concurrentielles
#         min_price, max_price = self.competitive_price_range
#         adjusted_price = max(min_price, min(adjusted_price, max_price))

#         return adjusted_price.quantize(Decimal("0.01"))


# class MenuPerformanceMetrics(BaseModel):
#     """
#     Métriques de performance consolidées pour un menu.

#     Regroupe tous les KPIs essentiels pour évaluer
#     l'efficacité commerciale et financiére d'un menu.

#     Attributes:
#         total_items: Nombre total d'articles
#         available_items: Nombre d'articles disponibles
#         signature_items: Nombre d'articles signature
#         average_price: Prix moyen pondéré
#         average_margin: Marge moyenne pondérée
#         food_cost_ratio: Ratio food cost global
#         category_balance: Répartition par catégorie
#         profitability_distribution: Répartition par niveau de marge
#         seasonal_coverage: Couverture saisonniére
#     """

#     total_items: int
#     available_items: int
#     signature_items: int
#     average_price: Decimal
#     average_margin: Decimal
#     food_cost_ratio: Decimal
#     category_balance: Dict[str, int]
#     profitability_distribution: Dict[ProfitabilityTier, int]
#     seasonal_coverage: Dict[SeasonalAvailability, int]

#     @property
#     def availability_rate(self) -> Decimal:
#         """Taux de disponibilité des articles."""
#         if self.total_items == 0:
#             return Decimal("0")
#         return Decimal(self.available_items) / Decimal(self.total_items) * 100

#     @property
#     def signature_ratio(self) -> Decimal:
#         """Pourcentage d'articles signature."""
#         if self.total_items == 0:
#             return Decimal("0")
#         return Decimal(self.signature_items) / Decimal(self.total_items) * 100


# class IngredientMarketData(BaseModel):
#     """
#     Données de marché pour un ingrédient.

#     Consolide les informations de marché nécessaires
#     é l'optimisation des achats et de la tarification.

#     Attributes:
#         ingredient_id: Identifiant de l'ingrédient
#         current_market_price: Prix de marché actuel
#         price_trend: Tendance des prix (-1 = baisse, +1 = hausse)
#         seasonal_factor: Facteur saisonnier actuel
#         availability_score: Score de disponibilité (0-100)
#         quality_premium: Surprix pour la qualité supérieure
#         forecast_price: Prix prévu é 30 jours
#     """

#     ingredient_id: str
#     current_market_price: Decimal
#     price_trend: Decimal  # -1.0 (forte baisse) é +1.0 (forte hausse)
#     seasonal_factor: Decimal  # Multiplicateur saisonnier
#     availability_score: int  # 0-100, impact sur prix et qualité
#     quality_premium: Decimal = Decimal("0")  # Surprix qualité
#     forecast_price: Decimal = Decimal("0")  # Prévision 30j
#     last_updated: date

#     def get_adjusted_price(self) -> Decimal:
#         """
#         Calcule le prix ajusté avec tous les facteurs.

#         Returns:
#             Prix ajusté tenant compte de tous les facteurs
#         """
#         adjusted = self.current_market_price * self.seasonal_factor
#         adjusted += self.quality_premium

#         # Ajustement selon disponibilité (pénurie = prix plus élevé)
#         availability_factor = 1 + (100 - self.availability_score) / 1000
#         adjusted *= Decimal(str(availability_factor))

#         return adjusted.quantize(Decimal("0.001"))


# # Types alias pour clarifier l'intention du code
# PlatId = str
# IngredientId = str
# RecipeId = str
# SupplierId = str

# # Structures composites pour analyses complexes
# PriceCompetitiveAnalysis = Dict[str, Tuple[Decimal, Decimal, Decimal]]
# SeasonalPricingCalendar = Dict[int, Decimal]  # mois -> ajustement prix
# MenuCategoryPerformance = Dict[str, MenuPerformanceMetrics]
# SupplierPriceMatrix = Dict[SupplierId, Dict[IngredientId, Decimal]]

# # Types pour l'optimisation de menu
# OptimizationSuggestion = Tuple[
#     str, str, Decimal, str
# ]  # item, action, impact, rationale
# MenuOptimizationReport = List[OptimizationSuggestion]

# # Types pour la gestion des stocks et approvisionnement
# StockRotationData = Dict[IngredientId, Tuple[int, date]]  # quantité, DLC la plus proche
# PurchaseRecommendation = Dict[
#     IngredientId, Tuple[Decimal, SupplierId, Decimal]
# ]  # quantité, fournisseur, coét


# def calculate_menu_complexity_score(recipes: List) -> Decimal:
#     """
#     Calcule un score de complexité globale du menu.

#     évalue la complexité opérationnelle d'un menu basé sur
#     la difficulté des recettes et leur temps de préparation.

#     Args:
#         recipes: Liste des recettes du menu

#     Returns:
#         Score de complexité (1.0 = trés simple, 5.0 = trés complexe)
#     """
#     if not recipes:
#         return Decimal("1.0")

#     total_complexity = Decimal("0")
#     total_weight = Decimal("0")

#     for recipe in recipes:
#         # Pondération par temps de préparation (plus long = plus impactant)
#         weight = Decimal(str(recipe.temps_total_min))
#         complexity = Decimal(str(recipe.difficulty))

#         total_complexity += complexity * weight
#         total_weight += weight

#     if total_weight == 0:
#         return Decimal("1.0")

#     return (total_complexity / total_weight).quantize(Decimal("0.1"))


# def estimate_kitchen_capacity_requirement(
#     recipes: List, expected_covers: int
# ) -> Dict[str, int]:
#     """
#     Estime les besoins en capacité de cuisine pour un menu donné.

#     Calcule les besoins en personnel et équipement selon
#     la complexité du menu et le volume attendu.

#     Args:
#         recipes: Liste des recettes du menu
#         expected_covers: Nombre de couverts attendus

#     Returns:
#         Dict avec les besoins estimés (personnel, temps, équipement)
#     """
#     if not recipes:
#         return {"cooks_needed": 0, "prep_time_hours": 0, "service_time_hours": 0}

#     total_prep_time = sum(recipe.temps_prepa_min for recipe in recipes)
#     total_service_time = sum(recipe.temps_service_min for recipe in recipes)

#     # Estimation basée sur la charge de travail
#     covers_factor = expected_covers / 100  # Base 100 couverts

#     return {
#         "cooks_needed": max(1, int(len(recipes) / 8 * covers_factor)),
#         "prep_time_hours": int(total_prep_time * covers_factor / 60),
#         "service_time_hours": int(total_service_time * covers_factor / 60),
#         "complexity_adjustment": float(calculate_menu_complexity_score(recipes)),
#     }
