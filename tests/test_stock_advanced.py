from datetime import date, timedelta
from decimal import Decimal

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src" / "foodops_pro" / "domain"))
from stock_advanced import AdvancedStockLot, AdvancedStockManager, StockStatus


def test_consume_ingredient_fefo():
    manager = AdvancedStockManager()
    lot1 = AdvancedStockLot(
        ingredient_id="tomato",
        quantity=Decimal("10"),
        unit_cost_ht=Decimal("1.0"),
        purchase_date=date.today(),
        expiry_date=date.today() + timedelta(days=1),
        supplier_id="sup1",
    )
    lot2 = AdvancedStockLot(
        ingredient_id="tomato",
        quantity=Decimal("10"),
        unit_cost_ht=Decimal("1.0"),
        purchase_date=date.today(),
        expiry_date=date.today() + timedelta(days=5),
        supplier_id="sup1",
    )
    manager.add_lot(lot1)
    manager.add_lot(lot2)

    obtained, used = manager.consume_ingredient("tomato", Decimal("15"))
    assert obtained == Decimal("15")
    assert lot1.quantity == Decimal("0")
    assert lot2.quantity == Decimal("5")
    assert used[0].expiry_date <= used[1].expiry_date


def test_promotion_and_near_expiry_detection():
    manager = AdvancedStockManager()
    lot = AdvancedStockLot(
        ingredient_id="salad",
        quantity=Decimal("5"),
        unit_cost_ht=Decimal("2.0"),
        purchase_date=date.today() - timedelta(days=7),
        expiry_date=date.today() + timedelta(days=3),
        supplier_id="sup2",
    )
    manager.add_lot(lot)

    promos = manager.get_promotion_candidates()
    assert lot in promos
    near = manager.get_lots_near_expiry(warning_days=3)
    assert lot in near
    assert lot.status in {StockStatus.NEAR_EXPIRY, StockStatus.PROMOTION}


def test_process_daily_operations_handles_waste():
    manager = AdvancedStockManager()
    expired = AdvancedStockLot(
        ingredient_id="milk",
        quantity=Decimal("5"),
        unit_cost_ht=Decimal("1.5"),
        purchase_date=date.today() - timedelta(days=5),
        expiry_date=date.today() - timedelta(days=1),
        supplier_id="sup3",
    )
    fresh = AdvancedStockLot(
        ingredient_id="milk",
        quantity=Decimal("10"),
        unit_cost_ht=Decimal("1.5"),
        purchase_date=date.today() - timedelta(days=1),
        expiry_date=date.today() + timedelta(days=4),
        supplier_id="sup3",
        quality_degradation_rate=Decimal("0.1"),
    )
    manager.add_lot(expired)
    manager.add_lot(fresh)

    report = manager.process_daily_operations()
    assert report["expired_lots"] == 1
    assert report["degradation_losses"]["milk"] == Decimal("1")
    assert fresh.quantity == Decimal("9")
    assert all(lot.ingredient_id == "milk" for lot in manager.lots)
    assert len(manager.waste_records) == 2
