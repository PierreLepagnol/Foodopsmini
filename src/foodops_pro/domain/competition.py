"""
Système de concurrence dynamique pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from enum import Enum
from datetime import date
import random

from .restaurant import Restaurant


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
    segment_impact: Dict[str, Decimal] = field(default_factory=dict)
    competitor_impact: Dict[str, Dict[str, Decimal]] = field(default_factory=dict)

    # Conditions d'activation
    season_requirements: List[str] = field(default_factory=list)
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


@dataclass
class CompetitorAction:
    """Action d'un concurrent IA."""

    competitor_id: str
    action_type: str  # "price_change", "quality_upgrade", "marketing_campaign"
    parameters: Dict
    turn_executed: int
    impact_duration: int = 1


class CompetitionManager:
    """Gestionnaire de la concurrence dynamique."""

    def __init__(self, random_seed: Optional[int] = None):
        self.rng = random.Random(random_seed)
        self.active_events: List[MarketEvent] = []
        self.event_history: List[MarketEvent] = []
        self.competitor_actions: List[CompetitorAction] = []

        # Chargement des événements possibles
        self.available_events = self._load_market_events()

        # État de la concurrence
        self.market_volatility = Decimal("0.1")  # 10% de volatilité de base
        self.competitive_pressure = Decimal("1.0")  # Pression concurrentielle
        # Modificateurs calculés lors du traitement des événements
        self.segment_event_modifiers: Dict[str, Decimal] = {}
        self.competitor_event_modifiers: Dict[str, Dict[str, Decimal]] = {}
        # Historique des réactions concurrentielles pour éviter les répétitions
        self.last_reaction_turn: Dict[str, int] = {}

    def _load_market_events(self) -> List[MarketEvent]:
        """Charge la liste des événements de marché possibles."""
        events = [
            # Événements météorologiques
            MarketEvent(
                id="canicule",
                name="Canicule",
                description="Forte chaleur, demande accrue pour boissons fraîches et salades",
                type=EventType.WEATHER,
                impact=EventImpact.POSITIVE,
                duration_days=5,
                probability=Decimal("0.15"),
                demand_modifier=Decimal("1.2"),
                segment_impact={
                    "familles": Decimal("1.3"),
                    "étudiants": Decimal("1.4"),
                },
                season_requirements=["été"],
            ),
            MarketEvent(
                id="pluie_continue",
                name="Pluie continue",
                description="Mauvais temps, les gens sortent moins",
                type=EventType.WEATHER,
                impact=EventImpact.NEGATIVE,
                duration_days=3,
                probability=Decimal("0.20"),
                demand_modifier=Decimal("0.85"),
                season_requirements=["automne", "hiver"],
            ),
            # Événements économiques
            MarketEvent(
                id="crise_pouvoir_achat",
                name="Crise du pouvoir d'achat",
                description="Les consommateurs deviennent plus sensibles aux prix",
                type=EventType.ECONOMIC,
                impact=EventImpact.NEGATIVE,
                duration_days=10,
                probability=Decimal("0.08"),
                price_sensitivity_modifier=Decimal("1.5"),
                segment_impact={
                    "étudiants": Decimal("0.7"),
                    "familles": Decimal("0.8"),
                },
            ),
            MarketEvent(
                id="prime_exceptionnelle",
                name="Prime exceptionnelle",
                description="Les salariés reçoivent une prime, augmentation du pouvoir d'achat",
                type=EventType.ECONOMIC,
                impact=EventImpact.POSITIVE,
                duration_days=7,
                probability=Decimal("0.12"),
                demand_modifier=Decimal("1.15"),
                price_sensitivity_modifier=Decimal("0.9"),
            ),
            # Événements sociaux
            MarketEvent(
                id="festival_local",
                name="Festival local",
                description="Événement culturel attirant du monde dans le quartier",
                type=EventType.SOCIAL,
                impact=EventImpact.POSITIVE,
                duration_days=3,
                probability=Decimal("0.25"),
                demand_modifier=Decimal("1.4"),
                segment_impact={"foodies": Decimal("1.6"), "familles": Decimal("1.3")},
            ),
            MarketEvent(
                id="greve_transports",
                name="Grève des transports",
                description="Difficultés de transport, moins de clients",
                type=EventType.SOCIAL,
                impact=EventImpact.NEGATIVE,
                duration_days=2,
                probability=Decimal("0.10"),
                demand_modifier=Decimal("0.75"),
            ),
            # Événements d'approvisionnement
            MarketEvent(
                id="penurie_viande",
                name="Pénurie de viande",
                description="Problème d'approvisionnement, prix de la viande en hausse",
                type=EventType.SUPPLY,
                impact=EventImpact.NEGATIVE,
                duration_days=8,
                probability=Decimal("0.06"),
                quality_importance_modifier=Decimal(
                    "1.3"
                ),  # Qualité devient plus importante
            ),
            MarketEvent(
                id="recolte_exceptionnelle",
                name="Récolte exceptionnelle",
                description="Excellente récolte de légumes, prix en baisse",
                type=EventType.SUPPLY,
                impact=EventImpact.POSITIVE,
                duration_days=15,
                probability=Decimal("0.18"),
                season_requirements=["automne"],
            ),
            # Événements concurrentiels
            MarketEvent(
                id="nouveau_concurrent",
                name="Nouveau concurrent",
                description="Ouverture d'un nouveau restaurant dans le quartier",
                type=EventType.COMPETITION,
                impact=EventImpact.NEGATIVE,
                duration_days=30,
                probability=Decimal("0.05"),
                demand_modifier=Decimal("0.9"),
                min_turn=5,
            ),
            MarketEvent(
                id="fermeture_concurrent",
                name="Fermeture concurrent",
                description="Un concurrent ferme définitivement",
                type=EventType.COMPETITION,
                impact=EventImpact.POSITIVE,
                duration_days=999,  # Permanent
                probability=Decimal("0.03"),
                demand_modifier=Decimal("1.15"),
                min_turn=10,
            ),
            # Événements réglementaires
            MarketEvent(
                id="controle_hygiene",
                name="Contrôle d'hygiène",
                description="Inspection sanitaire, importance accrue de la qualité",
                type=EventType.REGULATION,
                impact=EventImpact.NEUTRAL,
                duration_days=5,
                probability=Decimal("0.15"),
                quality_importance_modifier=Decimal("1.4"),
            ),
        ]

        return events

    def process_turn_events(
        self, current_turn: int, current_season: str
    ) -> List[MarketEvent]:
        """
        Traite les événements pour le tour actuel.

        Args:
            current_turn: Numéro du tour actuel
            current_season: Saison actuelle

        Returns:
            Liste des nouveaux événements déclenchés
        """
        new_events = []

        # Vérifier les événements possibles
        for event_template in self.available_events:
            if not event_template.is_applicable(current_turn, current_season):
                continue

            # Vérifier si l'événement se déclenche (probabilité)
            if self.rng.random() < float(event_template.probability):
                # Créer une instance de l'événement
                new_event = MarketEvent(
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
                    competitor_impact=event_template.competitor_impact.copy(),
                )

                new_events.append(new_event)
                self.active_events.append(new_event)

        # Supprimer les événements expirés
        self.active_events = [
            event for event in self.active_events if event.duration_days > 0
        ]

        # Décrémenter la durée des événements actifs
        for event in self.active_events:
            event.duration_days -= 1
            if event.duration_days == 0:
                self.event_history.append(event)

        # Recalculer les modificateurs par segment et par concurrent
        self.segment_event_modifiers = {}
        self.competitor_event_modifiers = {}
        for event in self.active_events:
            for segment, modifier in event.segment_impact.items():
                current = self.segment_event_modifiers.get(segment, Decimal("1.0"))
                self.segment_event_modifiers[segment] = current * modifier
            for comp_id, impacts in event.competitor_impact.items():
                comp_mod = self.competitor_event_modifiers.setdefault(
                    comp_id, {"price": Decimal("1.0"), "quality": Decimal("1.0")}
                )
                if "price" in impacts:
                    comp_mod["price"] *= impacts["price"]
                if "quality" in impacts:
                    comp_mod["quality"] *= impacts["quality"]

        return new_events

    def get_market_modifiers(self) -> Dict[str, Decimal]:
        """
        Calcule les modificateurs de marché basés sur les événements actifs.

        Returns:
            Dictionnaire des modificateurs
        """
        modifiers = {
            "demand_modifier": Decimal("1.0"),
            "price_sensitivity_modifier": Decimal("1.0"),
            "quality_importance_modifier": Decimal("1.0"),
            "segment_modifiers": self.segment_event_modifiers.copy(),
            "competitor_modifiers": self.competitor_event_modifiers.copy(),
        }

        # Appliquer les effets globaux des événements actifs
        for event in self.active_events:
            modifiers["demand_modifier"] *= event.demand_modifier
            modifiers["price_sensitivity_modifier"] *= event.price_sensitivity_modifier
            modifiers["quality_importance_modifier"] *= event.quality_importance_modifier

        return modifiers

    def simulate_competitor_actions(
        self, current_turn: int, market_data: Dict
    ) -> List[CompetitorAction]:
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

    def _generate_action_parameters(self, action_type: str) -> Dict:
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

    def apply_competitor_reactions(
        self,
        restaurants: List[Restaurant],
        market_shares: Dict[str, Decimal],
        current_turn: int,
    ) -> List[CompetitorAction]:
        """Ajuste prix ou qualité des concurrents selon la domination du marché.

        Les concurrents qui perdent trop de parts de marché réagissent en
        baissant leurs prix ou en améliorant légèrement leur réputation.

        Args:
            restaurants: Liste complète des restaurants en concurrence
            market_shares: Parts de marché actuelles par restaurant
            current_turn: Tour courant de la simulation

        Returns:
            Liste des actions générées
        """

        if not market_shares:
            return []

        leader_id, leader_share = max(market_shares.items(), key=lambda x: x[1])
        actions: List[CompetitorAction] = []

        for restaurant in restaurants:
            if restaurant.id == leader_id:
                continue

            share = market_shares.get(restaurant.id, Decimal("0"))
            # Si l'écart est important, le concurrent réagit
            if leader_share - share >= Decimal("0.15"):
                # Éviter de réagir plusieurs fois le même tour
                if self.last_reaction_turn.get(restaurant.id) == current_turn:
                    continue

                price_factor = Decimal("0.90")
                for recipe_id, price in list(restaurant.menu.items()):
                    new_price = (price * price_factor).quantize(Decimal("0.01"))
                    restaurant.set_recipe_price(recipe_id, new_price)

                quality_boost = Decimal("0.3")
                restaurant.reputation = min(
                    Decimal("10.0"), restaurant.reputation + quality_boost
                )

                action = CompetitorAction(
                    competitor_id=restaurant.id,
                    action_type="reactive_adjustment",
                    parameters={
                        "price_factor": float(price_factor),
                        "quality_boost": float(quality_boost),
                    },
                    turn_executed=current_turn,
                    impact_duration=1,
                )
                actions.append(action)
                self.competitor_actions.append(action)
                self.last_reaction_turn[restaurant.id] = current_turn

        return actions

    def get_competition_summary(self) -> Dict[str, any]:
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

    def update_competitive_pressure(self, market_performance: Dict[str, float]) -> None:
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
