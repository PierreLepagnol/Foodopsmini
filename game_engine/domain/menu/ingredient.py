"""
Modèle des ingrédients et système de qualité des ingrédients
"""

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class Ingredient(BaseModel):
    """
    Représente un ingrédient utilisé dans les recettes.

    Attributes:
        id: Identifiant unique de l'ingrédient
        name: Nom de l'ingrédient
        unit: Unité de mesure (kg, L, pièce, etc.)
        cost_ht: Coût d'achat hors taxes par unité
        vat_rate: Taux de TVA à l'achat (ex: 0.055 pour 5.5%)
        density: Densité pour conversions d'unités (optionnel)
        shelf_life_days: Durée de conservation en jours
        category: Catégorie (viande, légume, épice, etc.)
    """

    id: str
    name: str
    unit: str
    cost_ht: Decimal
    vat_rate: Decimal
    shelf_life_days: int
    category: str
    density: Decimal | None = None

    @property
    def cost_ttc(self) -> Decimal:
        """Coût TTC par unité."""
        return self.cost_ht * (1 + self.vat_rate)

    def convert_quantity(
        self, quantity: Decimal, from_unit: str, to_unit: str
    ) -> Decimal:
        """
        Convertit une quantité d'une unité vers une autre.

        Args:
            quantity: Quantité à convertir
            from_unit: Unité source
            to_unit: Unité cible

        Returns:
            Quantité convertie

        Raises:
            ValueError: Si la conversion n'est pas possible
        """
        if from_unit == to_unit:
            return quantity

        # Conversions simples supportées
        conversions = {
            ("kg", "g"): Decimal("1000"),
            ("g", "kg"): Decimal("0.001"),
            ("L", "mL"): Decimal("1000"),
            ("mL", "L"): Decimal("0.001"),
        }

        factor = conversions.get((from_unit, to_unit))
        if factor is not None:
            return quantity * factor

        # Conversion avec densité si disponible
        if self.density is not None:
            if from_unit == "L" and to_unit == "kg":
                return quantity * self.density
            elif from_unit == "kg" and to_unit == "L":
                return quantity / self.density

        raise ValueError(
            f"Conversion impossible de {from_unit} vers {to_unit} pour {self.name}"
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.cost_ht:.2f}€ HT/{self.unit})"


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


class QualityModifiers(BaseModel):
    """Modificateurs liés à la qualité d'un ingrédient."""

    cost_multiplier: Decimal  # Multiplicateur de coût (ex: 1.25 = +25%)
    satisfaction_bonus: Decimal  # Bonus satisfaction client (ex: 0.15 = +15%)
    prep_time_multiplier: Decimal  # Multiplicateur temps préparation
    shelf_life_multiplier: Decimal  # Multiplicateur DLC
    availability_seasonal: bool = False  # Disponibilité saisonnière

    def __post_init__(self):
        """
        Valide la cohérence des modificateurs de qualité.

        Raises:
            ValueError: Si un modificateur est négatif ou nul
        """
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
