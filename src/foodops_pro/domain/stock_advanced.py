"""
Système de gestion des stocks avancé pour FoodOps Pro avec FEFO.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import date, timedelta
from enum import Enum


class StockStatus(Enum):
    """Statut d'un lot de stock."""

    FRESH = "frais"
    NEAR_EXPIRY = "proche_expiration"
    EXPIRED = "expire"
    PROMOTION = "promotion"


class WasteReason(Enum):
    """Raisons de perte de stock."""

    EXPIRY = "expiration"
    DAMAGE = "deterioration"
    THEFT = "vol"
    PREPARATION_LOSS = "perte_preparation"


@dataclass
class AdvancedStockLot:
    """
    Lot de stock avancé avec gestion de la qualité et des pertes.

    Attributes:
        ingredient_id: Identifiant de l'ingrédient
        variant_id: ID de la variante qualité (optionnel)
        quantity: Quantité en stock
        unit_cost_ht: Coût unitaire HT d'achat
        purchase_date: Date d'achat
        expiry_date: Date de péremption
        supplier_id: Fournisseur d'origine
        lot_number: Numéro de lot (optionnel)
        quality_degradation_rate: Taux de dégradation par jour
    """

    ingredient_id: str
    quantity: Decimal
    unit_cost_ht: Decimal
    purchase_date: date
    expiry_date: date
    supplier_id: str
    variant_id: Optional[str] = None
    lot_number: Optional[str] = None
    quality_degradation_rate: Decimal = Decimal("0.01")  # 1% par jour par défaut

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.quantity < 0:
            raise ValueError(f"La quantité doit être positive: {self.quantity}")
        if self.unit_cost_ht < 0:
            raise ValueError(f"Le coût unitaire doit être positif: {self.unit_cost_ht}")
        if self.expiry_date <= self.purchase_date:
            raise ValueError(
                "La date de péremption doit être postérieure à la date d'achat"
            )
        if not (0 <= self.quality_degradation_rate <= 1):
            raise ValueError(
                f"Le taux de dégradation doit être entre 0 et 1: {self.quality_degradation_rate}"
            )

    @property
    def total_value_ht(self) -> Decimal:
        """Valeur totale HT du lot."""
        return self.quantity * self.unit_cost_ht

    @property
    def days_until_expiry(self) -> int:
        """Nombre de jours avant péremption."""
        return (self.expiry_date - date.today()).days

    @property
    def shelf_life_percentage(self) -> Decimal:
        """Pourcentage de durée de vie restante."""
        total_days = (self.expiry_date - self.purchase_date).days
        remaining_days = max(0, self.days_until_expiry)
        return (
            Decimal(remaining_days) / Decimal(total_days)
            if total_days > 0
            else Decimal("0")
        )

    @property
    def status(self) -> StockStatus:
        """Statut actuel du lot."""
        if self.is_expired:
            return StockStatus.EXPIRED
        elif self.is_near_expiry():
            return StockStatus.NEAR_EXPIRY
        elif self.is_promotion_candidate():
            return StockStatus.PROMOTION
        else:
            return StockStatus.FRESH

    @property
    def is_expired(self) -> bool:
        """Vérifie si le lot est périmé."""
        return date.today() > self.expiry_date

    def is_near_expiry(self, warning_days: int = 2) -> bool:
        """Vérifie si le lot approche de la péremption."""
        return 0 <= self.days_until_expiry <= warning_days

    def is_promotion_candidate(
        self, promotion_threshold: Decimal = Decimal("0.3")
    ) -> bool:
        """Vérifie si le lot est candidat à une promotion."""
        return self.shelf_life_percentage <= promotion_threshold

    def calculate_daily_loss(self) -> Decimal:
        """Calcule la perte quotidienne selon l'âge du produit."""
        if self.is_expired:
            return self.quantity  # Perte totale si expiré

        # Perte accélérée après 50% de la durée de vie
        if self.shelf_life_percentage < Decimal("0.5"):
            accelerated_rate = self.quality_degradation_rate * Decimal("2")
            return min(self.quantity * accelerated_rate, self.quantity)

        return self.quantity * self.quality_degradation_rate

    def consume(self, quantity: Decimal) -> Decimal:
        """
        Consomme une quantité du lot.

        Args:
            quantity: Quantité à consommer

        Returns:
            Quantité effectivement consommée
        """
        if quantity < 0:
            raise ValueError(f"La quantité à consommer doit être positive: {quantity}")

        consumed = min(quantity, self.quantity)
        self.quantity -= consumed
        return consumed

    def apply_daily_degradation(self) -> Decimal:
        """Applique la dégradation quotidienne et retourne la quantité perdue."""
        loss = self.calculate_daily_loss()
        self.quantity = max(Decimal("0"), self.quantity - loss)
        return loss

    def get_promotion_price(
        self, base_price: Decimal, discount_rate: Decimal = Decimal("0.5")
    ) -> Decimal:
        """Calcule le prix de promotion pour écouler le stock."""
        return base_price * (Decimal("1") - discount_rate)


