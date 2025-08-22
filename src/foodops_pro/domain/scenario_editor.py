"""Outil simple pour construire des scénarios FoodOps Pro.

Cet éditeur fournit une interface programmatique pour configurer le marché,
les effets météo, la concurrence et les événements liés à un scénario. Il ne
remplace pas une interface graphique mais facilite la création de scénarios
dans les tests ou scripts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal

from .scenario import Scenario, MarketSegment
from .random_events import RandomEvent


@dataclass
class ScenarioEditor:
    """Permet de construire progressivement un :class:`Scenario`.

    Exemple d'utilisation ::

        editor = ScenarioEditor(name="Demo")
        editor.add_market_segment(MarketSegment(...))
        editor.set_competition(2)
        editor.add_event(RandomEvent(...))
        scenario = editor.build()
    """

    name: str = "Scénario personnalisé"
    description: str = ""
    turns: int = 12
    base_demand: int = 100
    demand_noise: Decimal = Decimal("0.1")
    segments: List[MarketSegment] = field(default_factory=list)
    vat_rates: Dict[str, Decimal] = field(default_factory=dict)
    social_charges: Dict[str, Decimal] = field(default_factory=dict)
    interest_rate: Decimal = Decimal("0.05")
    ai_competitors: int = 0
    random_seed: Optional[int] = None
    events: List[RandomEvent] = field(default_factory=list)

    def add_market_segment(self, segment: MarketSegment) -> None:
        """Ajoute un segment de marché au scénario."""
        self.segments.append(segment)

    def set_competition(self, ai_competitors: int) -> None:
        """Définit le nombre de concurrents contrôlés par l'IA."""
        self.ai_competitors = ai_competitors

    def set_weather(self, month: int, factor: Decimal) -> None:
        """Applique un facteur saisonnier à tous les segments pour un mois donné."""
        for segment in self.segments:
            segment.seasonality[month] = factor

    def add_event(self, event: RandomEvent) -> None:
        """Ajoute un événement prédéfini au scénario."""
        self.events.append(event)

    def build(self) -> Scenario:
        """Construit l'objet :class:`Scenario` final."""
        if not self.segments:
            raise ValueError("Au moins un segment de marché est requis")
        return Scenario(
            name=self.name,
            description=self.description,
            turns=self.turns,
            base_demand=self.base_demand,
            demand_noise=self.demand_noise,
            segments=self.segments,
            vat_rates=self.vat_rates,
            social_charges=self.social_charges,
            interest_rate=self.interest_rate,
            ai_competitors=self.ai_competitors,
            random_seed=self.random_seed,
            events=self.events,
        )
