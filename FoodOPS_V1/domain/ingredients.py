# foodops/domain/ingredients.py
"""
Définitions de base (Enums + dataclass Ingredient) ET pont vers le catalogue FR.
D'autres modules importent parfois `foodops.domain.ingredients`, donc on ré-exporte
"""

import json
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, Field, ValidationError
from FoodOPS_V1.domain.types import RestaurantType


class IngredientCategory(Enum):
    VIANDE = "VIANDE"
    POISSON = "POISSON"
    LEGUME = "LEGUME"
    FECULENT = "FECULENT"
    LEGUMINEUSE = "LEGUMINEUSE"
    PRODUIT_LAITIER = "PRODUIT_LAITIER"
    CONDIMENT = "CONDIMENT"
    BOULANGERIE = "BOULANGERIE"
    AUTRE = "AUTRE"


class Tier(Enum):
    ALL = "ALL"
    BISTRO_PLUS = "BISTRO_PLUS"
    GASTRO_ONLY = "GASTRO_ONLY"


class FoodGrade(Enum):
    """Gammes pro FR (1→5).
    On s'en sert pour coût/qualité/coût de main d'oeuvre implicite.
    """

    G1_FRAIS_BRUT = "G1_FRAIS_BRUT"  # 1ère gamme : frais bruts
    G2_CONSERVE = "G2_CONSERVE"  # 2e gamme : conserve/semi-conserve
    G3_SURGELE = "G3_SURGELE"  # 3e gamme : surgelé
    G4_CRU_PRET = "G4_CRU_PRET"  # 4e gamme : cru prêt à l'emploi
    G5_CUIT_SOUS_VIDE = "G5_CUIT_SOUS_VIDE"  # 5e gamme : cuit/vide/régénération


class CatalogConfig(BaseModel):
    """Configuration model for ingredient catalog validation."""


# Coefficients de perception qualité selon le type de resto et la gamme
# 1.0 = qualité perçue optimale, < 1.0 = perçu comme moins qualitatif
QUALITY_PERCEPTION: Dict[RestaurantType, Dict[FoodGrade, float]] = {
    RestaurantType.FAST_FOOD: {
        FoodGrade.G1_FRAIS_BRUT: 1.0,
        FoodGrade.G2_CONSERVE: 0.9,
        FoodGrade.G3_SURGELE: 0.95,
        FoodGrade.G4_CRU_PRET: 1.0,
        FoodGrade.G5_CUIT_SOUS_VIDE: 0.95,
    },
    RestaurantType.BISTRO: {
        FoodGrade.G1_FRAIS_BRUT: 1.0,
        FoodGrade.G2_CONSERVE: 0.8,
        FoodGrade.G3_SURGELE: 0.85,
        FoodGrade.G4_CRU_PRET: 0.95,
        FoodGrade.G5_CUIT_SOUS_VIDE: 0.9,
    },
    RestaurantType.GASTRO: {
        FoodGrade.G1_FRAIS_BRUT: 1.0,
        FoodGrade.G2_CONSERVE: 0.6,
        FoodGrade.G3_SURGELE: 0.5,  # saumon surgelé en gastro => grosse pénalité
        FoodGrade.G4_CRU_PRET: 0.85,
        FoodGrade.G5_CUIT_SOUS_VIDE: 0.8,
    },
}


# -------------
class Ingredient(BaseModel):
    name: str
    categories: List[IngredientCategory]
    prices_by_grade: Dict[FoodGrade, float]
    perish_days: int
    fit_score: Dict[str, float]
    tier: Tier = Field(default=Tier.ALL)
    fit_score_keys: List[str] = Field(default=["FAST_FOOD", "BISTRO", "GASTRO"])
    grade: FoodGrade = FoodGrade.G1_FRAIS_BRUT


