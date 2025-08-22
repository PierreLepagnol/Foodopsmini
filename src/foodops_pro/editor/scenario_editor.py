"""Éditeur de scénarios interactif pour FoodOps Pro.

Ce module propose un petit utilitaire CLI permettant de générer un fichier
YAML décrivant un scénario de jeu. L'utilisateur peut définir rapidement le
marché, la concurrence et sélectionner des événements provenant de la
bibliothèque d'événements.
"""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
from typing import Dict, List

import yaml

from ..domain.scenario import Scenario, MarketSegment
from ..domain.restaurant import RestaurantType


def _prompt_segments() -> Dict[str, Dict[str, float]]:
    """Demande à l'utilisateur de saisir les segments de marché."""
    segments: Dict[str, Dict[str, float]] = {}
    count = int(input("Nombre de segments de marché: "))
    for i in range(count):
        print(f"Segment {i+1}")
        name = input("  Nom: ")
        size = int(input("  Taille du segment: "))
        budget = float(input("  Budget moyen: "))
        price = float(input("  Sensibilité prix (0-2): "))
        quality = float(input("  Sensibilité qualité (0-2): "))
        segments[name] = {
            "size": size,
            "budget": budget,
            "price_sensitivity": price,
            "quality_sensitivity": quality,
        }
    return segments


def create_scenario() -> tuple[Scenario, List[str]]:
    """Collecte les informations et crée un objet :class:`Scenario`.

    Returns
    -------
    tuple
        Le scénario créé et la liste d'ID d'événements sélectionnés.
    """
    name = input("Nom du scénario: ")
    description = input("Description: ")
    turns = int(input("Nombre de tours: "))
    base_demand = int(input("Demande de base: "))
    demand_noise = Decimal("0.10")
    ai_competitors = int(input("Nombre de concurrents IA: "))

    segments_data = _prompt_segments()
    total_size = sum(d["size"] for d in segments_data.values()) or 1
    segments: List[MarketSegment] = []
    for seg_name, data in segments_data.items():
        share = Decimal(data["size"]) / Decimal(total_size)
        segments.append(
            MarketSegment(
                name=seg_name,
                share=share,
                budget=Decimal(str(data["budget"])),
                type_affinity={RestaurantType.CLASSIC: Decimal("1.0")},
                price_sensitivity=Decimal(str(data["price_sensitivity"])),
                quality_sensitivity=Decimal(str(data["quality_sensitivity"])),
            )
        )

    scenario = Scenario(
        name=name,
        description=description,
        turns=turns,
        base_demand=base_demand,
        demand_noise=demand_noise,
        segments=segments,
        ai_competitors=ai_competitors,
    )
    events_raw = input(
        "ID d'événements (séparés par des virgules, optionnel): "
    )
    event_ids = [e.strip() for e in events_raw.split(",") if e.strip()]
    return scenario, event_ids


def save_scenario(scenario: Scenario, events: List[str], path: Path) -> None:
    """Sauvegarde le scénario dans un fichier YAML."""
    data = asdict(scenario)
    # Conversion des Decimal en float pour YAML
    def _convert(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert(v) for v in obj]
        return obj

    cleaned = _convert(data)
    if events:
        cleaned["events"] = events
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(cleaned, f, allow_unicode=True, sort_keys=False)


def main() -> None:
    """Point d'entrée CLI."""
    scenario, events = create_scenario()
    default_path = Path(f"{scenario.name.replace(' ', '_').lower()}.yaml")
    target = input(f"Chemin de sauvegarde [{default_path}]: ") or str(default_path)
    save_scenario(scenario, events, Path(target))
    print(f"Scénario sauvegardé dans {target}")


if __name__ == "__main__":  # pragma: no cover - CLI
    main()