@dataclass
class WasteRecord:
    """Enregistrement d'une perte de stock."""

    ingredient_id: str
    quantity_lost: Decimal
    unit_cost_ht: Decimal
    waste_date: date
    reason: WasteReason
    lot_number: Optional[str] = None

    @property
    def total_loss_value(self) -> Decimal:
        """Valeur totale de la perte."""
        return self.quantity_lost * self.unit_cost_ht


class AdvancedStockManager:
    """Gestionnaire avancé des stocks avec FEFO."""

    def __init__(self):
        self.lots: List[AdvancedStockLot] = []
        self.waste_records: List[WasteRecord] = []
        self.reorder_points: Dict[str, Decimal] = {}  # Seuils de réapprovisionnement
        self.max_stock_levels: Dict[str, Decimal] = {}  # Niveaux max de stock

    def add_lot(self, lot: AdvancedStockLot) -> None:
        """Ajoute un lot au stock."""
        self.lots.append(lot)
        self._sort_lots_by_expiry()

    def _sort_lots_by_expiry(self) -> None:
        """Trie les lots par date d'expiration (FEFO)."""
        self.lots.sort(key=lambda lot: lot.expiry_date)

    def get_available_quantity(
        self, ingredient_id: str, exclude_expired: bool = True
    ) -> Decimal:
        """Retourne la quantité disponible d'un ingrédient."""
        total = Decimal("0")
        for lot in self.lots:
            if lot.ingredient_id == ingredient_id:
                if not exclude_expired or not lot.is_expired:
                    total += lot.quantity
        return total

    def consume_ingredient(
        self, ingredient_id: str, quantity_needed: Decimal
    ) -> Tuple[Decimal, List[AdvancedStockLot]]:
        """
        Consomme un ingrédient selon la méthode FEFO.

        Args:
            ingredient_id: ID de l'ingrédient
            quantity_needed: Quantité nécessaire

        Returns:
            Tuple (quantité_obtenue, lots_utilisés)
        """
        quantity_obtained = Decimal("0")
        lots_used = []

        # Trier par date d'expiration (FEFO)
        ingredient_lots = [
            lot
            for lot in self.lots
            if lot.ingredient_id == ingredient_id and not lot.is_expired
        ]
        ingredient_lots.sort(key=lambda lot: lot.expiry_date)

        for lot in ingredient_lots:
            if quantity_obtained >= quantity_needed:
                break

            remaining_needed = quantity_needed - quantity_obtained
            consumed = lot.consume(remaining_needed)
            quantity_obtained += consumed

            if consumed > 0:
                lots_used.append(lot)

        # Nettoyer les lots vides
        self.lots = [lot for lot in self.lots if lot.quantity > 0]

        return quantity_obtained, lots_used

    def process_daily_operations(self) -> Dict[str, any]:
        """
        Traite les opérations quotidiennes (dégradation, expirations).

        Returns:
            Rapport des opérations
        """
        total_waste_value = Decimal("0")
        expired_lots = []
        degradation_losses = {}

        for lot in self.lots[:]:  # Copie pour modification sûre
            # Vérifier expiration
            if lot.is_expired:
                expired_lots.append(lot)
                waste_record = WasteRecord(
                    ingredient_id=lot.ingredient_id,
                    quantity_lost=lot.quantity,
                    unit_cost_ht=lot.unit_cost_ht,
                    waste_date=date.today(),
                    reason=WasteReason.EXPIRY,
                    lot_number=lot.lot_number,
                )
                self.waste_records.append(waste_record)
                total_waste_value += waste_record.total_loss_value
                self.lots.remove(lot)
                continue

            # Appliquer dégradation
            daily_loss = lot.apply_daily_degradation()
            if daily_loss > 0:
                if lot.ingredient_id not in degradation_losses:
                    degradation_losses[lot.ingredient_id] = Decimal("0")
                degradation_losses[lot.ingredient_id] += daily_loss

                waste_record = WasteRecord(
                    ingredient_id=lot.ingredient_id,
                    quantity_lost=daily_loss,
                    unit_cost_ht=lot.unit_cost_ht,
                    waste_date=date.today(),
                    reason=WasteReason.DAMAGE,
                    lot_number=lot.lot_number,
                )
                self.waste_records.append(waste_record)
                total_waste_value += waste_record.total_loss_value

        return {
            "expired_lots": len(expired_lots),
            "total_waste_value": total_waste_value,
            "degradation_losses": degradation_losses,
            "lots_near_expiry": self.get_lots_near_expiry(),
            "promotion_candidates": self.get_promotion_candidates(),
        }

    def get_lots_near_expiry(self, warning_days: int = 2) -> List[AdvancedStockLot]:
        """Retourne les lots proches de l'expiration."""
        return [lot for lot in self.lots if lot.is_near_expiry(warning_days)]

    def get_promotion_candidates(self) -> List[AdvancedStockLot]:
        """Retourne les lots candidats à une promotion."""
        return [lot for lot in self.lots if lot.is_promotion_candidate()]

    def get_reorder_alerts(self) -> List[str]:
        """Retourne les ingrédients nécessitant un réapprovisionnement."""
        alerts = []

        for ingredient_id, reorder_point in self.reorder_points.items():
            current_stock = self.get_available_quantity(ingredient_id)
            if current_stock <= reorder_point:
                alerts.append(ingredient_id)

        return alerts

    def set_reorder_point(self, ingredient_id: str, quantity: Decimal) -> None:
        """Définit le seuil de réapprovisionnement."""
        self.reorder_points[ingredient_id] = quantity

    def get_stock_rotation_analysis(self, ingredient_id: str) -> Dict[str, any]:
        """Analyse la rotation des stocks pour un ingrédient."""
        ingredient_lots = [
            lot for lot in self.lots if lot.ingredient_id == ingredient_id
        ]

        if not ingredient_lots:
            return {"average_age": 0, "oldest_lot_days": 0, "rotation_rate": "N/A"}

        total_age = sum(
            (date.today() - lot.purchase_date).days for lot in ingredient_lots
        )
        average_age = total_age / len(ingredient_lots)
        oldest_lot_days = max(
            (date.today() - lot.purchase_date).days for lot in ingredient_lots
        )

        # Calcul simplifié du taux de rotation
        total_quantity = sum(lot.quantity for lot in ingredient_lots)

        return {
            "average_age": average_age,
            "oldest_lot_days": oldest_lot_days,
            "total_quantity": total_quantity,
            "lots_count": len(ingredient_lots),
            "near_expiry_count": len(
                [lot for lot in ingredient_lots if lot.is_near_expiry()]
            ),
        }
