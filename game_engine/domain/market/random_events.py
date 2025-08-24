"""
Système d'événements aléatoires
"""

import random
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


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
    segment_effects: dict[str, Decimal] = None

    # Conditions d'activation
    min_turn: int = 1
    max_turn: int = 999
    season_required: str | None = None

    def __post_init__(self):
        if self.segment_effects is None:
            self.segment_effects = {}


class RandomEventManager:
    """Gestionnaire des événements aléatoires."""

    def __init__(self, random_seed: int | None = None):
        self.rng = random.Random(random_seed)
        self.active_events: list[RandomEvent] = []
        self.event_history: list[RandomEvent] = []
        self.events_pool = self._create_events_pool()

    def _create_events_pool(self) -> list[RandomEvent]:
        """Crée la liste des événements possibles."""
        return [
            # Événements météorologiques
            RandomEvent(
                id="heatwave",
                title="🌡️ Canicule",
                description="Forte chaleur ! Les clients recherchent des boissons fraîches et des plats légers.",
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
            RandomEvent(
                id="heavy_rain",
                title="🌧️ Pluie battante",
                description="Mauvais temps persistant. Les gens sortent moins et préfèrent rester chez eux.",
                category=EventCategory.WEATHER,
                probability=0.20,
                duration=2,
                demand_multiplier=Decimal("0.80"),
                season_required="automne",
            ),
            RandomEvent(
                id="snow_storm",
                title="❄️ Tempête de neige",
                description="Chutes de neige importantes. Circulation difficile, moins de clients.",
                category=EventCategory.WEATHER,
                probability=0.12,
                duration=2,
                demand_multiplier=Decimal("0.70"),
                season_required="hiver",
            ),
            # Événements économiques
            RandomEvent(
                id="economic_crisis",
                title="📉 Crise économique",
                description="Difficultés économiques. Les consommateurs deviennent très sensibles aux prix.",
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
                description="Les salariés reçoivent une prime. Augmentation temporaire du pouvoir d'achat.",
                category=EventCategory.ECONOMIC,
                probability=0.15,
                duration=3,
                demand_multiplier=Decimal("1.20"),
                price_sensitivity=Decimal("0.85"),
            ),
            # Événements sociaux
            RandomEvent(
                id="local_festival",
                title="🎪 Festival local",
                description="Grand événement culturel dans le quartier. Affluence exceptionnelle !",
                category=EventCategory.SOCIAL,
                probability=0.25,
                duration=2,
                demand_multiplier=Decimal("1.50"),
                segment_effects={"foodies": Decimal("1.8"), "familles": Decimal("1.4")},
            ),
            RandomEvent(
                id="transport_strike",
                title="🚇 Grève des transports",
                description="Grève générale des transports. Difficultés pour venir au restaurant.",
                category=EventCategory.SOCIAL,
                probability=0.10,
                duration=1,
                demand_multiplier=Decimal("0.65"),
            ),
            RandomEvent(
                id="university_exams",
                title="📚 Période d'examens",
                description="Examens universitaires. Les étudiants sortent moins mais commandent plus à emporter.",
                category=EventCategory.SOCIAL,
                probability=0.30,
                duration=4,
                segment_effects={"étudiants": Decimal("0.6")},
                min_turn=3,
            ),
            # Événements de concurrence
            RandomEvent(
                id="new_competitor",
                title="🏪 Nouveau concurrent",
                description="Ouverture d'un nouveau restaurant dans le quartier. La concurrence s'intensifie.",
                category=EventCategory.COMPETITION,
                probability=0.06,
                duration=10,
                demand_multiplier=Decimal("0.85"),
                min_turn=5,
            ),
            RandomEvent(
                id="competitor_closure",
                title="🔒 Fermeture concurrent",
                description="Un restaurant concurrent ferme définitivement. Opportunité de récupérer sa clientèle !",
                category=EventCategory.COMPETITION,
                probability=0.04,
                duration=999,  # Permanent
                demand_multiplier=Decimal("1.25"),
                min_turn=8,
            ),
            # Événements d'approvisionnement
            RandomEvent(
                id="meat_shortage",
                title="🥩 Pénurie de viande",
                description="Problèmes d'approvisionnement en viande. Prix en hausse, qualité plus importante.",
                category=EventCategory.SUPPLY,
                probability=0.08,
                duration=4,
                quality_importance=Decimal("1.4"),
            ),
            RandomEvent(
                id="excellent_harvest",
                title="🥬 Récolte exceptionnelle",
                description="Excellente récolte de légumes locaux. Produits frais abondants et moins chers.",
                category=EventCategory.SUPPLY,
                probability=0.20,
                duration=6,
                quality_importance=Decimal("1.2"),
                season_required="automne",
            ),
            # Événements réglementaires
            RandomEvent(
                id="health_inspection",
                title="🔍 Contrôle sanitaire",
                description="Inspection d'hygiène dans le secteur. L'importance de la qualité est renforcée.",
                category=EventCategory.REGULATION,
                probability=0.18,
                duration=3,
                quality_importance=Decimal("1.5"),
            ),
            RandomEvent(
                id="tax_reduction",
                title="📋 Réduction de charges",
                description="Baisse temporaire des charges sociales. Amélioration des marges pour tous.",
                category=EventCategory.REGULATION,
                probability=0.12,
                duration=8,
                demand_multiplier=Decimal("1.10"),
            ),
            # Événements spéciaux
            RandomEvent(
                id="food_trend",
                title="📱 Nouvelle tendance culinaire",
                description="Buzz sur les réseaux sociaux autour d'un type de cuisine. Les foodies sont très actifs.",
                category=EventCategory.SOCIAL,
                probability=0.22,
                duration=5,
                segment_effects={"foodies": Decimal("1.6")},
                quality_importance=Decimal("1.3"),
            ),
            RandomEvent(
                id="celebrity_visit",
                title="⭐ Visite de célébrité",
                description="Une célébrité est aperçue dans le quartier. Effet de mode temporaire !",
                category=EventCategory.SOCIAL,
                probability=0.05,
                duration=2,
                demand_multiplier=Decimal("1.80"),
                segment_effects={"foodies": Decimal("2.2")},
            ),
        ]

    def process_turn(self, turn: int, season: str) -> list[RandomEvent]:
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

    def get_current_effects(self) -> dict[str, any]:
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

    def get_events_summary(self) -> dict[str, any]:
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
