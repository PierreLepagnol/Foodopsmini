"""
Système de saisonnalité pour FoodOps Pro.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal
from enum import Enum
from datetime import date


class Season(Enum):
    """Saisons de l'année."""

    SPRING = "printemps"  # Mars-Mai
    SUMMER = "été"  # Juin-Août
    AUTUMN = "automne"  # Septembre-Novembre
    WINTER = "hiver"  # Décembre-Février


class SpecialEvent(Enum):
    """Événements spéciaux affectant les prix."""

    NEW_YEAR = "nouvel_an"
    EASTER = "paques"
    SUMMER_HOLIDAYS = "vacances_ete"
    BACK_TO_SCHOOL = "rentree"
    CHRISTMAS = "noel"
    HEATWAVE = "canicule"
    HARVEST = "recolte"


@dataclass(frozen=True)
class SeasonalModifier:
    """Modificateur saisonnier pour un ingrédient."""

    ingredient_id: str
    season: Season
    price_multiplier: Decimal  # Multiplicateur de prix (ex: 0.8 = -20%)
    quality_bonus: int = 0  # Bonus de qualité en étoiles
    availability_multiplier: Decimal = Decimal("1.0")  # Disponibilité
    demand_multiplier: Decimal = Decimal("1.0")  # Impact sur demande

    def __post_init__(self):
        """Validation des modificateurs."""
        if self.price_multiplier <= 0:
            raise ValueError(
                f"Le multiplicateur de prix doit être positif: {self.price_multiplier}"
            )
        if not (-2 <= self.quality_bonus <= 2):
            raise ValueError(
                f"Le bonus qualité doit être entre -2 et +2: {self.quality_bonus}"
            )
        if self.availability_multiplier < 0:
            raise ValueError(
                f"La disponibilité doit être positive: {self.availability_multiplier}"
            )


@dataclass(frozen=True)
class EventModifier:
    """Modificateur pour événement spécial."""

    ingredient_id: str
    event: SpecialEvent
    start_month: int
    end_month: int
    price_multiplier: Decimal
    demand_multiplier: Decimal = Decimal("1.0")

    def is_active(self, current_month: int) -> bool:
        """Vérifie si l'événement est actif pour le mois donné."""
        if self.start_month <= self.end_month:
            return self.start_month <= current_month <= self.end_month
        else:
            # Événement à cheval sur l'année (ex: décembre-février)
            return current_month >= self.start_month or current_month <= self.end_month


