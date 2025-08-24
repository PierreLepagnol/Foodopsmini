"""
Modèles des recettes
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RecipeItem:
    """
    Représente un ingrédient dans une recette avec ses quantités et rendements.

    Attributes:
        ingredient_id: ID de l'ingrédient
        qty_brute: Quantité brute nécessaire
        rendement_prepa: Rendement après préparation (0.0-1.0)
        rendement_cuisson: Rendement après cuisson (0.0-1.0)
    """

    ingredient_id: str
    qty_brute: Decimal
    rendement_prepa: Decimal = Decimal("1.0")
    rendement_cuisson: Decimal = Decimal("1.0")

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.qty_brute < 0:
            raise ValueError(f"La quantité brute doit être positive: {self.qty_brute}")
        if not (0 < self.rendement_prepa <= 1):
            raise ValueError(
                f"Le rendement prépa doit être entre 0 et 1: {self.rendement_prepa}"
            )
        if not (0 < self.rendement_cuisson <= 1):
            raise ValueError(
                f"Le rendement cuisson doit être entre 0 et 1: {self.rendement_cuisson}"
            )

    @property
    def qty_nette(self) -> Decimal:
        """Quantité nette après préparation et cuisson."""
        return self.qty_brute * self.rendement_prepa * self.rendement_cuisson

    @property
    def perte_totale(self) -> Decimal:
        """Pourcentage de perte total."""
        return Decimal("1.0") - (self.rendement_prepa * self.rendement_cuisson)


@dataclass(frozen=True)
class Recipe:
    """
    Représente une recette complète avec ses ingrédients et temps.

    Attributes:
        id: Identifiant unique de la recette
        name: Nom de la recette
        items: Liste des ingrédients avec quantités
        temps_prepa_min: Temps de préparation en minutes
        temps_service_min: Temps de service en minutes
        portions: Nombre de portions produites
        category: Catégorie (entrée, plat, dessert, etc.)
        difficulty: Niveau de difficulté (1-5)
    """

    id: str
    name: str
    items: list[RecipeItem]
    temps_prepa_min: int
    temps_service_min: int
    portions: int = 1
    category: str = "plat"
    difficulty: int = 1
    description: str = ""

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.temps_prepa_min < 0:
            raise ValueError(
                f"Le temps de prépa doit être positif: {self.temps_prepa_min}"
            )
        if self.temps_service_min < 0:
            raise ValueError(
                f"Le temps de service doit être positif: {self.temps_service_min}"
            )
        if self.portions <= 0:
            raise ValueError(
                f"Le nombre de portions doit être positif: {self.portions}"
            )
        if not (1 <= self.difficulty <= 5):
            raise ValueError(f"La difficulté doit être entre 1 et 5: {self.difficulty}")
        if not self.items:
            raise ValueError("Une recette doit avoir au moins un ingrédient")

    @property
    def temps_total_min(self) -> int:
        """Temps total de préparation et service."""
        return self.temps_prepa_min + self.temps_service_min

    def get_ingredient_ids(self) -> list[str]:
        """Retourne la liste des IDs d'ingrédients utilisés."""
        return [item.ingredient_id for item in self.items]

    def get_ingredient_quantity(self, ingredient_id: str) -> Decimal:
        """
        Retourne la quantité brute d'un ingrédient pour cette recette.

        Args:
            ingredient_id: ID de l'ingrédient

        Returns:
            Quantité brute nécessaire

        Raises:
            ValueError: Si l'ingrédient n'est pas dans la recette
        """
        for item in self.items:
            if item.ingredient_id == ingredient_id:
                return item.qty_brute
        raise ValueError(
            f"Ingrédient {ingredient_id} non trouvé dans la recette {self.id}"
        )

    def scale_recipe(self, factor: Decimal) -> "Recipe":
        """
        Crée une nouvelle recette avec les quantités multipliées par un facteur.

        Args:
            factor: Facteur de multiplication

        Returns:
            Nouvelle recette avec quantités ajustées
        """
        scaled_items = [
            RecipeItem(
                ingredient_id=item.ingredient_id,
                qty_brute=item.qty_brute * factor,
                rendement_prepa=item.rendement_prepa,
                rendement_cuisson=item.rendement_cuisson,
            )
            for item in self.items
        ]

        return Recipe(
            id=f"{self.id}_x{factor}",
            name=f"{self.name} (x{factor})",
            items=scaled_items,
            temps_prepa_min=self.temps_prepa_min,
            temps_service_min=self.temps_service_min,
            portions=int(self.portions * factor),
            category=self.category,
            difficulty=self.difficulty,
            description=self.description,
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.portions} portions, {self.temps_total_min}min)"
