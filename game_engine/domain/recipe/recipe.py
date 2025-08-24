"""
Modèles des recettes
"""

from dataclasses import dataclass
from decimal import Decimal

from pydantic import BaseModel, Field


class RecipeItem(BaseModel):
    """
    Représente un ingrédient dans une recette avec ses quantités et rendements.

    Attributes:
        ingredient_id: ID de l'ingrédient
        qty_brute: Quantité brute nécessaire
        rendement_prepa: Rendement après préparation (0.0-1.0)
        rendement_cuisson: Rendement après cuisson (0.0-1.0)
    """

    ingredient_id: str
    qty_brute: Decimal = Field(
        ge=0, description="Quantité brute nécessaire (doit être positive)"
    )
    rendement_prepa: Decimal = Field(
        default=Decimal("1.0"),
        gt=0,
        le=1,
        description="Rendement après préparation (entre 0 et 1)",
    )
    rendement_cuisson: Decimal = Field(
        default=Decimal("1.0"),
        gt=0,
        le=1,
        description="Rendement après cuisson (entre 0 et 1)",
    )

    @property
    def qty_nette(self) -> Decimal:
        """Quantité nette après préparation et cuisson."""
        return self.qty_brute * self.rendement_prepa * self.rendement_cuisson

    @property
    def perte_totale(self) -> Decimal:
        """Pourcentage de perte total."""
        return Decimal("1.0") - (self.rendement_prepa * self.rendement_cuisson)


class Recipe(BaseModel):
    """
    Représente une recette complète avec ses ingrédients et temps.
    """

    id: str
    name: str
    items: list[RecipeItem] = Field(
        min_length=1, description="Une recette doit avoir au moins un ingrédient"
    )
    temps_prepa_min: int = Field(
        ge=0, description="Le temps de prépa doit être positif"
    )
    temps_service_min: int = Field(
        ge=0, description="Le temps de service doit être positif"
    )
    portions: int = Field(
        default=1, gt=0, description="Le nombre de portions doit être positif"
    )
    category: str = "plat"
    difficulty: int = Field(
        default=1, ge=1, le=5, description="La difficulté doit être entre 1 et 5"
    )
    description: str = ""

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
