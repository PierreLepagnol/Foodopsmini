"""Gestionnaire de menu complet"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from game_engine.domain.menu.menu_item import Plat, PlatStatus
from game_engine.domain.menu.types import MenuCategory
from game_engine.domain.menu.recipe import Recipe


class MenuSection(BaseModel):
    """
    Section de menu regroupant des articles par catégorie.

    Attributes:
        category: Catégorie de la section
        name: Nom d'affichage de la section
        description: Description de la section
        items: Articles de cette section
        display_order: Ordre d'affichage dans le menu
        is_active: Section active ou non
    """

    category: MenuCategory
    name: str
    description: str = ""
    items: list[Plat] = Field(default_factory=list)
    display_order: int = 0
    is_active: bool = True

    def add_item(self, item: Plat) -> None:
        """
        Ajoute un article de menu à cette section.

        Vérifie que l'article appartient à la bonne catégorie avant l'ajout
        et maintient l'ordre de tri automatiquement.

        Args:
            item: L'article de menu à ajouter

        Raises:
            ValueError: Si la catégorie de l'article ne correspond pas à celle de la section
        """
        if item.category != self.category:
            raise ValueError(
                f"L'article {item.name} ({item.category.value}) ne peut pas être "
                f"ajouté à la section {self.category.value}"
            )
        self.items.append(item)
        self._sort_items()

    def remove_item(self, item_id: str) -> bool:
        """
        Retire un article de la section.

        Args:
            item_id: ID de l'article à retirer

        Returns:
            True si l'article a été retiré, False s'il n'était pas présent
        """
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                return True
        return False

    def get_available_items(self) -> list[Plat]:
        """
        Filtre et retourne uniquement les articles actuellement disponibles.

        Un article est considéré comme disponible s'il a le statut AVAILABLE
        ou SEASONAL (selon la propriété is_available de Plat).

        Returns:
            Liste des articles disponibles à la vente
        """
        return [item for item in self.items if item.is_available]

    def get_signature_items(self) -> list[Plat]:
        """
        Retourne les articles signature de cette section.

        Les articles signature sont les spécialités du restaurant,
        mis en avant pour leur qualité ou leur originalité.

        Returns:
            Liste des articles signature de la section
        """
        return [item for item in self.items if item.is_signature]

    def _sort_items(self) -> None:
        """
        Trie automatiquement les articles par position puis par nom.

        Maintient l'ordre d'affichage cohérent dans la section.
        Les articles avec position_in_menu identique sont triés alphabétiquement.
        """
        self.items.sort(key=lambda x: (x.position_in_menu, x.name))

    def calculate_section_metrics(self) -> dict:
        """
        Calcule des métriques détaillées pour analyser la section.

        Fournit des statistiques utiles pour l'analyse de performance
        et l'optimisation de la section de menu.

        Returns:
            Dict contenant:
            - total_items: Nombre total d'articles
            - available_items: Nombre d'articles disponibles
            - average_price: Prix moyen des articles disponibles
            - price_range: (prix_min, prix_max) des articles disponibles
            - signature_count: Nombre d'articles signature
        """
        available_items = self.get_available_items()
        if not available_items:
            return {
                "total_items": len(self.items),
                "available_items": 0,
                "average_price": Decimal("0"),
                "price_range": (Decimal("0"), Decimal("0")),
                "signature_count": 0,
            }

        prices = [item.price_ttc for item in available_items]
        return {
            "total_items": len(self.items),
            "available_items": len(available_items),
            "average_price": sum(prices) / len(prices),
            "price_range": (min(prices), max(prices)),
            "signature_count": len(self.get_signature_items()),
        }


class MenuManager(BaseModel):
    """
    Gestionnaire de menu complet avec sections et articles.

    Attributes:
        name: Nom du menu
        description: Description du menu
        restaurant_type: Type de restaurant associé
        sections: Sections du menu par catégorie
        is_active: Menu actif ou non
        last_updated: Dernière mise à jour
    """

    name: str = "Menu Principal"
    description: str = ""
    sections: list[MenuSection] = Field(default_factory=list)
    is_active: bool = True

    def model_post_init(self, __context=None) -> None:
        """
        Initialisation post-création du gestionnaire de menu.

        Crée automatiquement les sections standard si aucune n'existe.

        Args:
            __context: Contexte Pydantic (inutilisé)
        """
        if not self.sections:
            self._create_default_sections()

    def _create_default_sections(self) -> None:
        """
        Crée les sections standard d'un menu de restaurant.

        Initialise les 5 catégories principales avec noms et descriptions
        appropriés pour un restaurant français. L'ordre d'affichage suit
        la logique traditionnelle d'un repas.
        """
        default_sections = {
            MenuCategory.APPETIZER: MenuSection(
                category=MenuCategory.APPETIZER,
                name="Entrées",
                description="Pour bien commencer votre repas",
                display_order=1,
            ),
            MenuCategory.MAIN_COURSE: MenuSection(
                category=MenuCategory.MAIN_COURSE,
                name="Plats Principaux",
                description="Nos spécialités",
                display_order=2,
            ),
            MenuCategory.SIDE: MenuSection(
                category=MenuCategory.SIDE,
                name="Accompagnements",
                description="Pour compléter votre plat",
                display_order=3,
            ),
            MenuCategory.DESSERT: MenuSection(
                category=MenuCategory.DESSERT,
                name="Desserts",
                description="La touche sucrée finale",
                display_order=4,
            ),
            MenuCategory.BEVERAGE: MenuSection(
                category=MenuCategory.BEVERAGE,
                name="Boissons",
                description="Pour accompagner votre repas",
                display_order=5,
            ),
        }
        self.sections.update(default_sections)

    def add_recipe_as_menu_item(
        self,
        recipe: Recipe,
        price_ttc: Decimal,
        category: Optional[MenuCategory] = None,
        **kwargs,
    ) -> Plat:
        """
        Ajoute une recette comme article de menu.

        Args:
            recipe: Recette à ajouter
            price_ttc: Prix de vente TTC
            category: Catégorie (déduite si non fournie)
            **kwargs: Arguments supplémentaires pour Plat

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

        # Création de l'article
        item = Plat(
            id=f"menu_{recipe.id}",
            name=recipe.name,
            description=recipe.description,
            recipe=recipe,
            category=category,
            price_ttc=price_ttc,
            **kwargs,
        )

        # Adaptation selon le type de restaurant
        if self.restaurant_type:
            item.adapt_to_restaurant_type(self.restaurant_type)

        # Ajout à la section appropriée
        if category not in self.sections:
            self.sections[category] = MenuSection(
                category=category,
                name=category.value.title(),
                display_order=len(self.sections),
            )

        self.sections[category].add_item(item)
        return item

    def remove_menu_item(self, item_id: str) -> bool:
        """
        Retire un article du menu.

        Args:
            item_id: ID de l'article à retirer

        Returns:
            True si l'article a été retiré, False sinon
        """
        for section in self.sections.values():
            if section.remove_item(item_id):
                return True
        return False

    def get_menu_item(self, item_id: str) -> Optional[Plat]:
        """
        Récupère un article de menu par son ID.

        Args:
            item_id: ID de l'article

        Returns:
            Article trouvé ou None
        """
        for section in self.sections.values():
            for item in section.items:
                if item.id == item_id:
                    return item
        return None

    def get_all_items(self) -> list[Plat]:
        """
        Retourne la liste exhaustive de tous les articles du menu.

        Parcourt toutes les sections actives et inactives pour collecter
        tous les articles, indépendamment de leur statut de disponibilité.

        Returns:
            Liste complète de tous les articles de menu
        """
        items = []
        for section in self.sections.values():
            items.extend(section.items)
        return items

    def get_available_items(self) -> list[Plat]:
        """
        Retourne tous les articles actuellement disponibles à la vente.

        Filtre automatiquement les articles selon leur statut de disponibilité
        dans toutes les sections du menu.

        Returns:
            Liste des articles disponibles pour commande
        """
        items = []
        for section in self.sections.values():
            items.extend(section.get_available_items())
        return items

    def get_signature_items(self) -> list[Plat]:
        """Retourne tous les articles signature."""
        items = []
        for section in self.sections.values():
            items.extend(section.get_signature_items())
        return items

    def get_items_by_category(self, category: MenuCategory) -> list[Plat]:
        """
        Retourne les articles d'une catégorie.

        Args:
            category: Catégorie recherchée

        Returns:
            Liste des articles de cette catégorie
        """
        section = self.sections.get(category)
        return section.items if section else []

    def update_item_status(self, item_id: str, status: PlatStatus) -> bool:
        """
        Met à jour le statut d'un article.

        Args:
            item_id: ID de l'article
            status: Nouveau statut

        Returns:
            True si la mise à jour a réussi, False sinon
        """
        item = self.get_menu_item(item_id)
        if item:
            item.status = status
            return True
        return False

    def update_item_price(self, item_id: str, new_price_ttc: Decimal) -> bool:
        """
        Met à jour le prix d'un article.

        Args:
            item_id: ID de l'article
            new_price_ttc: Nouveau prix TTC

        Returns:
            True si la mise à jour a réussi, False sinon
        """
        item = self.get_menu_item(item_id)
        if item:
            item.price_ttc = new_price_ttc
            return True
        return False

    def calculate_menu_metrics(self) -> dict:
        """
        Calcule des métriques complètes pour l'analyse du menu.

        Fournit une vue d'ensemble des performances du menu avec
        des indicateurs clés pour l'optimisation commerciale.

        Returns:
            Dict avec métriques détaillées:
            - total_items: Nombre total d'articles
            - available_items: Nombre d'articles disponibles
            - average_price: Prix moyen
            - price_range: Fourchette de prix (min, max)
            - signature_count: Nombre d'articles signature
            - sections_count: Nombre de sections
            - categories_coverage: Catégories avec articles disponibles
        """
        all_items = self.get_all_items()
        available_items = self.get_available_items()

        if not available_items:
            return {
                "total_items": len(all_items),
                "available_items": 0,
                "average_price": Decimal("0"),
                "price_range": (Decimal("0"), Decimal("0")),
                "signature_count": 0,
                "sections_count": len(self.sections),
                "categories_coverage": [],
            }

        prices = [item.price_ttc for item in available_items]
        categories_with_items = set(item.category for item in available_items)

        return {
            "total_items": len(all_items),
            "available_items": len(available_items),
            "average_price": sum(prices) / len(prices),
            "price_range": (min(prices), max(prices)),
            "signature_count": len(self.get_signature_items()),
            "sections_count": len(self.sections),
            "categories_coverage": list(categories_with_items),
        }

    def get_ordered_sections(self) -> list[MenuSection]:
        """Retourne les sections ordonnées pour l'affichage."""
        return sorted(
            [s for s in self.sections.values() if s.is_active],
            key=lambda x: x.display_order,
        )

    def validate_menu_completeness(self) -> dict[str, list[str]]:
        """
        Effectue une validation complète de la cohérence du menu.

        Vérifie la présence d'éléments essentiels et détecte les
        incohérences potentielles (prix aberrants, sections vides, etc.).

        Returns:
            Dictionnaire avec deux clés:
            - "errors": Liste des erreurs bloquantes
            - "warnings": Liste des avertissements non-bloquants

        Note:
            Les erreurs empêchent le bon fonctionnement du restaurant,
            les avertissements sont des suggestions d'amélioration.
        """
        errors = []
        warnings = []

        # Vérification des sections essentielles
        essential_categories = [MenuCategory.MAIN_COURSE]
        for category in essential_categories:
            if (
                category not in self.sections
                or not self.sections[category].get_available_items()
            ):
                errors.append("Aucun plat principal disponible")

        # Vérifications des prix
        all_items = self.get_available_items()
        if not all_items:
            errors.append("Aucun article disponible dans le menu")
        else:
            # Vérification de cohérence des prix
            prices_by_category = {}
            for item in all_items:
                if item.category not in prices_by_category:
                    prices_by_category[item.category] = []
                prices_by_category[item.category].append(item.price_ttc)

            # Détection de prix aberrants
            for category, prices in prices_by_category.items():
                if len(prices) > 1:
                    min_price, max_price = min(prices), max(prices)
                    if max_price > min_price * 3:  # Écart de plus de 300%
                        warnings.append(
                            f"Écart de prix important dans {category.value}: "
                            f"{min_price:.2f}€ - {max_price:.2f}€"
                        )

        return {"errors": errors, "warnings": warnings}

    def __str__(self) -> str:
        metrics = self.calculate_menu_metrics()
        return (
            f"Menu '{self.name}' - {metrics['available_items']} articles disponibles "
            f"(Prix moyen: {metrics['average_price']:.2f}€)"
        )
