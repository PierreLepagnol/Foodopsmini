"""
Modèle des ingrédients
"""

from decimal import Decimal

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
