from decimal import Decimal

from src.foodops_pro.domain.scenario import Scenario, MarketSegment
from src.foodops_pro.domain.restaurant import RestaurantType


def test_total_demand_scales_with_players():
    segment = MarketSegment(
        name="Unique",
        share=Decimal("1.0"),
        budget=Decimal("10"),
        type_affinity={RestaurantType.FAST: Decimal("1.0")},
    )
    scenario = Scenario(
        name="Test",
        description="",
        turns=1,
        base_demand=100,
        days_per_turn=2,
        demand_noise=Decimal("0"),
        segments=[segment],
    )

    demand_one = scenario.calculate_total_demand(turn=1, month=1, players_count=1)
    demand_two = scenario.calculate_total_demand(turn=1, month=1, players_count=2)

    assert demand_one == 200
    assert demand_two == 400
    assert demand_two == demand_one * 2
