"""Gestion simple d'une suite de missions pour FoodOps Pro."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml

from .scenario import Scenario
from ..io.data_loader import DataLoader


@dataclass
class Mission:
    """Représente une mission avec son scénario et ses objectifs."""

    name: str
    scenario: Scenario
    objectives: Dict[str, float]


@dataclass
class MissionSeries:
    """Suite ordonnée de missions à accomplir."""

    missions: List[Mission]
    current_index: int = 0

    def current(self) -> Mission:
        return self.missions[self.current_index]

    def advance(self) -> bool:
        if self.current_index < len(self.missions) - 1:
            self.current_index += 1
            return True
        return False


def load_mission_series(path: Path) -> MissionSeries:
    """Charge une série de missions depuis un fichier YAML."""
    loader = DataLoader()
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    missions: List[Mission] = []
    for item in data.get("missions", []):
        scenario_path = path.parent / item["scenario"]
        scenario = loader.load_scenario(scenario_path)
        missions.append(
            Mission(
                name=item["name"],
                scenario=scenario,
                objectives=item.get("objectives", {}),
            )
        )

    return MissionSeries(missions)
