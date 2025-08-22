from decimal import Decimal
from datetime import date
import pytest

from src.foodops_pro.domain.supplier import Supplier


def test_supplier_quantity_and_lead_time():
    supplier = Supplier(
        id="s1",
        name="Fournisseur",
        reliability=Decimal("0.9"),
        lead_time_days=2,
        min_order_value=Decimal("100"),
        min_order_quantity=Decimal("5"),
        max_order_quantity=Decimal("20"),
        shipping_cost=Decimal("10"),
    )

    # Quantity below minimum
    with pytest.raises(ValueError):
        supplier.calculate_total_cost(Decimal("120"), Decimal("2"))

    # Quantity above maximum
    with pytest.raises(ValueError):
        supplier.calculate_total_cost(Decimal("500"), Decimal("25"))

    # Valid order
    total = supplier.calculate_total_cost(Decimal("150"), Decimal("10"))
    assert total == Decimal("160")  # 150 + shipping 10

    # Lead time
    delivery = supplier.get_expected_delivery_date(date(2024, 1, 1))
    assert delivery == date(2024, 1, 3)
