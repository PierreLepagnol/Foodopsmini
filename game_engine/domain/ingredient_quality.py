"""
Système de qualité des ingrédients pour FoodOps Pro.
"""

from dataclasses import dataclass
from typing import Dict, List
from decimal import Decimal
from enum import Enum


class QualityLevel(Enum):
    """Niveaux de qualité des ingrédients."""

    ECONOMIQUE = 1  # ⭐ Surgelé industriel, conserves
    STANDARD = 2  # ⭐⭐ Frais classique, sous-vide
    SUPERIEUR = 3  # ⭐⭐⭐ Frais premium, origine contrôlée
    PREMIUM = 4  # ⭐⭐⭐⭐ Bio, Label Rouge, AOP
    LUXE = 5  # ⭐⭐⭐⭐⭐ Artisanal, terroir, exception


class IngredientRange(Enum):
    """Gammes d'ingrédients."""

    SURGELE = "surgelé"
    CONSERVE = "conserve"
    SOUS_VIDE = "sous_vide"
    FRAIS_IMPORT = "frais_import"
    FRAIS_LOCAL = "frais_local"
    BIO = "bio"
    LABEL_ROUGE = "label_rouge"
    AOP = "aop"
    ARTISANAL = "artisanal"
    TERROIR = "terroir"


@dataclass(frozen=True)
class QualityModifiers:
    """Modificateurs liés à la qualité d'un ingrédient."""

    cost_multiplier: Decimal  # Multiplicateur de coût (ex: 1.25 = +25%)
    satisfaction_bonus: Decimal  # Bonus satisfaction client (ex: 0.15 = +15%)
    prep_time_multiplier: Decimal  # Multiplicateur temps préparation
    shelf_life_multiplier: Decimal  # Multiplicateur DLC
    availability_seasonal: bool = False  # Disponibilité saisonnière

    def __post_init__(self):
        """Validation des modificateurs."""
        if self.cost_multiplier <= 0:
            raise ValueError(
                f"Le multiplicateur de coût doit être positif: {self.cost_multiplier}"
            )
        if self.prep_time_multiplier <= 0:
            raise ValueError(
                f"Le multiplicateur de temps doit être positif: {self.prep_time_multiplier}"
            )
        if self.shelf_life_multiplier <= 0:
            raise ValueError(
                f"Le multiplicateur de DLC doit être positif: {self.shelf_life_multiplier}"
            )


@dataclass(frozen=True)
class IngredientVariant:
    """
    Variante d'un ingrédient avec qualité et gamme spécifiques.

    Attributes:
        base_ingredient_id: ID de l'ingrédient de base
        quality_level: Niveau de qualité (1-5 étoiles)
        range_type: Type de gamme (surgelé, bio, etc.)
        supplier_id: Fournisseur spécialisé
        modifiers: Modificateurs de qualité
        description: Description de la variante
        certifications: Certifications (bio, label rouge, etc.)
    """

    base_ingredient_id: str
    quality_level: QualityLevel
    range_type: IngredientRange
    supplier_id: str
    modifiers: QualityModifiers
    description: str = ""
    certifications: List[str] = None

    def __post_init__(self):
        """Initialisation des certifications."""
        if self.certifications is None:
            object.__setattr__(self, "certifications", [])

    @property
    def id(self) -> str:
        """ID unique de la variante."""
        return f"{self.base_ingredient_id}_{self.range_type.value}_{self.quality_level.value}"

    @property
    def display_name(self) -> str:
        """Nom d'affichage avec qualité."""
        stars = "⭐" * self.quality_level.value
        return f"{self.description} {stars}"

    @property
    def quality_description(self) -> str:
        """Description de la qualité."""
        descriptions = {
            QualityLevel.ECONOMIQUE: "Économique - Rapport qualité/prix",
            QualityLevel.STANDARD: "Standard - Qualité classique",
            QualityLevel.SUPERIEUR: "Supérieur - Qualité premium",
            QualityLevel.PREMIUM: "Premium - Haute qualité certifiée",
            QualityLevel.LUXE: "Luxe - Excellence artisanale",
        }
        return descriptions[self.quality_level]

    def calculate_final_cost(self, base_cost: Decimal) -> Decimal:
        """Calcule le coût final avec modificateurs."""
        return base_cost * self.modifiers.cost_multiplier

    def calculate_prep_time(self, base_time: int) -> int:
        """Calcule le temps de préparation avec modificateurs."""
        return int(base_time * self.modifiers.prep_time_multiplier)

    def calculate_shelf_life(self, base_shelf_life: int) -> int:
        """Calcule la DLC avec modificateurs."""
        return int(base_shelf_life * self.modifiers.shelf_life_multiplier)


