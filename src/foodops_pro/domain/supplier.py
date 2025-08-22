"""
Modèle des fournisseurs pour FoodOps Pro.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Optional
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
        min_order_quantity: Quantité minimale par commande
        max_order_quantity: Quantité maximale par commande
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
    min_order_quantity: Optional[Decimal] = None
    max_order_quantity: Optional[Decimal] = None
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
        if self.min_order_quantity is not None and self.min_order_quantity < 0:
            raise ValueError(
                f"La quantité minimale doit être positive: {self.min_order_quantity}"
            )
        if self.max_order_quantity is not None and self.max_order_quantity <= 0:
            raise ValueError(
                f"La quantité maximale doit être positive: {self.max_order_quantity}"
            )
        if (
            self.min_order_quantity is not None
            and self.max_order_quantity is not None
            and self.min_order_quantity > self.max_order_quantity
        ):
            raise ValueError("La quantité minimale ne peut dépasser la quantité maximale")
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

    def calculate_total_cost(self, order_value_ht: Decimal, quantity: Decimal) -> Decimal:
        """
        Calcule le coût total d'une commande incluant frais de port et remises.

        Args:
            order_value_ht: Valeur HT de la commande
            quantity: Quantité totale commandée

        Returns:
            Coût total HT
        """
        if order_value_ht < self.min_order_value:
            raise ValueError(
                f"Commande {order_value_ht} inférieure au MOQ {self.min_order_value}"
            )
        if self.min_order_quantity is not None and quantity < self.min_order_quantity:
            raise ValueError(
                f"Quantité {quantity} inférieure au minimum {self.min_order_quantity}"
            )
        if self.max_order_quantity is not None and quantity > self.max_order_quantity:
            raise ValueError(
                f"Quantité {quantity} supérieure au maximum {self.max_order_quantity}"
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

    def can_fulfill_order(self, order_value_ht: Decimal, quantity: Decimal) -> bool:
        """
        Vérifie si le fournisseur peut traiter une commande.

        Args:
            order_value_ht: Valeur HT de la commande
            quantity: Quantité totale

        Returns:
            True si la commande peut être traitée
        """
        if order_value_ht < self.min_order_value:
            return False
        if self.min_order_quantity is not None and quantity < self.min_order_quantity:
            return False
        if self.max_order_quantity is not None and quantity > self.max_order_quantity:
            return False
        return True

    def get_expected_delivery_date(self, order_date: date) -> date:
        """Calcule la date de livraison prévue en fonction du délai."""
        return order_date + timedelta(days=self.lead_time_days)

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
