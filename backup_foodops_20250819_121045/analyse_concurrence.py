#!/usr/bin/env python3
"""
Analyse détaillée du système de concurrence dans FoodOps Mini.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List

# Copie des constantes du jeu
BASE_DEMAND = 420
DEMAND_NOISE = 0.08
BUDGET_TOL = 1.15

SEGMENTS = [
    {
        "name": "Étudiants",
        "share": 0.35,
        "budget": 11.0,
        "type_weight": {"fast": 1.20, "classic": 0.70},
    },
    {
        "name": "Familles",
        "share": 0.40,
        "budget": 17.0,
        "type_weight": {"fast": 0.90, "classic": 1.00},
    },
    {
        "name": "Foodies",
        "share": 0.25,
        "budget": 25.0,
        "type_weight": {"fast": 0.60, "classic": 1.30},
    },
]

STAFF_CAPACITY = {0: 0.0, 1: 0.70, 2: 1.00, 3: 1.30}

RESTAURANT_TYPES = {
    "fast": {"base_capacity": 120, "speed": 1.40},
    "classic": {"base_capacity": 60, "speed": 1.00},
}


@dataclass
class Restaurant:
    name: str
    type_key: str
    price: float = 0.0
    staff_level: int = 2

    def capacity_this_turn(self) -> int:
        base = RESTAURANT_TYPES[self.type_key]["base_capacity"]
        speed = RESTAURANT_TYPES[self.type_key]["speed"]
        staff_coeff = STAFF_CAPACITY[self.staff_level]
        return int(base * speed * staff_coeff)


def price_factor(price: float, budget: float, tol: float = BUDGET_TOL) -> float:
    """Facteur d'attractivité basé sur le prix."""
    if price <= 0:
        return 0.0
    if price > budget * tol:
        return 0.0
    if price <= budget:
        bonus = min(0.30, (budget - price) / budget * 0.40)
        return 1.0 + bonus
    span = max(1e-6, budget * (tol - 1.0))
    drop = (price - budget) / span
    return max(0.20, 1.0 - drop)


def allocate_demand_detailed(
    restos: List[Restaurant], total_demand: int, rng: random.Random
) -> Dict:
    """Version détaillée de l'allocation avec analyse."""
    # Bruit sur la demande
    noise = 1.0 + rng.uniform(-DEMAND_NOISE, DEMAND_NOISE)
    demand = int(round(total_demand * noise))

    print(f"📊 ALLOCATION DE MARCHÉ")
    print(f"Demande de base: {total_demand}, avec bruit: {demand} ({noise:.2%})")

    # Demande par segment
    seg_demands = [int(round(demand * s["share"])) for s in SEGMENTS]

    print(f"\nRépartition par segment:")
    for seg, seg_d in zip(SEGMENTS, seg_demands):
        print(f"  {seg['name']}: {seg_d} clients (budget {seg['budget']}€)")

    # Analyse des scores par segment
    raw_alloc = {r.name: 0.0 for r in restos}
    segment_details = {}

    for seg, seg_d in zip(SEGMENTS, seg_demands):
        print(f"\n🎯 SEGMENT {seg['name']} ({seg_d} clients):")
        scores = {}

        for r in restos:
            if r.staff_level == 0:
                scores[r.name] = 0.0
                print(f"  {r.name}: FERMÉ")
                continue

            w = seg["type_weight"][r.type_key]
            pf = price_factor(r.price, seg["budget"], BUDGET_TOL)
            score = w * pf
            scores[r.name] = score

            print(f"  {r.name} ({r.type_key}): prix {r.price}€")
            print(f"    Affinité type: {w:.2f}")
            print(f"    Facteur prix: {pf:.2f}")
            print(f"    Score total: {score:.2f}")

        total_score = sum(scores.values())
        print(f"  Score total segment: {total_score:.2f}")

        if total_score <= 0:
            print(f"  ❌ Aucun restaurant attractif -> {seg_d} clients perdus")
            continue

        # Allocation proportionnelle
        segment_alloc = {}
        for r in restos:
            if scores[r.name] <= 0:
                segment_alloc[r.name] = 0
                continue
            alloc = seg_d * (scores[r.name] / total_score)
            segment_alloc[r.name] = alloc
            raw_alloc[r.name] += alloc
            print(f"    → {r.name}: {alloc:.1f} clients ({alloc / seg_d:.1%})")

        segment_details[seg["name"]] = segment_alloc

    # Contraintes de capacité
    print(f"\n🏪 CONTRAINTES DE CAPACITÉ:")
    result = {}
    total_shortage = 0.0
    total_spare = 0.0

    for r in restos:
        capacity = r.capacity_this_turn()
        allocated = int(round(raw_alloc[r.name]))
        served = min(allocated, capacity)
        shortage = max(0, allocated - capacity)
        spare = max(0, capacity - served)

        total_shortage += shortage
        total_spare += spare

        result[r.name] = {
            "allocated": allocated,
            "served": served,
            "capacity": capacity,
            "spare": spare,
        }

        status = "✅" if shortage == 0 else f"❌ -{shortage}"
        print(
            f"  {r.name}: {allocated} demandé, {capacity} capacité → {served} servi {status}"
        )

    # Redistribution
    if total_shortage > 0 and total_spare > 0:
        print(f"\n🔄 REDISTRIBUTION:")
        print(f"  Pénurie totale: {total_shortage:.0f}")
        print(f"  Capacité libre: {total_spare:.0f}")

        redistribute = min(total_shortage, total_spare)
        spare_sum = sum(v["spare"] for v in result.values())

        if spare_sum > 0:
            for r in restos:
                if result[r.name]["spare"] > 0:
                    add = int(
                        round(redistribute * (result[r.name]["spare"] / spare_sum))
                    )
                    possible = min(
                        add, result[r.name]["capacity"] - result[r.name]["served"]
                    )
                    result[r.name]["served"] += possible
                    print(f"    {r.name}: +{possible} clients redistribués")

    return {
        "results": result,
        "segment_details": segment_details,
        "total_demand": demand,
        "total_served": sum(r["served"] for r in result.values()),
    }


