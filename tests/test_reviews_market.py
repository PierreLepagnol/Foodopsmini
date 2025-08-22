from decimal import Decimal

from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType
from src.foodops_pro.domain.scenario import Scenario, MarketSegment
from src.foodops_pro.core.market import MarketEngine
from src.foodops_pro.domain.review import ReviewManager


def test_reviews_influence_demand():
    segment = MarketSegment(
        name="test",
        share=Decimal("1"),
        budget=Decimal("10"),
        type_affinity={RestaurantType.FAST: Decimal("1")},
    )
    scenario = Scenario(
        name="s",
        description="",
        turns=1,
        base_demand=100,
        demand_noise=Decimal("0"),
        segments=[segment],
        random_seed=42,
    )
    market = MarketEngine(scenario, random_seed=42)
    r1 = Restaurant(
        id="r1",
        name="A",
        type=RestaurantType.FAST,
        capacity_base=100,
        speed_service=Decimal("1"),
        menu={"r": Decimal("10")},
        active_recipes=["r"],
    )
    r2 = Restaurant(
        id="r2",
        name="B",
        type=RestaurantType.FAST,
        capacity_base=100,
        speed_service=Decimal("1"),
        menu={"r": Decimal("10")},
        active_recipes=["r"],
    )
    r1.staffing_level = r2.staffing_level = 2

    before = market.allocate_demand([r1, r2], turn=1)
    assert before["r1"].allocated_demand == before["r2"].allocated_demand

    manager = ReviewManager()
    manager.add_review(r1, Decimal("5"))

    after = market.allocate_demand([r1, r2], turn=2)
    assert after["r1"].allocated_demand > after["r2"].allocated_demand
