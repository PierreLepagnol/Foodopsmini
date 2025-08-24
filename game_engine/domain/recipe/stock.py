"""
Modèle de gestion des stocks
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class StockLot:
    """
    Représente un lot de stock d'un ingrédient avec sa DLC.

    Attributes:
        ingredient_id: ID de l'ingrédient
        quantity: Quantité disponible
        dlc: Date limite de consommation
        unit_cost_ht: Coût unitaire HT du lot
        vat_rate: Taux de TVA du lot
        supplier_id: ID du fournisseur
        received_date: Date de réception
        lot_number: Numéro de lot (optionnel)
    """

    ingredient_id: str
    quantity: Decimal
    dlc: date
    unit_cost_ht: Decimal
    vat_rate: Decimal
    supplier_id: str
    received_date: date
    lot_number: str | None = None

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.quantity < 0:
            raise ValueError(f"La quantité doit être positive: {self.quantity}")
        if self.unit_cost_ht < 0:
            raise ValueError(f"Le coût unitaire doit être positif: {self.unit_cost_ht}")
        if not (0 <= self.vat_rate <= 1):
            raise ValueError(f"Le taux de TVA doit être entre 0 et 1: {self.vat_rate}")
        if self.dlc < self.received_date:
            raise ValueError(
                "La DLC ne peut pas être antérieure à la date de réception"
            )

    @property
    def is_expired(self) -> bool:
        """Vérifie si le lot est périmé."""
        return date.today() > self.dlc

    @property
    def days_until_expiry(self) -> int:
        """Nombre de jours avant expiration."""
        return (self.dlc - date.today()).days

    @property
    def total_value_ht(self) -> Decimal:
        """Valeur totale HT du lot."""
        return self.quantity * self.unit_cost_ht

    @property
    def total_value_ttc(self) -> Decimal:
        """Valeur totale TTC du lot."""
        return self.total_value_ht * (1 + self.vat_rate)

    def consume(self, quantity: Decimal) -> Decimal:
        """
        Consomme une quantité du lot.

        Args:
            quantity: Quantité à consommer

        Returns:
            Quantité effectivement consommée

        Raises:
            ValueError: Si la quantité est négative
        """
        if quantity < 0:
            raise ValueError("La quantité à consommer doit être positive")

        consumed = min(quantity, self.quantity)
        self.quantity -= consumed
        return consumed

    def is_near_expiry(self, warning_days: int = 3) -> bool:
        """
        Vérifie si le lot approche de sa date d'expiration.

        Args:
            warning_days: Nombre de jours avant expiration pour l'alerte

        Returns:
            True si le lot expire bientôt
        """
        return 0 <= self.days_until_expiry <= warning_days

    def __str__(self) -> str:
        status = "PÉRIMÉ" if self.is_expired else f"DLC: {self.dlc}"
        return f"Lot {self.ingredient_id}: {self.quantity} unités ({status})"


class StockManager:
    """
    Gestionnaire de stock implémentant la méthode FEFO (First Expired, First Out).
    """

    def __init__(self) -> None:
        self.lots: list[StockLot] = []

    def add_lot(self, lot: StockLot) -> None:
        """Ajoute un lot au stock."""
        self.lots.append(lot)
        # Tri par DLC pour FEFO
        self.lots.sort(key=lambda x: x.dlc)

    def get_available_quantity(
        self, ingredient_id: str, exclude_expired: bool = True
    ) -> Decimal:
        """
        Retourne la quantité disponible d'un ingrédient.

        Args:
            ingredient_id: ID de l'ingrédient
            exclude_expired: Exclure les lots périmés

        Returns:
            Quantité totale disponible
        """
        total = Decimal("0")
        for lot in self.lots:
            if lot.ingredient_id == ingredient_id:
                if not exclude_expired or not lot.is_expired:
                    total += lot.quantity
        return total

    def consume_ingredient(
        self, ingredient_id: str, quantity: Decimal
    ) -> list[StockLot]:
        """
        Consomme une quantité d'ingrédient selon FEFO.

        Args:
            ingredient_id: ID de l'ingrédient
            quantity: Quantité à consommer

        Returns:
            Liste des lots utilisés avec quantités consommées

        Raises:
            ValueError: Si pas assez de stock disponible
        """
        available = self.get_available_quantity(ingredient_id, exclude_expired=True)
        if quantity > available:
            raise ValueError(
                f"Stock insuffisant pour {ingredient_id}: {quantity} demandé, {available} disponible"
            )

        remaining = quantity
        used_lots = []

        # Tri par DLC (FEFO)
        ingredient_lots = [
            lot
            for lot in self.lots
            if lot.ingredient_id == ingredient_id and not lot.is_expired
        ]
        ingredient_lots.sort(key=lambda x: x.dlc)

        for lot in ingredient_lots:
            if remaining <= 0:
                break

            consumed = lot.consume(remaining)
            if consumed > 0:
                # Créer un lot représentant ce qui a été consommé
                consumed_lot = StockLot(
                    ingredient_id=lot.ingredient_id,
                    quantity=consumed,
                    dlc=lot.dlc,
                    unit_cost_ht=lot.unit_cost_ht,
                    vat_rate=lot.vat_rate,
                    supplier_id=lot.supplier_id,
                    received_date=lot.received_date,
                    lot_number=lot.lot_number,
                )
                used_lots.append(consumed_lot)
                remaining -= consumed

        # Nettoyer les lots vides
        self.lots = [lot for lot in self.lots if lot.quantity > 0]

        return used_lots

    def get_expiring_lots(self, days: int = 3) -> list[StockLot]:
        """
        Retourne les lots qui expirent dans les prochains jours.

        Args:
            days: Nombre de jours pour l'alerte

        Returns:
            Liste des lots qui expirent bientôt
        """
        return [lot for lot in self.lots if lot.is_near_expiry(days)]

    def remove_expired_lots(self) -> list[StockLot]:
        """
        Supprime les lots périmés du stock.

        Returns:
            Liste des lots supprimés
        """
        expired = [lot for lot in self.lots if lot.is_expired]
        self.lots = [lot for lot in self.lots if not lot.is_expired]
        return expired

    def get_stock_value(self, ingredient_id: str | None = None) -> Decimal:
        """
        Calcule la valeur totale du stock.

        Args:
            ingredient_id: ID d'un ingrédient spécifique (optionnel)

        Returns:
            Valeur totale HT du stock
        """
        total = Decimal("0")
        for lot in self.lots:
            if ingredient_id is None or lot.ingredient_id == ingredient_id:
                if not lot.is_expired:
                    total += lot.total_value_ht
        return total
