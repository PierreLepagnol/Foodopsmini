"""
Achats & Réception (Procurement) pour FoodOps Pro.

- Planification des besoins à partir des recettes actives et des prévisions de ventes
- Proposition de commandes fournisseurs (arrondis aux packs, MOQ)
- Réception des commandes en StockLots (FEFO compatible)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from game_engine.domain.recipe import Recipe
from game_engine.domain.stock import StockLot, StockManager


@dataclass
class POLine:
    """Ligne d'un bon de commande fournisseur (support multi-fournisseurs/ingrédient)."""

    ingredient_id: str
    quantity: Decimal  # quantité commandée (unité catalogue, arrondie pack)
    unit_price_ht: Decimal  # prix unitaire HT catalogue
    vat_rate: Decimal  # taux de TVA
    supplier_id: str  # fournisseur choisi
    pack_size: Decimal  # taille du conditionnement
    # Métadonnées mercuriale / calculs
    pack_unit: str | None = None
    quality_level: int | None = None
    eta_days: int | None = None
    qty_rounded_pack: Decimal | None = None
    moq_ok: bool | None = None
    amount_ttc_estimated: Decimal | None = None
    # Réception / statut
    received_qty: Decimal = Decimal("0")
    accepted_qty: Decimal = Decimal("0")
    status: str = "OPEN"  # OPEN, PARTIAL, CLOSED

    def compute_amounts(self) -> None:
        """Calcule amount_ttc_estimated, qty_rounded_pack, moq_ok sur la ligne."""
        self.qty_rounded_pack = self.quantity
        self.moq_ok = True  # défini côté planner/UI lors des ajustements MOQ
        self.amount_ttc_estimated = (self.quantity * self.unit_price_ht) * (
            Decimal("1") + self.vat_rate
        )


@dataclass(frozen=True)
class PurchaseOrder:
    """Bon de commande simple."""

    supplier_id: str
    lines: list[POLine]
    created_on: date


@dataclass
class GoodsReceiptLine:
    ingredient_id: str
    qty_ordered: Decimal
    qty_delivered: Decimal
    qty_accepted: Decimal
    unit_price_ht: Decimal
    vat_rate: Decimal
    supplier_id: str
    pack_size: Decimal
    lots: list[StockLot]
    comment: str | None = None


@dataclass
class GoodsReceipt:
    date: date
    lines: list[GoodsReceiptLine]
    total_ht: Decimal
    total_ttc: Decimal
    status: str  # OPEN / PARTIAL / CLOSED


@dataclass(frozen=True)
class DeliveryLine:
    """Ligne de livraison (quantité effectivement reçue)."""

    ingredient_id: str
    quantity_received: Decimal
    unit_price_ht: Decimal
    vat_rate: Decimal
    supplier_id: str
    pack_size: Decimal
    lot_number: str | None = None
    quality_level: int | None = None  # 1..5


