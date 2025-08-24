"""
Modèle des fournisseurs pour FoodOps Pro.
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass(frozen=True)
class Supplier:
    """
    Représente un fournisseur d'ingrédients.

    Attributes:
        id: Identifiant unique du fournisseur
        name: Nom du fournisseur
        reliability: Fiabilité de livraison (0.0-1.0)
        lead_time_days: Délai de livraison en jours
        min_order_value: Montant minimum de commande (MOQ)
        shipping_cost: Frais de port fixes
        payment_terms_days: Délai de paiement en jours
        discount_threshold: Seuil pour remise quantité
        discount_rate: Taux de remise si seuil atteint
    """

    id: str
    name: str
    reliability: Decimal
    lead_time_days: int
    min_order_value: Decimal
    shipping_cost: Decimal
    payment_terms_days: int = 30
    discount_threshold: Optional[Decimal] = None
    discount_rate: Optional[Decimal] = None

    def __post_init__(self) -> None:
        """Validation des données."""
        if not (0 <= self.reliability <= 1):
            raise ValueError(f"La fiabilité doit être entre 0 et 1: {self.reliability}")
        if self.lead_time_days < 0:
            raise ValueError(
                f"Le délai de livraison doit être positif: {self.lead_time_days}"
            )
        if self.min_order_value < 0:
            raise ValueError(f"Le MOQ doit être positif: {self.min_order_value}")
        if self.shipping_cost < 0:
            raise ValueError(
                f"Les frais de port doivent être positifs: {self.shipping_cost}"
            )
        if self.payment_terms_days < 0:
            raise ValueError(
                f"Le délai de paiement doit être positif: {self.payment_terms_days}"
            )

        if self.discount_threshold is not None:
            if self.discount_threshold <= 0:
                raise ValueError(
                    f"Le seuil de remise doit être positif: {self.discount_threshold}"
                )
            if self.discount_rate is None or not (0 <= self.discount_rate <= 1):
                raise ValueError(
                    f"Le taux de remise doit être entre 0 et 1: {self.discount_rate}"
                )

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
