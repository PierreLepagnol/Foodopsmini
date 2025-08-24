"""
Système de concurrence dynamique pour FoodOps Pro.
"""

import json
import random
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from pathlib import Path

from pydantic import BaseModel

directory = Path("/home/lepagnol/Documents/Perso/Games/Foodopsmini/data")
EVENTS_FILE = directory / "events.json"


class EventType(Enum):
    """Types d'événements aléatoires."""

    WEATHER = "meteo"
    ECONOMIC = "economique"
    SOCIAL = "social"
    SUPPLY = "approvisionnement"
    COMPETITION = "concurrence"
    REGULATION = "reglementation"


class EventImpact(Enum):
    """Impact des événements."""

    POSITIVE = "positif"
    NEGATIVE = "negatif"
    NEUTRAL = "neutre"


@dataclass
class MarketEvent:
    """Événement de marché affectant la concurrence."""

    id: str
    name: str
    description: str
    type: EventType
    impact: EventImpact
    duration_days: int
    probability: Decimal  # 0.0 à 1.0

    # Effets sur le marché
    demand_modifier: Decimal = Decimal("1.0")  # Multiplicateur demande
    price_sensitivity_modifier: Decimal = Decimal("1.0")  # Sensibilité prix
    quality_importance_modifier: Decimal = Decimal("1.0")  # Importance qualité
    segment_impact: dict[str, Decimal] = field(default_factory=dict)

    # Conditions d'activation
    season_requirements: list[str] = field(default_factory=list)
    min_turn: int = 1
    max_turn: int = 999

    def is_applicable(self, current_turn: int, current_season: str) -> bool:
        """Vérifie si l'événement peut se produire."""
        # Vérification du tour
        if not (self.min_turn <= current_turn <= self.max_turn):
            return False

        # Vérification de la saison
        if self.season_requirements and current_season not in self.season_requirements:
            return False

        return True

    def decrement_duration(self):
        self.duration_days -= 1


class SegmentModifiers(BaseModel):
    segment_name: str
    modifier: Decimal


class Modifiers(BaseModel):
    demand_modifier: Decimal = Decimal("1.0")
    price_sensitivity_modifier: Decimal = Decimal("1.0")
    quality_importance_modifier: Decimal = Decimal("1.0")
    segment_modifiers: list[SegmentModifiers] = []


@dataclass
class CompetitorAction:
    """Action d'un concurrent IA."""

    competitor_id: str
    action_type: str  # "price_change", "quality_upgrade", "marketing_campaign"
    parameters: dict
    turn_executed: int
    impact_duration: int = 1