def test_concurrence_scenarios():
    """Teste différents scénarios de concurrence."""
    print("🎮 TEST DE SCÉNARIOS DE CONCURRENCE")
    print("=" * 60)

    rng = random.Random(42)

    scenarios = [
        {
            "name": "Prix similaires",
            "restos": [
                Restaurant("Quick Burger", "fast", 10.0, 2),
                Restaurant("Chez Papa", "classic", 16.0, 2),
            ],
        },
        {
            "name": "Guerre des prix",
            "restos": [
                Restaurant("Quick Burger", "fast", 8.0, 2),
                Restaurant("Chez Papa", "classic", 12.0, 2),
            ],
        },
        {
            "name": "Positionnement premium",
            "restos": [
                Restaurant("Quick Burger", "fast", 12.0, 3),
                Restaurant("Chez Papa", "classic", 20.0, 3),
            ],
        },
        {
            "name": "Concurrence directe (même type)",
            "restos": [
                Restaurant("Quick Burger", "fast", 10.0, 2),
                Restaurant("Speed Food", "fast", 9.5, 2),
                Restaurant("Chez Papa", "classic", 16.0, 2),
            ],
        },
    ]

    for scenario in scenarios:
        print(f"\n{'=' * 20} {scenario['name']} {'=' * 20}")
        result = allocate_demand_detailed(scenario["restos"], BASE_DEMAND, rng)

        print(f"\n📈 RÉSULTATS FINAUX:")
        total_ca = 0
        for resto in scenario["restos"]:
            resto_result = result["results"][resto.name]
            ca = resto_result["served"] * resto.price
            total_ca += ca
            market_share = (
                resto_result["served"] / result["total_served"] * 100
                if result["total_served"] > 0
                else 0
            )

            print(f"  {resto.name}:")
            print(f"    Clients servis: {resto_result['served']}")
            print(f"    Part de marché: {market_share:.1f}%")
            print(f"    CA: {ca:.0f}€")

        print(f"  CA total marché: {total_ca:.0f}€")
        print(f"  Clients perdus: {result['total_demand'] - result['total_served']}")


def analyze_competition_weaknesses():
    """Analyse les faiblesses du système de concurrence."""
    print("\n\n🔍 ANALYSE DES FAIBLESSES")
    print("=" * 50)

    print("❌ PROBLÈMES IDENTIFIÉS:")
    print("1. Allocation trop prévisible")
    print("   → Même prix = même résultat à chaque fois")
    print("   → Pas de variabilité dans les préférences clients")

    print("\n2. Segments trop rigides")
    print("   → Étudiants vont TOUJOURS au fast-food")
    print("   → Pas de crossover entre segments")

    print("\n3. Facteur prix trop dominant")
    print("   → Prix bas = victoire garantie")
    print("   → Autres facteurs (qualité, service) ignorés")

    print("\n4. Pas d'effets dynamiques")
    print("   → Pas de fidélisation client")
    print("   → Pas d'effet de réputation")
    print("   → Pas de saisonnalité")

    print("\n5. Redistribution simpliste")
    print("   → Clients refusés vont automatiquement ailleurs")
    print("   → Pas de perte définitive de clients")


def main():
    """Analyse complète du système de concurrence."""
    test_concurrence_scenarios()
    analyze_competition_weaknesses()


if __name__ == "__main__":
    main()
