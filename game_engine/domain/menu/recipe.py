"""Modèles des recettes"""

from decimal import Decimal

from pydantic import BaseModel, Field


class RecipeItem(BaseModel):
    """
    Représente un ingrédient dans une recette avec gestion des pertes.

    Modélise précisément les quantités d'ingrédients nécessaires en tenant
    compte des pertes réelles lors de la préparation et cuisson.
    Essential pour un calcul de coûts précis en restauration.

    Attributes:
        ingredient_id: Identifiant de l'ingrédient dans le catalogue
        quantity_brute: Quantité brute à acheter (avant pertes)
        rendement_prepa: Coefficient après épluchage/parage (0.0-1.0)
        rendement_cuisson: Coefficient après cuisson/réduction (0.0-1.0)

    Example:
        Pour 100g de pommes de terre dans l'assiette:
        - quantity_brute = 130g (pertes d'épluchage et cuisson)
        - rendement_prepa = 0.85 (15% de perte à l'épluchage)
        - rendement_cuisson = 0.9 (10% de perte à la cuisson)
    """

    ingredient_id: str
    quantity_brute: Decimal = Field(
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
    def quantity_nette(self) -> Decimal:
        """
        Calcule la quantité nette finale après toutes les pertes.

        Applique successivement les pertes de préparation puis de cuisson
        pour obtenir la quantité réellement présente dans l'assiette.

        Returns:
            Quantité effective utilisable après transformation

        Formula:
            quantity_nette = quantity_brute × rendement_prepa × rendement_cuisson
        """
        return self.quantity_brute * self.rendement_prepa * self.rendement_cuisson

    @property
    def perte_totale(self) -> Decimal:
        """
        Calcule le pourcentage de perte global de l'ingrédient.

        Combine les pertes de préparation et de cuisson pour obtenir
        le taux de perte total, essentiel pour le calcul des coûts.

        Returns:
            Pourcentage de perte (0.0 = pas de perte, 0.3 = 30% de perte)

        Example:
            Si rendement_prepa = 0.85 et rendement_cuisson = 0.9
            Perte totale = 1.0 - (0.85 × 0.9) = 0.235 (23.5% de perte)
        """
        return Decimal("1.0") - (self.rendement_prepa * self.rendement_cuisson)


class Recipe(BaseModel):
    """
    Modèle d'une recette de restaurant avec métadonnées opérationnelles.

    Encapsule tous les éléments nécessaires à l'exécution d'une recette
    en cuisine professionnelle : ingrédients, quantités, timing, difficulté.

    Attributes:
        id: Identifiant unique de la recette
        name: Nom commercial de la recette
        items: Liste des ingrédients avec quantités et rendements
        temps_prepa_min: Temps de préparation en minutes
        temps_service_min: Temps de finition/dressage en minutes
        portions: Nombre de portions produites par cette recette
        category: Catégorie culinaire (plat, entrée, dessert, etc.)
        difficulty: Niveau de difficulté technique (1=facile, 5=expert)
        description: Description ou notes sur la recette
    """

    id: str
    name: str
    ingredients: list[RecipeItem] = Field(min_length=1, description="Liste ingrédients")
    temps_prepa_min: int = Field(ge=0, description="Le temps de prépa")
    temps_service_min: int = Field(ge=0, description="Le temps de service")
    portions: int = Field(default=1, gt=0, description="Le nombre de portions")
    category: str = Field(default="plat", description="La catégorie")
    description: str = Field(default="", description="La description")
    difficulty: int = Field(default=1, ge=1, le=5, description="La difficulté")
    cost_per_portion: Decimal = Field(
        default=Decimal("0"), ge=0, description="coût par portion"
    )

    @property
    def temps_total_min(self) -> int:
        """
        Temps total d'occupation en cuisine = temps de préparation + temps de service
        """
        return self.temps_prepa_min + self.temps_service_min

    def get_ingredient_ids(self) -> list[str]:
        """
        Extrait la liste des identifiants d'ingrédients nécessaires.

        Pratique pour vérifier la disponibilité en stock,
        calculer les besoins d'approvisionnement ou valider
        la faisabilité d'une recette.

        Returns:
            Liste des IDs d'ingrédients (sans doublons)
        """
        return [item.ingredient_id for item in self.ingredients]

    def get_ingredient_quantity(self, ingredient_id: str) -> Decimal:
        """
        Récupère la quantité brute requise d'un ingrédient spécifique.

        Recherche dans la liste des ingrédients et retourne la quantité
        brute (avant pertes) nécessaire pour exécuter cette recette.

        Args:
            ingredient_id: Identifiant de l'ingrédient recherché

        Returns:
            Quantité brute nécessaire en unité de base

        Raises:
            ValueError: Si l'ingrédient n'existe pas dans cette recette

        Note:
            Pour la quantité nette (après pertes), utiliser quantity_nette
            de l'objet RecipeItem correspondant.
        """
        for item in self.ingredients:
            if item.ingredient_id == ingredient_id:
                return item.quantity_brute
        raise ValueError(
            f"Ingrédient {ingredient_id} non trouvé dans la recette {self.id}"
        )

    def __str__(self) -> str:
        """
        Représentation textuelle concise de la recette.

        Returns:
            Nom de la recette (X portions, Y min)

        Format: "Nom de la recette (X portions, Y min)"
        """
        return f"{self.name} ({self.portions} portions, {self.temps_total_min}min)"


def scale_recipe(recipe: Recipe, factor: int) -> Recipe:
    """
    Génère une version mise à l'échelle de cette recette.

    Crée une nouvelle recette avec toutes les quantités multipliées
    par le facteur donné. Utile pour adapter une recette de base
    aux besoins de production réels du service.

    Args:
        factor: Facteur multiplicateur (ex: 2.5 pour 2.5x plus de portions)

    Returns:
        Nouvelle instance de Recipe avec quantités et portions ajustées

    Note:
        - Les temps de préparation restent identiques
        - Les rendements sont conservés
        - L'ID et le nom sont modifiés pour éviter les conflits

    Example:
        Recette de base pour 4 portions -> factor=2.5 -> 10 portions
    """
    # Création des nouveaux items avec quantités ajustées
    # Les rendements restent identiques car ils sont intrinsèques à l'ingrédient
    scaled_items = [
        RecipeItem(
            ingredient_id=item.ingredient_id,
            quantity_brute=item.quantity_brute
            * factor,  # Seule la quantité est multipliée
            rendement_prepa=item.rendement_prepa,  # Rendements inchangés
            rendement_cuisson=item.rendement_cuisson,
        )
        for item in recipe.ingredients
    ]

    # Construction de la nouvelle recette mise à l'échelle
    return Recipe(
        id=f"{recipe.id}_x{factor}",  # ID unique pour éviter les conflits
        name=f"{recipe.name} (x{factor})",  # Nom explicite du facteur
        ingredients=scaled_items,
        temps_prepa_min=recipe.temps_prepa_min,  # Temps inchangés
        temps_service_min=recipe.temps_service_min,
        portions=int(recipe.portions * factor),  # Portions ajustées
        category=recipe.category,  # Métadonnées conservées
        difficulty=recipe.difficulty,
        description=recipe.description,
        cost_per_portion=recipe.cost_per_portion,
    )
