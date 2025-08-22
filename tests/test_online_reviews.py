from decimal import Decimal
from foodops_pro.domain.restaurant import Restaurant, RestaurantType


def test_online_review_average():
    r = Restaurant(id="r1", name="R", type=RestaurantType.FAST, capacity_base=50, speed_service=Decimal("1.0"))
    r.add_online_review(Decimal("4"))
    r.add_online_review(Decimal("5"))
    assert r.average_review == Decimal("4.5")