def load_catalog_config(filepath: str) -> Dict[str, Ingredient]:
    """Charge la configuration du catalogue d'ingrédients depuis un fichier JSON.

    Lit un fichier JSON contenant la configuration des ingrédients et retourne
    un dictionnaire structuré avec validation Pydantic.

    Paramètres
    ----------
    filepath : str
        Chemin vers le fichier JSON de configuration du catalogue.

    Retour
    ------
    Dict[str, Ingredient]
        Dictionnaire mappant chaque nom d'ingrédient à son objet Ingredient.

    Exemple
    -------
    >>> config = load_catalog_config("catalog_config.json")
    >>> "Poulet" in config
    True
    >>> isinstance(config["Poulet"], Ingredient)
    True

    Lève
    ----
    FileNotFoundError
        Si le fichier de configuration n'existe pas.
    ValueError
        Si les données du JSON ne sont pas valides selon le modèle Ingredient.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    catalog: Dict[str, Ingredient] = {}
    for ingredient_name, ingredient_data in raw_data.items():
        try:
            # Ajout du nom de l'ingrédient aux données
            ingredient_data["name"] = ingredient_name
            catalog[ingredient_name] = Ingredient.model_validate(ingredient_data)
        except ValidationError as e:
            raise ValueError(f"Validation error for ingredient {ingredient_name}: {e}")

    return catalog


CATALOG = load_catalog_config(
    "/home/lepagnol/Documents/Perso/Games/foodopsV0TL/FoodOPS_V1/data/catalog_config.json"
)


def get_all_ingredients() -> List[Ingredient]:
    """
    Retourne une liste d'ingrédients avec plusieurs gammes disponibles.
    """
    ingredients: List[Ingredient] = []

    # Viandes
    ingredients += [
        Ingredient(
            "Steak haché",
            12.0,
            IngredientCategory.VIANDE,
            FoodGrade.G1_FRAIS_BRUT,
            5,
        ),
        Ingredient(
            "Steak haché",
            9.0,
            IngredientCategory.VIANDE,
            FoodGrade.G3_SURGELE,
            180,
        ),
        Ingredient(
            "Poulet",
            11.0,
            IngredientCategory.VIANDE,
            FoodGrade.G1_FRAIS_BRUT,
            5,
        ),
        Ingredient("Poulet", 8.0, IngredientCategory.VIANDE, FoodGrade.G3_SURGELE, 180),
    ]

    # Poissons
    ingredients += [
        Ingredient(
            "Saumon",
            20.0,
            IngredientCategory.POISSON,
            FoodGrade.G1_FRAIS_BRUT,
            3,
        ),
        Ingredient(
            "Saumon",
            15.0,
            IngredientCategory.POISSON,
            FoodGrade.G3_SURGELE,
            180,
        ),
        Ingredient(
            "Cabillaud",
            16.0,
            IngredientCategory.POISSON,
            FoodGrade.G1_FRAIS_BRUT,
            3,
        ),
        Ingredient(
            "Cabillaud",
            12.0,
            IngredientCategory.POISSON,
            FoodGrade.G3_SURGELE,
            180,
        ),
    ]

    # Féculents
    ingredients += [
        Ingredient("Riz", 2.5, IngredientCategory.FECULENT, FoodGrade.G2_CONSERVE, 365),
        Ingredient("Riz", 2.0, IngredientCategory.FECULENT, FoodGrade.G3_SURGELE, 180),
    ]

    # Produits laitiers
    ingredients += [
        Ingredient(
            "Fromage cheddar",
            7.0,
            IngredientCategory.PRODUIT_LAITIER,
            FoodGrade.G3_SURGELE,
            180,
        ),
        Ingredient(
            "Fromage cheddar",
            8.5,
            IngredientCategory.PRODUIT_LAITIER,
            FoodGrade.G1_FRAIS_BRUT,
            15,
        ),
    ]

    # oeufs
    ingredients += [
        Ingredient(
            "oeufs",
            4.0,
            IngredientCategory.PRODUIT_LAITIER,
            FoodGrade.G1_FRAIS_BRUT,
            15,
        ),
        Ingredient(
            "oeufs",
            5.5,
            IngredientCategory.PRODUIT_LAITIER,
            FoodGrade.G5_CUIT_SOUS_VIDE,
            60,
        ),
    ]

    return ingredients
