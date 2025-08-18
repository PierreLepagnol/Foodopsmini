# -*- coding: utf-8 -*-
"""
FOODOPS MINI – Prototype jouable en 1 fichier
Objectif : faire tester très vite un business game de gestion de restaurant (tour par tour, multi-joueurs sur la même console).

Ce prototype implémente :
- 2 types de restaurants (fast / classique) avec vitesses et coûts différents
- Décisions par tour : prix TTC, niveau de staffing (0=fermé, 1=léger, 2=normal, 3=renforcé)
- Marché avec 3 segments (budget & affinité par type) + tolérance au dépassement de budget
- Allocation de la demande par score d'attraction (prix vs budget + affinité type)
- Capacité limitée (capacité brute × vitesse × coefficient staffing)
- Redistribution simple si certains restos saturent et que d'autres ont de la marge
- P&L simplifié par tour (CA, COGS, staff, fixes, résultat) + cash cumulé

Dépendances : Python 3.10+, aucune lib externe
Lancer :  python foodops_mini.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math
import random

# =====================
# Paramètres du jeu
# =====================

TURNS = 12
BASE_DEMAND = 420  # couverts/clients potentiels par tour (avant bruit)
DEMAND_NOISE = 0.08  # ±8% de bruit de demande
BUDGET_TOL = 1.15  # au-delà de budget * TOL, le client n'envisage pas le resto

# Types de restaurants (capacités et coûts indicatifs, modifiables)
RESTAURANT_TYPES: Dict[str, dict] = {
    "fast": {
        "label": "Fast-food",
        "base_capacity": 120,      # couverts/tour (avant vitesse/staff)
        "speed": 1.40,             # facteur vitesse de service
        "cogs_rate": 0.32,         # % du CA en coût matières
        "staff_costs": {1: 1800, 2: 2600, 3: 3400},
        "fixed_cost": 1200,        # loyer + charges fixes/tour
        "suggested_price": 11.5,
    },
    "classic": {
        "label": "Classique",
        "base_capacity": 60,
        "speed": 1.00,
        "cogs_rate": 0.36,
        "staff_costs": {1: 2200, 2: 3200, 3: 4200},
        "fixed_cost": 1800,
        "suggested_price": 17.0,
    },
}

# Coefficient de capacité selon staffing choisi
STAFF_CAPACITY: Dict[int, float] = {0: 0.0, 1: 0.70, 2: 1.00, 3: 1.30}

# Segments de clientèle (parts de marché, budget, affinité par type)
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

# =====================
# Modèle
# =====================

@dataclass
class Restaurant:
    name: str
    type_key: str  # "fast" ou "classic"
    cash: float = 0.0
    history: List[dict] = field(default_factory=list)

    # Décisions du tour courant (remises à zéro à chaque tour dans la boucle de jeu)
    price: float = 0.0
    staff_level: int = 0  # 0..3

    def cfg(self) -> dict:
        return RESTAURANT_TYPES[self.type_key]

    def capacity_this_turn(self) -> int:
        base = self.cfg()["base_capacity"]
        speed = self.cfg()["speed"]
        staff_mult = STAFF_CAPACITY.get(self.staff_level, 0.0)
        return math.floor(base * speed * staff_mult)

    def staff_cost(self) -> int:
        if self.staff_level == 0:
            return 0
        return int(self.cfg()["staff_costs"][self.staff_level])

    def fixed_cost(self) -> int:
        return int(self.cfg()["fixed_cost"])

    def cogs_rate(self) -> float:
        return float(self.cfg()["cogs_rate"])


# =====================
# Marché & allocation
# =====================

def price_factor(price: float, budget: float, tol: float = BUDGET_TOL) -> float:
    """Retourne un facteur d'attractivité lié au prix.
    - Si price > budget * tol -> 0 (inabordable pour le segment)
    - Si price <= budget      -> bonus modéré (jusqu'à +30%)
    - Entre budget et budget*tol -> décroissance linéaire vers 0.2
    """
    if price <= 0:
        return 0.0
    if price > budget * tol:
        return 0.0
    if price <= budget:
        bonus = min(0.30, (budget - price) / budget * 0.40)
        return 1.0 + bonus
    # zone de tolérance
    span = max(1e-6, budget * (tol - 1.0))
    drop = (price - budget) / span  # 0..1
    return max(0.20, 1.0 - drop)


def allocate_demand(restos: List[Restaurant], total_demand: int, rng: random.Random) -> Dict[str, dict]:
    """Alloue la demande par segment, calcule servi vs capacité, redistribue en 1 passe.
    Retour: {resto.name: {allocated, served, capacity}}
    """
    # 1) bruit
    noise = 1.0 + rng.uniform(-DEMAND_NOISE, DEMAND_NOISE)
    demand = int(round(total_demand * noise))

    # 2) demande par segment
    seg_demands = [int(round(demand * s["share"])) for s in SEGMENTS]

    # 3) scores par segment -> allocations brutes
    raw_alloc = {r.name: 0.0 for r in restos}
    for seg, seg_d in zip(SEGMENTS, seg_demands):
        scores = {}
        for r in restos:
            if r.staff_level == 0:
                scores[r.name] = 0.0
                continue
            w = seg["type_weight"][r.type_key]
            pf = price_factor(r.price, seg["budget"], BUDGET_TOL)
            scores[r.name] = w * pf
        total_score = sum(scores.values())
        if total_score <= 0:
            continue  # tout le monde trop cher/fermé -> clients perdus
        for r in restos:
            if scores[r.name] <= 0:
                continue
            raw_alloc[r.name] += seg_d * (scores[r.name] / total_score)

    # 4) capacité et premier passage de service
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

    # 5) redistribution simple des pénuries vers les restos avec capacité libre
    if total_shortage > 0 and total_spare > 0:
        redistribute = min(total_shortage, total_spare)
        # répartir proportionnellement à la capacité libre
        spare_sum = sum(v["spare"] for v in result.values())
        if spare_sum > 0:
            for r in restos:
                add = int(round(redistribute * (result[r.name]["spare"] / spare_sum)))
                # pas dépasser la capacité
                possible = min(add, result[r.name]["capacity"] - result[r.name]["served"])
                result[r.name]["served"] += possible

    return result


# =====================
# P&L simplifié
# =====================

def compute_pnl(r: Restaurant, served: int) -> dict:
    ca = r.price * served
    cogs = ca * r.cogs_rate()
    staff = r.staff_cost()
    fixed = r.fixed_cost()
    ebit = ca - cogs - staff - fixed
    return {
        "revenue": ca,
        "cogs": cogs,
        "staff": staff,
        "fixed": fixed,
        "profit": ebit,
    }


# =====================
# Interface console
# =====================

def ask_int(prompt: str, min_v: int, max_v: int) -> int:
    while True:
        try:
            v = int(input(prompt).strip())
            if min_v <= v <= max_v:
                return v
        except ValueError:
            pass
        print(f"→ Entrez un entier entre {min_v} et {max_v}")


def ask_float(prompt: str, min_v: float, max_v: float) -> float:
    while True:
        try:
            v = float(input(prompt).strip().replace(",", "."))
            if min_v <= v <= max_v:
                return v
        except ValueError:
            pass
        print(f"→ Entrez un nombre entre {min_v} et {max_v}")


def print_turn_header(turn: int, demand_hint: int):
    print("\n" + "=" * 70)
    print(f"TOUR {turn} — Demande attendue ≈ {demand_hint} couverts (+/- {int(DEMAND_NOISE*100)}%)")
    print("Segments : ")
    for s in SEGMENTS:
        print(
            f"  - {s['name']}: {int(s['share']*100)}% (budget ~ {s['budget']:.1f}€)"
        )
    print("=" * 70)


def print_scoreboard(restos: List[Restaurant], alloc: Dict[str, dict]):
    print("\nRésultats du tour :")
    print("-" * 70)
    print(f"{'Resto':16} | {'Cap.':>4} | {'Alloc.':>6} | {'Servi':>5} | {'Util.':>5} | {'CA €':>10} | {'Résultat €':>11}")
    print("-" * 70)
    for r in restos:
        served = alloc[r.name]["served"]
        cap = alloc[r.name]["capacity"]
        pnl = compute_pnl(r, served)
        util = 0 if cap == 0 else int(round(100 * served / cap))
        print(
            f"{r.name:16} | {cap:>4} | {alloc[r.name]['allocated']:>6} | {served:>5} | {util:>4}% | "
            f"{pnl['revenue']:>10.0f} | {pnl['profit']:>11.0f}"
        )
    print("-" * 70)


def run_game():
    print("FOODOPS MINI — Simulation de gestion de restaurant")
    print("(Prototype simplifié • 2 types : fast / classique)\n")

    rng = random.Random(42)

    # Création des joueurs
    n_players = ask_int("Combien de joueurs (1-4) ? ", 1, 4)
    restos: List[Restaurant] = []

    for i in range(1, n_players + 1):
        name = input(f"Nom du restaurant {i} ? ").strip() or f"Resto{i}"
        tsel = None
        while tsel not in ("fast", "classic"):
            tsel = input("Type ('fast' ou 'classic') ? ").strip().lower()
        r = Restaurant(name=name, type_key=tsel)
        restos.append(r)

    # Boucle de jeu
    for turn in range(1, TURNS + 1):
        print_turn_header(turn, BASE_DEMAND)

        # Décisions
        for r in restos:
            cfg = r.cfg()
            suggestion = cfg["suggested_price"]
            print(f"\n{r.name} ({cfg['label']})")
            r.price = ask_float(
                f"  Prix TTC (€) [ex. {suggestion:.1f}] ? ", 5.0, 40.0
            )
            r.staff_level = ask_int("  Staffing 0=fermé,1=léger,2=normal,3=renforcé ? ", 0, 3)

        # Marché
        alloc = allocate_demand(restos, BASE_DEMAND, rng)

        # Comptes
        for r in restos:
            served = alloc[r.name]["served"]
            pnl = compute_pnl(r, served)
            r.cash += pnl["profit"]
            # journal
            r.history.append({
                "turn": turn,
                "price": r.price,
                "staff": r.staff_level,
                "served": served,
                **pnl,
            })

        # Affichage tour
        print_scoreboard(restos, alloc)
        print("\nCash cumulé :")
        for r in restos:
            print(f"  - {r.name}: {r.cash:.0f} €")

    # Fin de partie
    print("\n" + "#" * 70)
    print("FIN DE PARTIE — Classement par cash cumulé")
    ranking = sorted(restos, key=lambda x: x.cash, reverse=True)
    for i, r in enumerate(ranking, start=1):
        print(f"{i}. {r.name:<16}  {r.cash:>10.0f} €")


if __name__ == "__main__":
    run_game()
