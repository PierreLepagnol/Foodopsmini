from decimal import Decimal

from src.foodops_pro.domain.scenario import Scenario, MarketSegment
from src.foodops_pro.domain.restaurant import RestaurantType


def test_total_demand_scales_with_players():
    segment = MarketSegment(
        name="Unique",
        share=Decimal("1.0"),
        budget=Decimal("10"),
        type_affinity={RestaurantType.CLASSIC: Decimal("1.0")},
    )
    scenario = Scenario(
        name="scale",
        description="",
        turns=1,
        days_per_turn=7,
        base_demand=20,
        demand_noise=Decimal("0"),
        segments=[segment],
    )

    demand_one = scenario.calculate_total_demand(1, players_count=1)
    demand_three = scenario.calculate_total_demand(1, players_count=3)

    assert demand_one * 3 == demand_three
