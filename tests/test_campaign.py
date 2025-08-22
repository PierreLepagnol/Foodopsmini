"""Tests du gestionnaire de campagne."""

from decimal import Decimal
from pathlib import Path

from src.foodops_pro.domain.scenario import Scenario, MarketSegment
from src.foodops_pro.domain.restaurant import RestaurantType
from src.foodops_pro.domain.campaign import CampaignManager
from src.foodops_pro.io.persistence import CampaignPersistence


def _make_scenario(name: str) -> Scenario:
    segment = MarketSegment(
        name="Unique",
        share=Decimal("1.0"),
        budget=Decimal("10"),
        type_affinity={RestaurantType.CLASSIC: Decimal("1.0")},
    )
    return Scenario(
        name=name,
        description="",
        turns=1,
        days_per_turn=1,
        base_demand=100,
        demand_noise=Decimal("0"),
        segments=[segment],
    )


def test_campaign_progress_persistence(tmp_path: Path) -> None:
    """La progression doit être sauvegardée et restaurée."""
    scenarios = [_make_scenario("S1"), _make_scenario("S2")]
    persistence = CampaignPersistence(save_directory=tmp_path)

    manager = CampaignManager("camp", scenarios, persistence)
    assert manager.current_scenario().name == "S1"

    manager.advance()
    assert manager.current_scenario().name == "S2"

    # Rechargement pour vérifier la persistance
    manager2 = CampaignManager("camp", scenarios, persistence)
    assert manager2.current_scenario().name == "S2"
    assert manager2.is_completed()
