"""Suite de missions prêtes à l'emploi pour FoodOps Pro."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List
from decimal import Decimal

from .scenario import Scenario, MarketSegment
from .restaurant import RestaurantType


@dataclass
class Mission:
    """Représente une mission de campagne avec un objectif spécifique."""

    name: str
    scenario: Scenario
    objective: str


def _default_segments() -> List[MarketSegment]:
    """Crée les segments de marché standards utilisés dans les missions."""
    return [
        MarketSegment(
            name="étudiants",
            share=Decimal("0.35"),
            budget=Decimal("11"),
            type_affinity={
                RestaurantType.FAST_FOOD: Decimal("1.2"),
                RestaurantType.CLASSIC: Decimal("0.8"),
            },
        ),
        MarketSegment(
            name="familles",
            share=Decimal("0.40"),
            budget=Decimal("17"),
            type_affinity={
                RestaurantType.CLASSIC: Decimal("1.1"),
                RestaurantType.FAST_FOOD: Decimal("0.9"),
            },
        ),
        MarketSegment(
            name="foodies",
            share=Decimal("0.25"),
            budget=Decimal("25"),
            type_affinity={
                RestaurantType.GASTRO: Decimal("1.3"),
                RestaurantType.CLASSIC: Decimal("1.0"),
            },
        ),
    ]


def create_default_missions() -> List[Mission]:
    """Retourne une suite de missions graduées."""
    missions = [
        Mission(
            name="Snack de quartier",
            scenario=Scenario(
                name="Snack de quartier",
                description="Débutez dans un petit snack local.",
                turns=6,
                base_demand=80,
                demand_noise=Decimal("0.1"),
                segments=_default_segments(),
                ai_competitors=1,
            ),
            objective="Atteindre un CA de 10k€",
        ),
        Mission(
            name="Bistrot de ville",
            scenario=Scenario(
                name="Bistrot de ville",
                description="Développez un bistrot en centre-ville.",
                turns=10,
                base_demand=120,
                demand_noise=Decimal("0.15"),
                segments=_default_segments(),
                ai_competitors=2,
            ),
            objective="Maintenir une marge brute > 60%",
        ),
        Mission(
            name="Chaîne nationale",
            scenario=Scenario(
                name="Chaîne nationale",
                description="Gérez une chaîne à l'échelle du pays.",
                turns=18,
                base_demand=200,
                demand_noise=Decimal("0.20"),
                segments=_default_segments(),
                ai_competitors=4,
            ),
            objective="Ouvrir dans 5 régions",
        ),
    ]
    return missions
