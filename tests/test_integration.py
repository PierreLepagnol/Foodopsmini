"""Tests d'intégration pour le gestionnaire de sauvegarde."""

from decimal import Decimal

from src.foodops_pro.io.save_manager import SaveManager
from src.foodops_pro.domain.restaurant import Restaurant
from src.foodops_pro.domain.scenario import Scenario, MarketSegment


def test_save_and_load_cycle(tmp_path):
    save_dir = tmp_path / "saves"
    manager = SaveManager(save_directory=str(save_dir))

    restaurant = Restaurant(
        id="r1",
        name="Resto",
        type="fast",
        capacity_base=50,
        speed_service=Decimal("1.0"),
        quality_manager=None,
    )

    segment = MarketSegment(
        name="grand public",
        share=Decimal("1.0"),
        budget=Decimal("10"),
        type_affinity={"fast": Decimal("1.0")},
    )

    scenario = Scenario(
        name="demo",
        description="",
        turns=1,
        base_demand=100,
        demand_noise=Decimal("0"),
        segments=[segment],
    )

    game_data = {
        "restaurants": [restaurant],
        "scenario": scenario,
        "current_turn": 1,
        "total_turns": 1,
        "scenario_name": scenario.name,
    }

    save_name = manager.save_game(game_data, save_name="demo")
    loaded = manager.load_game(save_name)

    assert isinstance(loaded["restaurants"][0], Restaurant)
    assert loaded["restaurants"][0].name == restaurant.name
    assert isinstance(loaded["scenario"], Scenario)
    assert loaded["scenario"].name == scenario.name
