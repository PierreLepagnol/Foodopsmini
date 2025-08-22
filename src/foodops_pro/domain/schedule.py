"""Structures de planification hebdomadaire et jours spéciaux."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class SpecialDay:
    """Décrit un événement spécial impactant l'activité."""

    date: date
    event_type: str
    expected_impact: Decimal


@dataclass
class WeeklySchedule:
    """Planification hebdomadaire avec journées spéciales."""

    special_days: list[SpecialDay] = field(default_factory=list)

    def get_special_day(self, day: date) -> SpecialDay | None:
        """Retourne l'événement spécial prévu pour une date."""
        for sd in self.special_days:
            if sd.date == day:
                return sd
        return None

    def get_expected_impact(self, day: date) -> Decimal:
        """Facteur multiplicatif de fréquentation pour la date donnée."""
        sd = self.get_special_day(day)
        return sd.expected_impact if sd else Decimal("1.0")
