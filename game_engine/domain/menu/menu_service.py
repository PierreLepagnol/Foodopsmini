"""Services de menu et stratégies de tarification"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from game_engine.domain.menu.ingredient import IngredientQualityManager
from game_engine.domain.menu.menu import MenuManager
from game_engine.domain.menu.menu_item import MenuItem, MenuCategory
from game_engine.domain.menu.recipe import Recipe
from game_engine.domain.menu.recipe_costing import RecipeCostCalculator
from game_engine.domain.stock.stock import StockLot
from game_engine.domain.types import RestaurantType


class MenuAnalytics(BaseModel):
    """
    Modèle d'analyse des performances et rentabilité du menu.
    
    Regroupe tous les indicateurs clés de performance (KPI) nécessaires
    pour évaluer l'efficacité commerciale et financière d'un menu.
    
    Attributes:
        total_revenue_potential: Potentiel de revenus total
        average_margin_percentage: Marge moyenne en pourcentage
        food_cost_percentage: Ratio food cost global
        price_competitiveness_score: Score de compétitivité des prix
        category_coverage_score: Couverture des catégories de menu
        signature_items_ratio: Pourcentage d'articles signature
    """

    total_revenue_potential: Decimal = Decimal("0")
    average_margin_percentage: Decimal = Decimal("0")
    food_cost_percentage: Decimal = Decimal("0")
    price_competitiveness_score: Decimal = Decimal("0")
    category_coverage_score: Decimal = Decimal("0")
    signature_items_ratio: Decimal = Decimal("0")


class CompetitorPricing(BaseModel):
    """
    Structure des données de veille concurrentielle pour la tarification.
    
    Encapsule les informations de prix collectées sur le marché
    pour une catégorie d'articles donnée.
    
    Attributes:
        category: Catégorie d'articles concernée
        item_name: Nom de référence de l'article
        competitor_price_low: Prix le plus bas observé
        competitor_price_high: Prix le plus haut observé
        market_average: Prix moyen du marché
    """

    category: MenuCategory
    item_name: str
    competitor_price_low: Decimal
    competitor_price_high: Decimal
    market_average: Decimal

    @property
    def price_range(self) -> tuple[Decimal, Decimal]:
        """
        Retourne la fourchette de prix observée sur le marché.
        
        Returns:
            Tuple (prix_min, prix_max) de la concurrence
            
        Note:
            Utile pour positionner ses propres prix dans le marché
        """
        return (self.competitor_price_low, self.competitor_price_high)


class MenuOptimizationSuggestion(BaseModel):
    """
    Recommandation d'optimisation pour un article de menu.
    
    Structure une suggestion d'amélioration basée sur l'analyse
    des performances, de la concurrence et des objectifs de rentabilité.
    
    Attributes:
        item_id: Identifiant de l'article concerné
        suggestion_type: Type d'action recommandée
        current_value: Valeur actuelle à modifier
        suggested_value: Nouvelle valeur proposée
        expected_impact: Description de l'impact attendu
        rationale: Justification de la recommandation
        confidence_score: Niveau de confiance (0-1)
    """

    item_id: str
    suggestion_type: (
        str  # "price_increase", "price_decrease", "remove", "promote", "reposition"
    )
    current_value: Decimal
    suggested_value: Decimal
    expected_impact: str
    rationale: str
    confidence_score: Decimal  # 0-1


class MenuService:
    """
    Service central pour la création, gestion et optimisation des menus.
    
    Orchestre les différents composants (coûts, qualité, tarification)
    pour fournir une gestion intelligente et automatisée des menus.
    
    Responsibilities:
        - Création de menus à partir de recettes
        - Optimisation des prix selon la concurrence
        - Analyse des performances et KPIs
        - Recommandations d'amélioration
        - Suggestions de composition optimale
    """

    def __init__(
        self,
        cost_calculator: RecipeCostCalculator,
        quality_manager: IngredientQualityManager,
    ):
        """
        Initialise le service avec ses dépendances.
        
        Args:
            cost_calculator: Calculateur de coûts de recettes
            quality_manager: Gestionnaire de qualité des ingrédients
        """
        self.cost_calculator = cost_calculator
        self.quality_manager = quality_manager

    def create_menu_from_recipes(
        self,
        recipes: list[Recipe],
        restaurant_type: RestaurantType,
        target_margin: Decimal = Decimal("70"),
    ) -> MenuManager:
        """
        Génère automatiquement un menu optimisé à partir de recettes.
        
        Convertit une liste de recettes en menu commercial complet
        avec tarification adaptée au type de restaurant et aux objectifs
        de marge. Calcule les coûts réels et applique les stratégies
        de prix appropriées.
        
        Args:
            recipes: Collection de recettes disponibles
            restaurant_type: Concept du restaurant (influence la tarification)
            target_margin: Objectif de marge brute en % (défaut: 70%)
            
        Returns:
            MenuManager prêt à l'emploi avec articles tarifiés
            
        Process:
            1. Calcul du coût réel de chaque recette
            2. Application de la marge cible selon le type de restaurant
            3. Création des articles de menu
            4. Organisation par sections
        """
        menu = MenuManager(
            name=f"Menu {restaurant_type.display_name}", restaurant_type=restaurant_type
        )

        for recipe in recipes:
            # Calcul du coût de la recette
            cost_breakdown = self.cost_calculator.calculate_recipe_cost(recipe)
            cost_per_portion = cost_breakdown.total_cost_with_labor / recipe.portions

            # Calcul du prix suggéré selon la marge cible
            suggested_price = self._calculate_suggested_price(
                cost_per_portion, target_margin, restaurant_type
            )

            # Ajout au menu
            menu.add_recipe_as_menu_item(recipe, suggested_price)

        return menu

    def optimize_menu_pricing(
        self,
        menu: MenuManager,
        competitor_data: list[CompetitorPricing],
        stock_lots: Optional[list[StockLot]] = None,
    ) -> list[MenuOptimizationSuggestion]:
        """
        Analyse et propose des optimisations de tarification intelligentes.
        
        Croise les données internes (coûts, marges) avec l'intelligence
        concurrentielle pour identifier les opportunités d'amélioration.
        
        Args:
            menu: Menu actuel à analyser et optimiser
            competitor_data: Benchmark des prix de la concurrence par catégorie
            stock_lots: Stock disponible pour calcul de coûts réels (optionnel)
            
        Returns:
            Liste de recommandations triées par niveau de confiance
            
        Analysis Criteria:
            - Position concurrentielle (trop cher/pas assez cher)
            - Rentabilité (marge trop faible/excessive)
            - Cohérence interne du menu
            - Opportunités de repositionnement
        """
        suggestions = []
        competitor_by_category = {data.category: data for data in competitor_data}

        for item in menu.get_available_items():
            # Calcul du coût actuel
            cost_breakdown = self.cost_calculator.calculate_recipe_cost(
                item.recipe, stock_lots
            )
            current_cost = cost_breakdown.total_cost_with_labor / item.recipe.portions

            # Analyse de la marge actuelle
            current_margin = item.calculate_margin_ht(current_cost)
            current_margin_pct = (
                (current_margin / item.price_ht) * 100
                if item.price_ht > 0
                else Decimal("0")
            )

            # Comparaison avec la concurrence
            competitor_info = competitor_by_category.get(item.category)
            if competitor_info:
                suggestions.extend(
                    self._analyze_competitive_position(
                        item, competitor_info, current_cost
                    )
                )

            # Analyse de la marge
            suggestions.extend(
                self._analyze_margin_optimization(
                    item, current_cost, current_margin_pct
                )
            )

        return sorted(suggestions, key=lambda x: x.confidence_score, reverse=True)

    def calculate_menu_analytics(
        self,
        menu: MenuManager,
        stock_lots: Optional[list[StockLot]] = None,
    ) -> MenuAnalytics:
        """
        Génère un tableau de bord complet des performances du menu.
        
        Calcule tous les KPIs essentiels pour le pilotage commercial
        et financier du restaurant, en tenant compte des coûts réels
        et de la structure actuelle du menu.
        
        Args:
            menu: Menu à analyser en détail
            stock_lots: Inventaire pour coûts réels (optionnel)
            
        Returns:
            Tableau de bord avec métriques consolidées
            
        Calculated Metrics:
            - Potentiel de revenus global
            - Marge moyenne pondérée
            - Food cost consolidé
            - Couverture des catégories
            - Ratio d'articles premium/signature
        """
        available_items = menu.get_available_items()
        if not available_items:
            return MenuAnalytics()

        total_revenue = Decimal("0")
        total_margin = Decimal("0")
        total_cost = Decimal("0")

        for item in available_items:
            cost_breakdown = self.cost_calculator.calculate_recipe_cost(
                item.recipe, stock_lots
            )
            item_cost = cost_breakdown.total_cost_with_labor / item.recipe.portions

            # Estimation de revenus basée sur le prix
            estimated_revenue = item.price_ht
            item_margin = item.calculate_margin_ht(item_cost)

            total_revenue += estimated_revenue
            total_margin += item_margin
            total_cost += item_cost

        # Calculs des métriques
        avg_margin_pct = (
            (total_margin / total_revenue) * 100 if total_revenue > 0 else Decimal("0")
        )
        food_cost_pct = (
            (total_cost / total_revenue) * 100 if total_revenue > 0 else Decimal("0")
        )

        # Score de couverture des catégories
        available_categories = set(item.category for item in available_items)
        total_categories = len(MenuCategory)
        category_coverage = (len(available_categories) / total_categories) * 100

        # Ratio d'articles signature
        signature_count = len(menu.get_signature_items())
        signature_ratio = (signature_count / len(available_items)) * 100

        return MenuAnalytics(
            total_revenue_potential=total_revenue,
            average_margin_percentage=avg_margin_pct,
            food_cost_percentage=food_cost_pct,
            category_coverage_score=Decimal(str(category_coverage)),
            signature_items_ratio=Decimal(str(signature_ratio)),
        )

    def suggest_menu_composition(
        self,
        available_recipes: list[Recipe],
        restaurant_type: RestaurantType,
        max_items_per_category: int = 8,
    ) -> dict[MenuCategory, list[Recipe]]:
        """
        Recommande la composition optimale d'un menu selon le concept.
        
        Analyse le portefeuille de recettes disponibles et sélectionne
        la combinaison optimale pour chaque catégorie, en tenant compte
        du positionnement du restaurant et des contraintes opérationnelles.
        
        Args:
            available_recipes: Pool de recettes à évaluer
            restaurant_type: Concept qui influence la sélection
            max_items_per_category: Limite par section (défaut: 8)
            
        Returns:
            Dictionnaire {catégorie: [recettes_sélectionnées]}
            
        Selection Criteria:
            - Adaptation au type de restaurant
            - Complexité vs capacité opérationnelle
            - Temps de préparation compatible
            - Diversité et complémentarité
            - Potentiel de marge
        """
        # Groupement par catégorie
        recipes_by_category = {}
        for recipe in available_recipes:
            category_mapping = {
                "entree": MenuCategory.APPETIZER,
                "plat": MenuCategory.MAIN_COURSE,
                "dessert": MenuCategory.DESSERT,
                "boisson": MenuCategory.BEVERAGE,
                "accompagnement": MenuCategory.SIDE,
            }
            category = category_mapping.get(recipe.category, MenuCategory.MAIN_COURSE)

            if category not in recipes_by_category:
                recipes_by_category[category] = []
            recipes_by_category[category].append(recipe)

        # Sélection optimale par catégorie
        recommendations = {}
        for category, recipes in recipes_by_category.items():
            # Tri par score de qualité et complexité
            scored_recipes = []
            for recipe in recipes:
                score = self._calculate_recipe_score(recipe, restaurant_type)
                scored_recipes.append((recipe, score))

            # Sélection des meilleurs
            scored_recipes.sort(key=lambda x: x[1], reverse=True)
            selected = [r[0] for r in scored_recipes[:max_items_per_category]]
            recommendations[category] = selected

        return recommendations

    def _calculate_suggested_price(
        self,
        cost_per_portion: Decimal,
        target_margin: Decimal,
        restaurant_type: RestaurantType,
    ) -> Decimal:
        """
        Calcule le prix de vente optimal selon la stratégie du restaurant.
        
        Applique des ajustements de marge selon le positionnement
        et les contraintes spécifiques de chaque type de restaurant.
        
        Args:
            cost_per_portion: Coût unitaire des ingrédients
            target_margin: Marge cible de base
            restaurant_type: Type qui influence l'ajustement
            
        Returns:
            Prix TTC optimisé avec TVA 10%
            
        Margin Adjustments:
            - FAST: -10% (volume et rapidité)
            - CLASSIC: Standard (référence)
            - BRASSERIE: +10% (service et ambiance)
            - GASTRONOMIQUE: +30% (excellence et unicité)
        """
        # Ajustement de la marge selon le type de restaurant
        margin_adjustments = {
            RestaurantType.FAST: Decimal("0.9"),  # -10%
            RestaurantType.CLASSIC: Decimal("1.0"),  # Standard
            RestaurantType.BRASSERIE: Decimal("1.1"),  # +10%
            RestaurantType.GASTRONOMIQUE: Decimal("1.3"),  # +30%
        }

        adjusted_margin = target_margin * margin_adjustments.get(
            restaurant_type, Decimal("1.0")
        )
        suggested_price_ht = cost_per_portion / ((100 - adjusted_margin) / 100)

        # Application de la TVA
        return suggested_price_ht * Decimal("1.10")  # TVA 10%

    def _analyze_competitive_position(
        self,
        item: MenuItem,
        competitor_info: CompetitorPricing,
        current_cost: Decimal,
    ) -> list[MenuOptimizationSuggestion]:
        """Analyse la position concurrentielle d'un article."""
        suggestions = []

        # Comparaison avec les prix du marché
        if item.price_ttc > competitor_info.competitor_price_high * Decimal("1.2"):
            # Prix trop élevé
            suggested_price = competitor_info.market_average * Decimal("1.1")
            if suggested_price > current_cost * Decimal("2"):  # Marge minimale
                suggestions.append(
                    MenuOptimizationSuggestion(
                        item_id=item.id,
                        suggestion_type="price_decrease",
                        current_value=item.price_ttc,
                        suggested_value=suggested_price,
                        expected_impact="Amélioration de la compétitivité",
                        rationale=f"Prix {item.price_ttc:.2f}€ trop élevé vs marché {competitor_info.market_average:.2f}€",
                        confidence_score=Decimal("0.8"),
                    )
                )

        elif item.price_ttc < competitor_info.competitor_price_low * Decimal("0.8"):
            # Prix trop bas, opportunité d'augmentation
            suggested_price = competitor_info.market_average * Decimal("0.9")
            suggestions.append(
                MenuOptimizationSuggestion(
                    item_id=item.id,
                    suggestion_type="price_increase",
                    current_value=item.price_ttc,
                    suggested_value=suggested_price,
                    expected_impact="Amélioration de la marge",
                    rationale=f"Prix {item.price_ttc:.2f}€ sous-valorisé vs marché {competitor_info.market_average:.2f}€",
                    confidence_score=Decimal("0.7"),
                )
            )

        return suggestions

    def _analyze_margin_optimization(
        self,
        item: MenuItem,
        current_cost: Decimal,
        current_margin_pct: Decimal,
    ) -> list[MenuOptimizationSuggestion]:
        """Analyse l'optimisation de la marge."""
        suggestions = []

        # Marge trop faible
        if current_margin_pct < Decimal("50"):
            target_margin = Decimal("60")
            suggested_price = (
                current_cost / ((100 - target_margin) / 100) * Decimal("1.10")
            )

            suggestions.append(
                MenuOptimizationSuggestion(
                    item_id=item.id,
                    suggestion_type="price_increase",
                    current_value=item.price_ttc,
                    suggested_value=suggested_price,
                    expected_impact="Amélioration de la rentabilité",
                    rationale=f"Marge actuelle {current_margin_pct:.1f}% trop faible",
                    confidence_score=Decimal("0.9"),
                )
            )

        # Marge très élevée (risque de perte de compétitivité)
        elif current_margin_pct > Decimal("85"):
            suggestions.append(
                MenuOptimizationSuggestion(
                    item_id=item.id,
                    suggestion_type="reposition",
                    current_value=current_margin_pct,
                    suggested_value=Decimal("75"),
                    expected_impact="Amélioration du rapport qualité-prix",
                    rationale=f"Marge actuelle {current_margin_pct:.1f}% très élevée",
                    confidence_score=Decimal("0.6"),
                )
            )

        return suggestions

    def _calculate_recipe_score(
        self,
        recipe: Recipe,
        restaurant_type: RestaurantType,
    ) -> Decimal:
        """
        Évalue l'adéquation d'une recette avec le concept de restaurant.
        
        Calcule un score composite basé sur la complexité,
        le temps de préparation et l'adéquation avec le type d'établissement.
        
        Args:
            recipe: Recette à évaluer
            restaurant_type: Concept de référence
            
        Returns:
            Score de compatibilité (plus élevé = mieux adapté)
            
        Scoring Logic:
            - FAST: Privilégie la simplicité et la rapidité
            - GASTRONOMIQUE: Valorise la complexité et l'élaboration
            - Bonus pour temps de préparation adapté au concept
            - Pénalité pour inadaptation au positionnement
        """
        base_score = Decimal("50")

        # Bonus selon la difficulté et le type de restaurant
        # Chaque type a une préférence différente pour la complexité
        difficulty_bonus = {
            RestaurantType.FAST: max(0, 3 - recipe.difficulty)
            * 5,  # Préfère simplicité (moins c'est complexe, mieux c'est)
            RestaurantType.CLASSIC: recipe.difficulty * 3,  # Équilibré
            RestaurantType.BRASSERIE: recipe.difficulty * 4,  # Un peu plus élaboré
            RestaurantType.GASTRONOMIQUE: recipe.difficulty * 8,  # Valorise la complexité
        }

        base_score += Decimal(str(difficulty_bonus.get(restaurant_type, 0)))

        # Bonus pour temps de préparation adapté au concept
        if restaurant_type == RestaurantType.FAST and recipe.temps_total_min <= 15:
            base_score += Decimal("20")  # Fast-food privilégie la rapidité
        elif (
            restaurant_type == RestaurantType.GASTRONOMIQUE
            and recipe.temps_total_min >= 30
        ):
            base_score += Decimal("15")  # Gastronomie valorise l'élaboration

        return base_score