class ProcurementPlanner:
    """
    Calcule les besoins nets et propose des achats.
    """

    def compute_requirements(
        self,
        active_recipes: list[Recipe],
        sales_forecast: dict[str, int],  # recipe_id -> portions prévues
        stock: StockManager,
    ) -> dict[str, Decimal]:
        """
        Besoin brut = Σ (ventes prévues × qty_brute_par_portion)
        Besoin net = max(0, besoin_brut - stock_dispo_non_perime)
        """
        requirements: dict[str, Decimal] = {}

        # Agréger les besoins par ingrédient
        for recipe in active_recipes:
            forecast = Decimal(str(sales_forecast.get(recipe.id, 0)))
            if forecast <= 0:
                continue
            ratio = forecast / Decimal(str(recipe.portions))
            for item in recipe.items:
                qty = item.qty_brute * ratio
                requirements[item.ingredient_id] = (
                    requirements.get(item.ingredient_id, Decimal("0")) + qty
                )

        # Déduire le stock disponible non périmé
        net_requirements: dict[str, Decimal] = {}
        for ingredient_id, gross_need in requirements.items():
            available = stock.get_available_quantity(
                ingredient_id, exclude_expired=True
            )
            net = gross_need - available
            if net > 0:
                net_requirements[ingredient_id] = net

        return net_requirements

    def propose_purchase_orders(
        self,
        requirements: dict[str, Decimal],
        suppliers_catalog: dict[str, dict[str, dict[str, Decimal]]],
        # structure: ingredient_id -> supplier_id -> {"price_ht": Decimal, "vat": Decimal, "pack": Decimal, "moq_value": Decimal}
        safety_stock: dict[str, Decimal] | None = None,
    ) -> list[POLine]:
        """
        Propose des lignes d'achat optimisées par coût total (prix, pack, MOQ).
        """
        safety_stock = safety_stock or {}
        lines: list[POLine] = []

        for ingredient_id, need in requirements.items():
            target = need + safety_stock.get(ingredient_id, Decimal("0"))
            best: tuple[Decimal, POLine] | None = None  # (score, line)

            if ingredient_id not in suppliers_catalog:
                continue

            for supplier_id, offer in suppliers_catalog[ingredient_id].items():
                price = Decimal(str(offer.get("price_ht", 0)))
                vat = Decimal(str(offer.get("vat", 0.10)))
                pack = Decimal(str(offer.get("pack", 1)))
                moq_value = Decimal(str(offer.get("moq_value", 0)))
                lead_time = offer.get("lead_time_days")
                reliability = offer.get("reliability")

                packs_needed = (target / pack).to_integral_value(
                    rounding="ROUND_CEILING"
                )
                qty = packs_needed * pack
                order_value = qty * price

                if order_value < moq_value and price > 0:
                    deficit_value = moq_value - order_value
                    extra_qty = (deficit_value / price).to_integral_value(
                        rounding="ROUND_CEILING"
                    )
                    qty += extra_qty
                    order_value = qty * price

                line = POLine(
                    ingredient_id=ingredient_id,
                    quantity=qty,
                    unit_price_ht=price,
                    vat_rate=vat,
                    supplier_id=supplier_id,
                    pack_size=pack,
                )

                score = self._score_offer(qty, price, lead_time, reliability)
                if best is None or score < best[0]:
                    best = (score, line)

            if best:
                lines.append(best[1])

        return lines

    def _score_offer(
        self,
        qty: Decimal,
        price: Decimal,
        lead_time: int | None,
        reliability: Decimal | None,
    ) -> Decimal:
        """Score simple: valeur HT + pénalité délai - bonus fiabilité."""
        total_value = qty * price
        penalty = (
            Decimal(str(lead_time)) if lead_time is not None else Decimal("0")
        ) * Decimal("0.5")
        bonus = (
            Decimal(str(reliability)) if reliability is not None else Decimal("0")
        ) * Decimal("10")
        return total_value + penalty - bonus


class ReceivingService:
    """Conversion des livraisons en lots de stock (FEFO)."""

    def __init__(self, shelf_life_rules: dict[int, int] | None = None) -> None:
        # Ajustement DLUO par niveau de qualité (jours). Ex: {1: -2, 3: 0, 5: +2}
        self.shelf_life_rules = shelf_life_rules or {}

    def receive(
        self,
        deliveries: list[DeliveryLine],
        received_date: date,
        default_shelf_life_days: int = 5,
    ) -> list[StockLot]:
        """
        Convertit des DeliveryLine en StockLot en calculant une DLC.
        DLC = received_date + default_shelf_life +/- ajustement qualité.
        """
        lots: list[StockLot] = []
        for d in deliveries:
            adjust = self.shelf_life_rules.get(d.quality_level or 2, 0)
            dlc = received_date + timedelta(days=default_shelf_life_days + adjust)
            lot = StockLot(
                ingredient_id=d.ingredient_id,
                quantity=d.quantity_received,
                dlc=dlc,
                unit_cost_ht=d.unit_price_ht,
                vat_rate=d.vat_rate,
                supplier_id=d.supplier_id,
                received_date=received_date,
                lot_number=d.lot_number,
            )
            lots.append(lot)
        return lots
