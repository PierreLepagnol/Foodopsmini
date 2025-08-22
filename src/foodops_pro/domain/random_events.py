"""
Système d'événements aléatoires pour FoodOps Pro.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal
from enum import Enum
from copy import deepcopy
import random


class EventCategory(Enum):
    """Catégories d'événements."""

    WEATHER = "météo"
    ECONOMIC = "économique"
    SOCIAL = "social"
    COMPETITION = "concurrence"
    SUPPLY = "approvisionnement"
    REGULATION = "réglementation"


@dataclass
class RandomEvent:
    """Événement aléatoire affectant le marché."""

    id: str
    title: str
    description: str
    category: EventCategory
    probability: float  # 0.0 à 1.0
    duration: int  # Nombre de tours

    # Effets sur le gameplay
    demand_multiplier: Decimal = Decimal("1.0")
    price_sensitivity: Decimal = Decimal("1.0")
    quality_importance: Decimal = Decimal("1.0")
    segment_effects: Dict[str, Decimal] = None

    # Conditions d'activation
    min_turn: int = 1
    max_turn: int = 999
    season_required: Optional[str] = None

    def __post_init__(self):
        if self.segment_effects is None:
            self.segment_effects = {}


class RandomEventManager:
    """Gestionnaire des événements aléatoires."""

    def __init__(self, random_seed: Optional[int] = None):
        self.rng = random.Random(random_seed)
        self.active_events: List[RandomEvent] = []
        self.event_history: List[RandomEvent] = []
        self.events_pool = self._create_events_pool()

    def _create_events_pool(self) -> List[RandomEvent]:
        """Crée la liste des événements possibles à partir de la bibliothèque."""
        from .event_library import EVENT_LIBRARY

        return [
            deepcopy(event)
            for periods in EVENT_LIBRARY.values()
            for event_list in periods.values()
            for event in event_list
        ]

    def process_turn(self, turn: int, season: str) -> List[RandomEvent]:
        """
        Traite les événements pour un tour donné.

        Args:
            turn: Numéro du tour
            season: Saison actuelle

        Returns:
            Liste des nouveaux événements déclenchés
        """
        new_events = []

        # Vérifier les événements possibles
        for event_template in self.events_pool:
            # Vérifier les conditions
            if not self._can_trigger(event_template, turn, season):
                continue

            # Test de probabilité
            if self.rng.random() < event_template.probability:
                # Créer une instance de l'événement
                event_instance = RandomEvent(
                    id=f"{event_template.id}_{turn}",
                    title=event_template.title,
                    description=event_template.description,
                    category=event_template.category,
                    probability=event_template.probability,
                    duration=event_template.duration,
                    demand_multiplier=event_template.demand_multiplier,
                    price_sensitivity=event_template.price_sensitivity,
                    quality_importance=event_template.quality_importance,
                    segment_effects=event_template.segment_effects.copy(),
                )

                new_events.append(event_instance)
                self.active_events.append(event_instance)

        # Décrémenter la durée des événements actifs
        self._update_active_events()

        return new_events

    def _can_trigger(self, event: RandomEvent, turn: int, season: str) -> bool:
        """Vérifie si un événement peut se déclencher."""
        # Vérifier le tour
        if not (event.min_turn <= turn <= event.max_turn):
            return False

        # Vérifier la saison
        if event.season_required and season != event.season_required:
            return False

        # Éviter les doublons d'événements similaires
        for active_event in self.active_events:
            if active_event.category == event.category and active_event.duration > 1:
                return False

        return True

    def _update_active_events(self):
        """Met à jour la liste des événements actifs."""
        expired_events = []

        for event in self.active_events:
            event.duration -= 1
            if event.duration <= 0:
                expired_events.append(event)
                self.event_history.append(event)

        # Supprimer les événements expirés
        for event in expired_events:
            self.active_events.remove(event)

    def get_current_effects(self) -> Dict[str, any]:
        """Retourne les effets cumulés des événements actifs."""
        effects = {
            "demand_multiplier": Decimal("1.0"),
            "price_sensitivity": Decimal("1.0"),
            "quality_importance": Decimal("1.0"),
            "segment_effects": {},
        }

        for event in self.active_events:
            effects["demand_multiplier"] *= event.demand_multiplier
            effects["price_sensitivity"] *= event.price_sensitivity
            effects["quality_importance"] *= event.quality_importance

            # Effets par segment
            for segment, multiplier in event.segment_effects.items():
                if segment not in effects["segment_effects"]:
                    effects["segment_effects"][segment] = Decimal("1.0")
                effects["segment_effects"][segment] *= multiplier

        return effects

    def get_events_summary(self) -> Dict[str, any]:
        """Retourne un résumé des événements."""
        return {
            "active_events": [
                {
                    "title": event.title,
                    "description": event.description,
                    "category": event.category.value,
                    "remaining_turns": event.duration,
                }
                for event in self.active_events
            ],
            "total_active": len(self.active_events),
            "total_history": len(self.event_history),
        }

    def get_event_notification(self, event: RandomEvent) -> str:
        """Génère une notification pour un événement."""
        category_icons = {
            EventCategory.WEATHER: "🌤️",
            EventCategory.ECONOMIC: "💰",
            EventCategory.SOCIAL: "👥",
            EventCategory.COMPETITION: "🏪",
            EventCategory.SUPPLY: "📦",
            EventCategory.REGULATION: "📋",
        }

        icon = category_icons.get(event.category, "📢")

        notification = f"{icon} ÉVÉNEMENT: {event.title}\n"
        notification += f"   {event.description}\n"
        notification += f"   Durée: {event.duration} tour(s)\n"

        # Ajouter les effets principaux
        effects = []
        if event.demand_multiplier != Decimal("1.0"):
            change = (event.demand_multiplier - 1) * 100
            effects.append(f"Demande: {change:+.0f}%")

        if event.price_sensitivity != Decimal("1.0"):
            change = (event.price_sensitivity - 1) * 100
            effects.append(f"Sensibilité prix: {change:+.0f}%")

        if event.quality_importance != Decimal("1.0"):
            change = (event.quality_importance - 1) * 100
            effects.append(f"Importance qualité: {change:+.0f}%")

        if effects:
            notification += f"   Effets: {' | '.join(effects)}"

        return notification