# Définitions des modificateurs par niveau de qualité
QUALITY_MODIFIERS = {
    QualityLevel.ECONOMIQUE: QualityModifiers(
        cost_multiplier=Decimal("0.70"),  # -30%
        satisfaction_bonus=Decimal("-0.20"),  # -20%
        prep_time_multiplier=Decimal("0.85"),  # -15% (pré-coupé)
        shelf_life_multiplier=Decimal("2.0"),  # +100% (surgelé)
    ),
    QualityLevel.STANDARD: QualityModifiers(
        cost_multiplier=Decimal("1.00"),  # Prix de référence
        satisfaction_bonus=Decimal("0.00"),  # Neutre
        prep_time_multiplier=Decimal("1.00"),  # Standard
        shelf_life_multiplier=Decimal("1.0"),  # Standard
    ),
    QualityLevel.SUPERIEUR: QualityModifiers(
        cost_multiplier=Decimal("1.25"),  # +25%
        satisfaction_bonus=Decimal("0.15"),  # +15%
        prep_time_multiplier=Decimal("1.10"),  # +10%
        shelf_life_multiplier=Decimal("0.9"),  # -10% (plus frais)
    ),
    QualityLevel.PREMIUM: QualityModifiers(
        cost_multiplier=Decimal("1.50"),  # +50%
        satisfaction_bonus=Decimal("0.30"),  # +30%
        prep_time_multiplier=Decimal("1.20"),  # +20%
        shelf_life_multiplier=Decimal("0.8"),  # -20% (très frais)
    ),
    QualityLevel.LUXE: QualityModifiers(
        cost_multiplier=Decimal("2.00"),  # +100%
        satisfaction_bonus=Decimal("0.50"),  # +50%
        prep_time_multiplier=Decimal("1.30"),  # +30%
        shelf_life_multiplier=Decimal("0.7"),  # -30% (ultra frais)
    ),
}


class IngredientQualityManager:
    """Gestionnaire du système de qualité des ingrédients."""

    def __init__(self):
        self.variants: Dict[str, IngredientVariant] = {}
        self._load_default_variants()

    def _load_default_variants(self):
        """Charge les variantes par défaut."""
        # Exemples de variantes pour le steak haché
        self.add_variant(
            IngredientVariant(
                base_ingredient_id="beef_ground",
                quality_level=QualityLevel.ECONOMIQUE,
                range_type=IngredientRange.SURGELE,
                supplier_id="davigel",
                modifiers=QUALITY_MODIFIERS[QualityLevel.ECONOMIQUE],
                description="Steak haché surgelé",
                certifications=[],
            )
        )

        self.add_variant(
            IngredientVariant(
                base_ingredient_id="beef_ground",
                quality_level=QualityLevel.STANDARD,
                range_type=IngredientRange.FRAIS_IMPORT,
                supplier_id="metro_pro",
                modifiers=QUALITY_MODIFIERS[QualityLevel.STANDARD],
                description="Steak haché frais",
                certifications=[],
            )
        )

        self.add_variant(
            IngredientVariant(
                base_ingredient_id="beef_ground",
                quality_level=QualityLevel.PREMIUM,
                range_type=IngredientRange.BIO,
                supplier_id="bio_france",
                modifiers=QUALITY_MODIFIERS[QualityLevel.PREMIUM],
                description="Steak haché bio",
                certifications=["AB", "Origine France"],
            )
        )

        # Exemples pour les tomates
        self.add_variant(
            IngredientVariant(
                base_ingredient_id="tomato",
                quality_level=QualityLevel.ECONOMIQUE,
                range_type=IngredientRange.CONSERVE,
                supplier_id="metro_pro",
                modifiers=QUALITY_MODIFIERS[QualityLevel.ECONOMIQUE],
                description="Tomates en conserve",
                certifications=[],
            )
        )

        self.add_variant(
            IngredientVariant(
                base_ingredient_id="tomato",
                quality_level=QualityLevel.LUXE,
                range_type=IngredientRange.TERROIR,
                supplier_id="local_farm",
                modifiers=QUALITY_MODIFIERS[QualityLevel.LUXE],
                description="Tomates du terroir",
                certifications=["Producteur local", "Variété ancienne"],
            )
        )

    def add_variant(self, variant: IngredientVariant):
        """Ajoute une variante d'ingrédient."""
        self.variants[variant.id] = variant

    def get_variants_for_ingredient(
        self, base_ingredient_id: str
    ) -> List[IngredientVariant]:
        """Retourne toutes les variantes d'un ingrédient de base."""
        return [
            v
            for v in self.variants.values()
            if v.base_ingredient_id == base_ingredient_id
        ]

    def get_variants_by_supplier(self, supplier_id: str) -> List[IngredientVariant]:
        """Retourne toutes les variantes d'un fournisseur."""
        return [v for v in self.variants.values() if v.supplier_id == supplier_id]

    def get_variants_by_quality(
        self, quality_level: QualityLevel
    ) -> List[IngredientVariant]:
        """Retourne toutes les variantes d'un niveau de qualité."""
        return [v for v in self.variants.values() if v.quality_level == quality_level]

    def calculate_recipe_quality_score(
        self, ingredient_variants: Dict[str, IngredientVariant]
    ) -> Decimal:
        """
        Calcule le score de qualité d'une recette basé sur ses ingrédients.

        Args:
            ingredient_variants: Dict {ingredient_id: variant}

        Returns:
            Score de qualité moyen pondéré (1.0 à 5.0)
        """
        if not ingredient_variants:
            return Decimal("2.0")  # Standard par défaut

        total_score = Decimal("0")
        for variant in ingredient_variants.values():
            total_score += Decimal(str(variant.quality_level.value))

        return total_score / Decimal(str(len(ingredient_variants)))

    def get_quality_impact_on_attractiveness(self, quality_score: Decimal) -> Decimal:
        """
        Calcule l'impact du score de qualité sur l'attractivité.

        Args:
            quality_score: Score de qualité (1.0 à 5.0)

        Returns:
            Multiplicateur d'attractivité
        """
        if quality_score <= 1.5:
            return Decimal("0.80")  # -20%
        elif quality_score <= 2.5:
            return Decimal("1.00")  # Neutre
        elif quality_score <= 3.5:
            return Decimal("1.15")  # +15%
        elif quality_score <= 4.5:
            return Decimal("1.30")  # +30%
        else:
            return Decimal("1.50")  # +50%
