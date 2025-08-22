"""Bibliothèque d'événements aléatoires classés par thème et période."""
from __future__ import annotations

from typing import Dict, List
from decimal import Decimal
from copy import deepcopy

from .random_events import RandomEvent, EventCategory

# Les événements sont regroupés par catégorie puis par période (saison).
# La clé "all" indique que l'événement peut survenir à n'importe quel moment.
EVENT_LIBRARY: Dict[EventCategory, Dict[str, List[RandomEvent]]] = {
    EventCategory.WEATHER: {
        "été": [
            RandomEvent(
                id="heatwave",
                title="🌡️ Canicule",
                description="Forte chaleur, les clients recherchent des boissons fraîches.",
                category=EventCategory.WEATHER,
                probability=0.15,
                duration=3,
                demand_multiplier=Decimal("1.25"),
                segment_effects={
                    "étudiants": Decimal("1.4"),
                    "familles": Decimal("1.3"),
                },
                season_required="été",
            ),
        ],
        "automne": [
            RandomEvent(
                id="heavy_rain",
                title="🌧️ Pluie battante",
                description="Les gens sortent moins et préfèrent rester chez eux.",
                category=EventCategory.WEATHER,
                probability=0.20,
                duration=2,
                demand_multiplier=Decimal("0.80"),
                season_required="automne",
            ),
        ],
        "hiver": [
            RandomEvent(
                id="snow_storm",
                title="❄️ Tempête de neige",
                description="Circulation difficile, moins de clients.",
                category=EventCategory.WEATHER,
                probability=0.12,
                duration=2,
                demand_multiplier=Decimal("0.70"),
                season_required="hiver",
            ),
        ],
    },
    EventCategory.ECONOMIC: {
        "all": [
            RandomEvent(
                id="economic_crisis",
                title="📉 Crise économique",
                description="Les consommateurs deviennent très sensibles aux prix.",
                category=EventCategory.ECONOMIC,
                probability=0.08,
                duration=5,
                price_sensitivity=Decimal("1.6"),
                segment_effects={
                    "étudiants": Decimal("0.7"),
                    "familles": Decimal("0.8"),
                },
            ),
            RandomEvent(
                id="bonus_payment",
                title="💰 Prime exceptionnelle",
                description="Augmentation temporaire du pouvoir d'achat.",
                category=EventCategory.ECONOMIC,
                probability=0.15,
                duration=3,
                demand_multiplier=Decimal("1.20"),
                price_sensitivity=Decimal("0.85"),
            ),
        ]
    },
    EventCategory.SOCIAL: {
        "printemps": [
            RandomEvent(
                id="local_festival",
                title="🎉 Festival local",
                description="Afflux de visiteurs pour le festival local.",
                category=EventCategory.SOCIAL,
                probability=0.18,
                duration=2,
                demand_multiplier=Decimal("1.30"),
                season_required="printemps",
            ),
        ]
    },
    EventCategory.COMPETITION: {
        "all": [
            RandomEvent(
                id="new_competitor",
                title="🏪 Nouveau concurrent",
                description="Une nouvelle enseigne s'installe à proximité.",
                category=EventCategory.COMPETITION,
                probability=0.10,
                duration=4,
                demand_multiplier=Decimal("0.90"),
            ),
        ]
    },
}


def get_events(theme: EventCategory, period: str | None = None) -> List[RandomEvent]:
    """Retourne les événements pour un thème et une période donnés."""
    period_key = period or "all"
    events = []
    themed = EVENT_LIBRARY.get(theme, {})
    if period_key in themed:
        events.extend(themed[period_key])
    if period_key != "all" and "all" in themed:
        events.extend(themed["all"])
    # Retourner une copie pour éviter la modification de la bibliothèque
    return [deepcopy(e) for e in events]
