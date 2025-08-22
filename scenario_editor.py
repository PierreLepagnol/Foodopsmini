"""Éditeur interactif de scénarios pour FoodOps Pro."""
from pathlib import Path
from typing import List

import yaml

from src.foodops_pro.io.data_loader import DataLoader


def prompt(text: str) -> str:
    try:
        return input(text)
    except EOFError:  # pragma: no cover
        return ""


def main() -> None:
    loader = DataLoader()
    events_bank = loader.load_events()

    name = prompt("Nom du scénario: ") or "Nouveau scénario"
    description = prompt("Description: ") or "Scénario généré"
    turns = int(prompt("Nombre de tours: ") or 6)
    base_demand = int(prompt("Demande de base: ") or 300)
    demand_noise = float(prompt("Variabilité demande (0-1): ") or 0.1)

    # Segments simples
    segment = {
        "name": "Général",
        "share": 1.0,
        "budget": 15.0,
        "price_sensitivity": 1.0,
        "quality_sensitivity": 1.0,
        "type_affinity": {
            "fast": 1.0,
            "classic": 1.0,
            "gastronomique": 1.0,
            "brasserie": 1.0,
        },
    }

    events: List[str] = []
    if events_bank.list_events():
        print("\nÉvénements disponibles:")
        for event in events_bank.list_events():
            print(f"- {event.id}: {event.name} - {event.description}")
        selected = prompt("Sélectionner des événements (ids séparés par des virgules): ")
        events = [e.strip() for e in selected.split(",") if events_bank.get(e.strip())]

    scenario = {
        "name": name,
        "description": description,
        "turns": turns,
        "base_demand": base_demand,
        "demand_noise": demand_noise,
        "segments": [segment],
        "events": events,
    }

    out_path = Path(prompt("Fichier de sortie (ex: nouveau.yaml): ") or "nouveau_scenario.yaml")
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(scenario, f, allow_unicode=True)
    print(f"Scénario sauvegardé dans {out_path}")


if __name__ == "__main__":
    main()