class CompetitionManager:
    """Gestionnaire de la concurrence dynamique."""

    def __init__(self, random_seed: int | None = None):
        self.rng = random.Random(random_seed)
        self.active_events: list[MarketEvent] = []
        self.event_history: list[MarketEvent] = []
        self.competitor_actions: list[CompetitorAction] = []

        # Chargement des événements possibles
        self.available_events = self._load_market_events()

        # État de la concurrence
        self.market_volatility = Decimal("0.1")  # 10% de volatilité de base
        self.competitive_pressure = Decimal("1.0")  # Pression concurrentielle

    @staticmethod
    def _load_market_events() -> list[MarketEvent]:
        """Charge la liste des événements de marché possibles."""
        with open(EVENTS_FILE) as f:
            events_data = json.load(f)
        events = [MarketEvent(**event) for event in events_data["events"]]
        return events

    def clean_expired_events(self) -> None:
        """Nettoie les événements expirés."""
        self.active_events = [
            event for event in self.active_events if event.duration_days > 0
        ]

    def process_turn_events(
        self, current_turn: int, current_season: str
    ) -> list[MarketEvent]:
        """
        Traite les événements pour le tour actuel.

        Cette méthode gère le cycle de vie complet des événements de marché :
        - Évalue quels nouveaux événements peuvent se déclencher
        - Crée les instances d'événements selon leur probabilité
        - Met à jour la durée des événements actifs
        - Archive les événements terminés

        Les événements peuvent affecter la demande, la sensibilité aux prix,
        l'importance de la qualité, et avoir des impacts spécifiques par segment.

        Args:
            current_turn: Numéro du tour actuel (utilisé pour les conditions min_turn)
            current_season: Saison actuelle ("printemps", "été", "automne", "hiver")
                          pour les événements saisonniers

        Returns:
            Liste des nouveaux événements déclenchés ce tour.
            Les événements retournés sont aussi ajoutés à self.active_events.

        Note:
            Cette méthode modifie l'état interne (active_events, event_history).
            Elle doit être appelée une seule fois par tour pour éviter les doublons.
        """
        # === PHASE 1: FILTRAGE DES ÉVÉNEMENTS APPLICABLES ===
        # Filtres des événements qui ne peuvent pas se déclencher
        applicable_events = [
            event
            for event in self.available_events
            if event.is_applicable(current_turn, current_season)
        ]
        potential_events = [
            event
            for event in applicable_events
            if self.rng.random() < float(event.probability)
        ]

        # === PHASE 2: DÉCLENCHEMENT DE NOUVEAUX ÉVÉNEMENTS ===

        # Build new events
        new_events = [
            MarketEvent(
                id=f"{event_template.id}_{current_turn}",
                name=event_template.name,
                description=event_template.description,
                type=event_template.type,
                impact=event_template.impact,
                duration_days=event_template.duration_days,
                probability=event_template.probability,
                demand_modifier=event_template.demand_modifier,
                price_sensitivity_modifier=event_template.price_sensitivity_modifier,
                quality_importance_modifier=event_template.quality_importance_modifier,
                segment_impact=event_template.segment_impact.copy(),
            )
            for event_template in potential_events
        ]

        # === PHASE 3: MISE À JOUR DES DURÉES ===
        self.active_events.extend(new_events)
        self.clean_expired_events()
        # Décrémenter la durée de tous les événements actifs
        [event.decrement_duration() for event in self.active_events]
        # Supprimer les événements qui viennent de se terminer, l'archiver
        self.event_history.extend(
            [event for event in self.active_events if event.duration_days == 0]
        )
        self.clean_expired_events()

        return new_events

    def get_market_modifiers(self) -> Modifiers:
        """
        Calcule les modificateurs de marché cumulés basés sur tous les événements actifs.

        Cette méthode agrège les effets de tous les événements en cours pour produire
        un ensemble de modificateurs qui influencent le comportement du marché.
        Les modificateurs sont multiplicatifs - plusieurs événements peuvent se combiner
        pour créer des effets composés.

        Returns:
            Dict[str, Decimal]: Dictionnaire contenant les modificateurs de marché:
                - demand_modifier: Multiplicateur de la demande globale (1.0 = neutre)
                - price_sensitivity_modifier: Multiplicateur de la sensibilité aux prix
                - quality_importance_modifier: Multiplicateur de l'importance de la qualité
                - segment_modifiers: Dict des modificateurs spécifiques par segment de clientèle

        Note:
            - Tous les modificateurs partent de 1.0 (neutre) et sont multipliés ensemble
            - Les valeurs > 1.0 indiquent un effet positif, < 1.0 un effet négatif
            - Les modificateurs par segment sont optionnels et ne s'appliquent qu'aux segments concernés
        """
        # === INITIALISATION DES MODIFICATEURS DE BASE ===
        # Tous les modificateurs partent de 1.0 (effet neutre)

        modifiers = {
            "demand_modifier": Decimal("1.0"),
            "price_sensitivity_modifier": Decimal("1.0"),
            "quality_importance_modifier": Decimal("1.0"),
            "segment_modifiers": {},
        }

        # === AGRÉGATION DES EFFETS DES ÉVÉNEMENTS ACTIFS ===
        for event in self.active_events:
            # Appliquer les effets multiplicatifs globaux
            modifiers["demand_modifier"] *= event.demand_modifier
            modifiers["price_sensitivity_modifier"] *= event.price_sensitivity_modifier
            modifiers["quality_importance_modifier"] *= (
                event.quality_importance_modifier
            )

            # Appliquer les modificateurs par segment
            for segment, modifier in event.segment_impact.items():
                if segment not in modifiers["segment_modifiers"]:
                    modifiers["segment_modifiers"][segment] = Decimal("1.0")
                modifiers["segment_modifiers"][segment] *= modifier

        return modifiers

    def simulate_competitor_actions(
        self, current_turn: int, market_data: dict
    ) -> list[CompetitorAction]:
        """
        Simule les actions des concurrents IA.

        Args:
            current_turn: Tour actuel
            market_data: Données du marché

        Returns:
            Liste des actions des concurrents
        """
        actions = []

        # Probabilité d'action des concurrents
        action_probability = 0.3 + (self.competitive_pressure - 1.0) * 0.2

        if self.rng.random() < action_probability:
            # Types d'actions possibles
            action_types = [
                "price_reduction",
                "quality_upgrade",
                "marketing_campaign",
                "menu_expansion",
            ]

            action_type = self.rng.choice(action_types)

            action = CompetitorAction(
                competitor_id="ai_competitor_1",
                action_type=action_type,
                parameters=self._generate_action_parameters(action_type),
                turn_executed=current_turn,
                impact_duration=self.rng.randint(2, 5),
            )

            actions.append(action)
            self.competitor_actions.append(action)

        return actions

    def _generate_action_parameters(self, action_type: str) -> dict:
        """Génère les paramètres pour une action de concurrent."""
        if action_type == "price_reduction":
            return {
                "price_change": -self.rng.uniform(0.05, 0.15),  # -5% à -15%
                "description": "Baisse des prix pour attirer plus de clients",
            }
        elif action_type == "quality_upgrade":
            return {
                "quality_improvement": self.rng.uniform(0.2, 0.5),  # +20% à +50%
                "description": "Amélioration de la qualité des ingrédients",
            }
        elif action_type == "marketing_campaign":
            return {
                "marketing_boost": self.rng.uniform(0.1, 0.3),  # +10% à +30%
                "duration": self.rng.randint(3, 7),
                "description": "Lancement d'une campagne publicitaire",
            }
        elif action_type == "menu_expansion":
            return {
                "new_options": self.rng.randint(1, 3),
                "attractiveness_boost": self.rng.uniform(0.05, 0.15),
                "description": "Ajout de nouveaux plats au menu",
            }

        return {}

    def get_competition_summary(self) -> dict[str, any]:
        """Retourne un résumé de l'état de la concurrence."""
        return {
            "active_events": len(self.active_events),
            "market_volatility": float(self.market_volatility),
            "competitive_pressure": float(self.competitive_pressure),
            "recent_competitor_actions": len(
                [
                    a
                    for a in self.competitor_actions
                    if a.turn_executed >= max(1, len(self.competitor_actions) - 5)
                ]
            ),
            "current_events": [
                {
                    "name": event.name,
                    "description": event.description,
                    "type": event.type.value,
                    "impact": event.impact.value,
                    "remaining_days": event.duration_days,
                }
                for event in self.active_events
            ],
        }

    def update_competitive_pressure(self, market_performance: dict[str, float]) -> None:
        """Met à jour la pression concurrentielle basée sur les performances."""
        # Si le marché est très compétitif (marges faibles), augmenter la pression
        avg_margin = (
            sum(market_performance.values()) / len(market_performance)
            if market_performance
            else 0.15
        )

        if avg_margin < 0.10:  # Marges très faibles
            self.competitive_pressure = min(
                Decimal("2.0"), self.competitive_pressure + Decimal("0.1")
            )
        elif avg_margin > 0.25:  # Marges élevées
            self.competitive_pressure = max(
                Decimal("0.5"), self.competitive_pressure - Decimal("0.05")
            )

    def get_event_impact_description(self, event: MarketEvent) -> str:
        """Retourne une description de l'impact d'un événement."""
        impacts = []

        if event.demand_modifier != Decimal("1.0"):
            change = (event.demand_modifier - 1) * 100
            impacts.append(f"Demande: {change:+.0f}%")

        if event.price_sensitivity_modifier != Decimal("1.0"):
            change = (event.price_sensitivity_modifier - 1) * 100
            impacts.append(f"Sensibilité prix: {change:+.0f}%")

        if event.quality_importance_modifier != Decimal("1.0"):
            change = (event.quality_importance_modifier - 1) * 100
            impacts.append(f"Importance qualité: {change:+.0f}%")

        if event.segment_impact:
            for segment, modifier in event.segment_impact.items():
                change = (modifier - 1) * 100
                impacts.append(f"{segment}: {change:+.0f}%")

        return " | ".join(impacts) if impacts else "Aucun impact direct"