class SeasonalityManager:
    """Gestionnaire de la saisonnalité des ingrédients."""

    def __init__(self):
        self.seasonal_modifiers: List[SeasonalModifier] = []
        self.event_modifiers: List[EventModifier] = []
        self._load_default_seasonality()

    def _load_default_seasonality(self):
        """Charge la saisonnalité par défaut."""

        # === LÉGUMES DE PRINTEMPS ===
        spring_vegetables = [
            ("lettuce_iceberg", Decimal("0.80"), 1),  # Salade de saison
            ("carrot", Decimal("0.85"), 1),  # Carottes nouvelles
            ("onion", Decimal("0.90"), 0),  # Oignons nouveaux
        ]

        for veg_id, price_mult, quality_bonus in spring_vegetables:
            self.seasonal_modifiers.append(
                SeasonalModifier(
                    ingredient_id=veg_id,
                    season=Season.SPRING,
                    price_multiplier=price_mult,
                    quality_bonus=quality_bonus,
                    availability_multiplier=Decimal("1.2"),
                    demand_multiplier=Decimal("1.1"),
                )
            )

        # === LÉGUMES D'ÉTÉ ===
        summer_vegetables = [
            ("tomato", Decimal("0.70"), 2),  # Tomates de saison
            ("bell_pepper", Decimal("0.75"), 1),  # Poivrons d'été
            ("lettuce_iceberg", Decimal("0.85"), 1),  # Salades fraîches
        ]

        for veg_id, price_mult, quality_bonus in summer_vegetables:
            self.seasonal_modifiers.append(
                SeasonalModifier(
                    ingredient_id=veg_id,
                    season=Season.SUMMER,
                    price_multiplier=price_mult,
                    quality_bonus=quality_bonus,
                    availability_multiplier=Decimal("1.3"),
                    demand_multiplier=Decimal("1.2"),  # Plus de salades en été
                )
            )

        # === LÉGUMES D'AUTOMNE ===
        autumn_vegetables = [
            ("mushroom", Decimal("0.75"), 1),  # Champignons de saison
            ("potato", Decimal("0.80"), 1),  # Pommes de terre nouvelles
            ("carrot", Decimal("0.85"), 0),  # Légumes racines
        ]

        for veg_id, price_mult, quality_bonus in autumn_vegetables:
            self.seasonal_modifiers.append(
                SeasonalModifier(
                    ingredient_id=veg_id,
                    season=Season.AUTUMN,
                    price_multiplier=price_mult,
                    quality_bonus=quality_bonus,
                    availability_multiplier=Decimal("1.2"),
                    demand_multiplier=Decimal("1.15"),  # Plus de plats mijotés
                )
            )

        # === LÉGUMES D'HIVER (HORS SAISON) ===
        winter_penalties = [
            ("tomato", Decimal("1.40"), -1),  # Tomates hors saison
            ("bell_pepper", Decimal("1.30"), -1),  # Poivrons importés
            ("lettuce_iceberg", Decimal("1.20"), 0),  # Salades sous serre
        ]

        for veg_id, price_mult, quality_penalty in winter_penalties:
            self.seasonal_modifiers.append(
                SeasonalModifier(
                    ingredient_id=veg_id,
                    season=Season.WINTER,
                    price_multiplier=price_mult,
                    quality_bonus=quality_penalty,
                    availability_multiplier=Decimal("0.8"),
                    demand_multiplier=Decimal("0.8"),  # Moins de salades en hiver
                )
            )

        # === ÉVÉNEMENTS SPÉCIAUX ===

        # Fêtes de fin d'année
        self.event_modifiers.extend(
            [
                EventModifier(
                    "salmon_fillet",
                    SpecialEvent.CHRISTMAS,
                    12,
                    1,
                    Decimal("1.50"),
                    Decimal("1.8"),
                ),
                EventModifier(
                    "cheese_goat",
                    SpecialEvent.CHRISTMAS,
                    12,
                    1,
                    Decimal("1.30"),
                    Decimal("1.5"),
                ),
            ]
        )

        # Pâques
        self.event_modifiers.append(
            EventModifier(
                "egg", SpecialEvent.EASTER, 3, 4, Decimal("1.20"), Decimal("1.3")
            )
        )

        # Canicule (impact sur les salades)
        self.event_modifiers.extend(
            [
                EventModifier(
                    "lettuce_iceberg",
                    SpecialEvent.HEATWAVE,
                    7,
                    8,
                    Decimal("1.10"),
                    Decimal("1.4"),
                ),
                EventModifier(
                    "tomato",
                    SpecialEvent.HEATWAVE,
                    7,
                    8,
                    Decimal("1.05"),
                    Decimal("1.3"),
                ),
            ]
        )

        # Rentrée (légumes)
        self.event_modifiers.append(
            EventModifier(
                "potato",
                SpecialEvent.BACK_TO_SCHOOL,
                9,
                9,
                Decimal("1.20"),
                Decimal("1.2"),
            )
        )

    def get_current_season(self, current_date: Optional[date] = None) -> Season:
        """Détermine la saison actuelle."""
        if current_date is None:
            current_date = date.today()

        month = current_date.month

        if 3 <= month <= 5:
            return Season.SPRING
        elif 6 <= month <= 8:
            return Season.SUMMER
        elif 9 <= month <= 11:
            return Season.AUTUMN
        else:  # 12, 1, 2
            return Season.WINTER

    def get_seasonal_modifier(
        self, ingredient_id: str, current_date: Optional[date] = None
    ) -> Optional[SeasonalModifier]:
        """Retourne le modificateur saisonnier pour un ingrédient."""
        current_season = self.get_current_season(current_date)

        for modifier in self.seasonal_modifiers:
            if (
                modifier.ingredient_id == ingredient_id
                and modifier.season == current_season
            ):
                return modifier

        return None

    def get_active_event_modifiers(
        self, ingredient_id: str, current_date: Optional[date] = None
    ) -> List[EventModifier]:
        """Retourne les modificateurs d'événements actifs pour un ingrédient."""
        if current_date is None:
            current_date = date.today()

        current_month = current_date.month
        active_modifiers = []

        for modifier in self.event_modifiers:
            if modifier.ingredient_id == ingredient_id and modifier.is_active(
                current_month
            ):
                active_modifiers.append(modifier)

        return active_modifiers

    def calculate_final_price(
        self,
        ingredient_id: str,
        base_price: Decimal,
        current_date: Optional[date] = None,
    ) -> Decimal:
        """
        Calcule le prix final d'un ingrédient avec saisonnalité et événements.

        Args:
            ingredient_id: ID de l'ingrédient
            base_price: Prix de base
            current_date: Date actuelle (optionnel)

        Returns:
            Prix final avec modificateurs
        """
        final_price = base_price

        # Application du modificateur saisonnier
        seasonal_mod = self.get_seasonal_modifier(ingredient_id, current_date)
        if seasonal_mod:
            final_price *= seasonal_mod.price_multiplier

        # Application des modificateurs d'événements
        event_mods = self.get_active_event_modifiers(ingredient_id, current_date)
        for event_mod in event_mods:
            final_price *= event_mod.price_multiplier

        return final_price

    def get_quality_bonus(
        self, ingredient_id: str, current_date: Optional[date] = None
    ) -> int:
        """Retourne le bonus de qualité saisonnier."""
        seasonal_mod = self.get_seasonal_modifier(ingredient_id, current_date)
        return seasonal_mod.quality_bonus if seasonal_mod else 0

    def get_availability_multiplier(
        self, ingredient_id: str, current_date: Optional[date] = None
    ) -> Decimal:
        """Retourne le multiplicateur de disponibilité."""
        seasonal_mod = self.get_seasonal_modifier(ingredient_id, current_date)
        return seasonal_mod.availability_multiplier if seasonal_mod else Decimal("1.0")

    def get_demand_impact(
        self, ingredient_id: str, current_date: Optional[date] = None
    ) -> Decimal:
        """Calcule l'impact total sur la demande (saisonnier + événements)."""
        demand_multiplier = Decimal("1.0")

        # Impact saisonnier
        seasonal_mod = self.get_seasonal_modifier(ingredient_id, current_date)
        if seasonal_mod:
            demand_multiplier *= seasonal_mod.demand_multiplier

        # Impact des événements
        event_mods = self.get_active_event_modifiers(ingredient_id, current_date)
        for event_mod in event_mods:
            demand_multiplier *= event_mod.demand_multiplier

        return demand_multiplier

    def get_seasonal_summary(self, current_date: Optional[date] = None) -> Dict:
        """Retourne un résumé de la situation saisonnière actuelle."""
        if current_date is None:
            current_date = date.today()

        current_season = self.get_current_season(current_date)

        # Ingrédients en saison (prix réduits)
        in_season = []
        out_of_season = []

        for modifier in self.seasonal_modifiers:
            if modifier.season == current_season:
                if modifier.price_multiplier < 1:
                    in_season.append(
                        {
                            "ingredient_id": modifier.ingredient_id,
                            "discount": (1 - modifier.price_multiplier) * 100,
                            "quality_bonus": modifier.quality_bonus,
                        }
                    )
                elif modifier.price_multiplier > 1:
                    out_of_season.append(
                        {
                            "ingredient_id": modifier.ingredient_id,
                            "surcharge": (modifier.price_multiplier - 1) * 100,
                            "quality_penalty": modifier.quality_bonus,
                        }
                    )

        # Événements actifs
        active_events = []
        for modifier in self.event_modifiers:
            if modifier.is_active(current_date.month):
                active_events.append(
                    {
                        "ingredient_id": modifier.ingredient_id,
                        "event": modifier.event.value,
                        "price_impact": (modifier.price_multiplier - 1) * 100,
                        "demand_impact": (modifier.demand_multiplier - 1) * 100,
                    }
                )

        return {
            "season": current_season.value,
            "month": current_date.month,
            "in_season": in_season,
            "out_of_season": out_of_season,
            "active_events": active_events,
        }
