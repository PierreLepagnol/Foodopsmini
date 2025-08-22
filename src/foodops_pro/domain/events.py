from __future__ import annotations

"""Définition et chargement d'événements de jeu."""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML optionnel
    yaml = None


@dataclass(frozen=True)
class Event:
    """Représente un événement affectant la partie."""

    id: str
    name: str
    description: str
    demand_factor: Decimal = Decimal("1.0")
    cost_factor: Decimal = Decimal("1.0")


class EventBank:
    """Banque d'événements chargés depuis un fichier YAML."""

    def __init__(self, events: Dict[str, Event]) -> None:
        self._events = events

    def get(self, event_id: str) -> Optional[Event]:
        """Retourne un événement par son identifiant."""
        return self._events.get(event_id)

    def list_events(self) -> List[Event]:
        """Retourne la liste des événements disponibles."""
        return list(self._events.values())

    @classmethod
    def from_yaml(cls, path: Path) -> "EventBank":
        """Charge une banque d'événements depuis un fichier YAML."""
        if yaml is None or not path.exists():
            return cls({})
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or []
        events: Dict[str, Event] = {}
        for item in data:
            event = Event(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                demand_factor=Decimal(str(item.get("demand_factor", 1.0))),
                cost_factor=Decimal(str(item.get("cost_factor", 1.0))),
            )
            events[event.id] = event
        return cls(events)
