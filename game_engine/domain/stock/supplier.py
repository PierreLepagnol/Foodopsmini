"""Modèle des fournisseurs"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class Supplier(BaseModel):
    """Représente un fournisseur d'ingrédients."""

    id: str
    name: str
    reliability: Decimal = Field(
        ge=0, le=1, description="Fiabilité de livraison (0.0-1.0)"
    )
    lead_time_days: int = Field(ge=0, description="Délai de livraison en jours")
    min_order_value: Decimal = Field(
        ge=0, description="Montant minimum de commande (MOQ)"
    )
    shipping_cost: Decimal = Field(ge=0, description="Frais de port fixes")
    payment_terms_days: int = Field(
        default=30, ge=0, description="Délai de paiement en jours"
    )
    discount_threshold: Optional[Decimal] = Field(
        default=None, gt=0, description="Seuil pour remise quantité"
    )
    discount_rate: Optional[Decimal] = Field(
        default=None, ge=0, le=1, description="Taux de remise si seuil atteint"
    )

    @model_validator(mode="after")
    def validate_discount_coherence(self):
        """Valide la cohérence entre seuil et taux de remise."""
        if self.discount_threshold is not None and self.discount_rate is None:
            raise ValueError(
                "Le taux de remise doit être défini si un seuil de remise est spécifié"
            )
        if self.discount_rate is not None and self.discount_threshold is None:
            raise ValueError(
                "Le seuil de remise doit être défini si un taux de remise est spécifié"
            )
        return self

    def calculate_total_cost(self, order_value_ht: Decimal) -> Decimal:
        """
        Calcule le coût total d'une commande incluant frais de port et remises.

        Args:
            order_value_ht: Valeur HT de la commande

        Returns:
            Coût total HT
        """
        if order_value_ht < self.min_order_value:
            raise ValueError(
                f"Commande {order_value_ht} inférieure au MOQ {self.min_order_value}"
            )

        # Application de la remise si applicable
        discounted_value = order_value_ht
        if (
            self.discount_threshold is not None
            and self.discount_rate is not None
            and order_value_ht >= self.discount_threshold
        ):
            discounted_value = order_value_ht * (1 - self.discount_rate)

        return discounted_value + self.shipping_cost

    def can_fulfill_order(self, order_value_ht: Decimal) -> bool:
        """
        Vérifie si le fournisseur peut traiter une commande.

        Args:
            order_value_ht: Valeur HT de la commande

        Returns:
            True si la commande peut être traitée
        """
        return order_value_ht >= self.min_order_value

    def get_delivery_risk(self) -> str:
        """
        Retourne le niveau de risque de livraison.

        Returns:
            Niveau de risque ("faible", "moyen", "élevé")
        """
        if self.reliability >= Decimal("0.95"):
            return "faible"
        elif self.reliability >= Decimal("0.85"):
            return "moyen"
        else:
            return "élevé"

    def __str__(self) -> str:
        return f"{self.name} (fiabilité: {self.reliability:.1%}, délai: {self.lead_time_days}j)"
