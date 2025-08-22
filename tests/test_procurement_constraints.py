from decimal import Decimal
from foodops_pro.core.procurement import ProcurementPlanner


def test_purchase_order_min_max_qty_and_delay():
    planner = ProcurementPlanner()
    requirements = {"ing1": Decimal("5")}
    catalog = {
        "ing1": {
            "sup1": {
                "price_ht": Decimal("1"),
                "vat": Decimal("0.1"),
                "pack": Decimal("1"),
                "lead_time_days": 3,
                "min_qty": Decimal("10"),
                "max_qty": Decimal("20"),
            }
        }
    }
    lines = planner.propose_purchase_orders(requirements, catalog)
    assert len(lines) == 1
    line = lines[0]
    assert line.quantity == Decimal("10")  # respect min_qty
    assert line.min_qty == Decimal("10") and line.max_qty == Decimal("20")
    assert line.eta_days == 3 and line.expected_delivery is not None
