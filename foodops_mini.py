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
BUDGET_TOL = 1.15

# === NOUVEAUX SYSTÈMES ===

# Système de qualité simplifié pour intégration
QUALITY_LEVELS = {
    1: {"name": "Économique", "cost_mult": 0.70, "satisfaction": -0.20},
    2: {"name": "Standard", "cost_mult": 1.00, "satisfaction": 0.00},
    3: {"name": "Supérieur", "cost_mult": 1.25, "satisfaction": 0.15},
    4: {"name": "Premium", "cost_mult": 1.50, "satisfaction": 0.30},
    5: {"name": "Luxe", "cost_mult": 2.00, "satisfaction": 0.50}
}

# Saisonnalité simplifiée (mois actuel)
SEASONAL_BONUSES = {
    "Étudiants": {1: 0.9, 2: 0.9, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.1, 7: 1.2, 8: 1.2, 9: 1.0, 10: 1.0, 11: 0.9, 12: 0.9},
    "Familles": {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.1, 5: 1.1, 6: 1.2, 7: 1.3, 8: 1.3, 9: 1.0, 10: 1.0, 11: 1.0, 12: 1.1},
    "Foodies": {1: 1.0, 2: 1.0, 3: 1.1, 4: 1.2, 5: 1.2, 6: 1.1, 7: 1.0, 8: 1.0, 9: 1.1, 10: 1.2, 11: 1.1, 12: 1.2}
}  # au-delà de budget * TOL, le client n'envisage pas le resto

# Types de restaurants (capacités et coûts indicatifs, modifiables)
RESTAURANT_TYPES: Dict[str, dict] = {
    "fast": {
        "label": "Fast-food",
        "base_capacity": 120,      # couverts/tour (avant vitesse/staff)
        "speed": 1.40,             # facteur vitesse de service
        "cogs_rate": 0.32,         # % du CA en coût matières
        "staff_costs": {1: 58, 2: 100, 3: 142},  # Coûts réalistes par service
        "fixed_cost": 92,          # loyer + charges fixes/tour (5500€/mois ÷ 60)
        "suggested_price": 11.5,
    },
    "classic": {
        "label": "Classique",
        "base_capacity": 60,
        "speed": 1.00,
        "cogs_rate": 0.36,
        "staff_costs": {1: 75, 2: 133, 3: 192},  # Coûts réalistes par service
        "fixed_cost": 128,         # loyer + charges fixes/tour (7700€/mois ÷ 60)
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

    # NOUVEAUX: Système qualité et réputation
    quality_level: float = 2.0  # Score qualité 1.0-5.0
    reputation: float = 5.0  # Réputation 0.0-10.0
    ingredient_choices: dict = field(default_factory=dict)  # Choix d'ingrédients par qualité

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
        base_cogs = float(self.cfg()["cogs_rate"])
        # Ajustement selon la qualité des ingrédients
        quality_adjustment = (self.quality_level - 2.0) * 0.05  # ±5% par niveau
        return max(0.1, base_cogs + quality_adjustment)

    def set_ingredient_quality(self, ingredient_type: str, quality_level: int) -> None:
        """Définit le niveau de qualité pour un type d'ingrédient."""
        self.ingredient_choices[ingredient_type] = quality_level
        self._update_overall_quality()

    def _update_overall_quality(self) -> None:
        """Met à jour le score de qualité global basé sur les choix d'ingrédients."""
        if not self.ingredient_choices:
            return

        # Score moyen des ingrédients choisis
        avg_ingredient_quality = sum(self.ingredient_choices.values()) / len(self.ingredient_choices)

        # Score de base selon le type de restaurant
        base_quality = {
            "fast": 1.5,
            "classic": 2.5,
            "gastronomique": 3.5
        }.get(self.type_key, 2.0)

        # Bonus staff (formation)
        staff_bonus = (self.staff_level - 1) * 0.3

        # Score final
        self.quality_level = min(5.0, max(1.0, base_quality + (avg_ingredient_quality - 2.0) * 0.8 + staff_bonus))

    def update_reputation(self, customer_satisfaction: float) -> None:
        """Met à jour la réputation basée sur la satisfaction client."""
        # Évolution lente de la réputation (10% du delta)
        target_reputation = customer_satisfaction * 2  # Satisfaction 0-5 -> Réputation 0-10
        self.reputation += (target_reputation - self.reputation) * 0.1
        self.reputation = max(0.0, min(10.0, self.reputation))

    def get_quality_description(self) -> str:
        """Retourne une description textuelle de la qualité."""
        if self.quality_level >= 4.5:
            return "⭐⭐⭐⭐⭐ Luxe"
        elif self.quality_level >= 3.5:
            return "⭐⭐⭐⭐ Premium"
        elif self.quality_level >= 2.5:
            return "⭐⭐⭐ Supérieur"
        elif self.quality_level >= 1.5:
            return "⭐⭐ Standard"
        else:
            return "⭐ Économique"


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


def get_seasonal_demand_bonus(segment_name: str) -> float:
    """Retourne le bonus de demande saisonnier pour un segment."""
    import datetime
    current_month = datetime.date.today().month
    return SEASONAL_BONUSES.get(segment_name, {}).get(current_month, 1.0)


def get_restaurant_quality_score(restaurant) -> float:
    """Calcule le score de qualité d'un restaurant (1.0 à 5.0)."""
    # Pour l'instant, score basé sur le type et le niveau de staff
    # Plus tard: basé sur les ingrédients choisis
    base_quality = {
        "fast": 2.0,
        "classic": 3.0,
        "gastronomique": 4.0
    }.get(restaurant.type_key, 2.5)

    # Bonus selon le niveau de staff (formation)
    staff_bonus = (restaurant.staff_level - 1) * 0.3

    # Simuler l'impact des ingrédients (à remplacer par le vrai système)
    ingredient_bonus = getattr(restaurant, 'quality_level', 0) * 0.5

    return min(5.0, base_quality + staff_bonus + ingredient_bonus)


def get_quality_attractiveness_factor(quality_score: float, segment: dict) -> float:
    """Calcule l'impact de la qualité sur l'attractivité selon le segment."""
    # Sensibilité à la qualité par segment
    quality_sensitivity = {
        "Étudiants": 0.5,    # Moins sensibles à la qualité
        "Familles": 1.0,     # Sensibilité normale
        "Foodies": 1.5       # Très sensibles à la qualité
    }.get(segment["name"], 1.0)

    # Conversion score qualité (1-5) en facteur attractivité
    if quality_score <= 1.5:
        base_factor = 0.80  # -20%
    elif quality_score <= 2.5:
        base_factor = 1.00  # Neutre
    elif quality_score <= 3.5:
        base_factor = 1.15  # +15%
    elif quality_score <= 4.5:
        base_factor = 1.30  # +30%
    else:
        base_factor = 1.50  # +50%

    # Ajustement selon la sensibilité du segment
    if base_factor > 1.0:
        bonus = (base_factor - 1.0) * quality_sensitivity
        return 1.0 + bonus
    else:
        malus = (1.0 - base_factor) * quality_sensitivity
        return 1.0 - malus


def get_reputation_factor(restaurant) -> float:
    """Calcule le facteur de réputation d'un restaurant."""
    # Réputation de base selon le type
    base_reputation = getattr(restaurant, 'reputation', 5.0)  # Sur 10

    # Conversion en facteur (5.0 = neutre)
    if base_reputation >= 8.0:
        return 1.20  # +20% pour excellente réputation
    elif base_reputation >= 6.0:
        return 1.10  # +10% pour bonne réputation
    elif base_reputation >= 4.0:
        return 1.00  # Neutre
    elif base_reputation >= 2.0:
        return 0.90  # -10% pour mauvaise réputation
    else:
        return 0.80  # -20% pour très mauvaise réputation


def allocate_demand(restos: List[Restaurant], total_demand: int, rng: random.Random) -> Dict[str, dict]:
    """Alloue la demande par segment avec qualité, saisonnalité et réputation.
    Retour: {resto.name: {allocated, served, capacity, quality_score, reputation}}
    """
    # 1) bruit sur la demande
    noise = 1.0 + rng.uniform(-DEMAND_NOISE, DEMAND_NOISE)
    demand = int(round(total_demand * noise))

    # 2) demande par segment avec saisonnalité
    seg_demands = []
    for s in SEGMENTS:
        base_demand = int(round(demand * s["share"]))
        # Bonus saisonnier (simulé)
        seasonal_bonus = get_seasonal_demand_bonus(s["name"])
        seasonal_demand = int(base_demand * seasonal_bonus)
        seg_demands.append(seasonal_demand)

    # 3) scores par segment avec qualité et réputation
    raw_alloc = {r.name: 0.0 for r in restos}
    for seg, seg_d in zip(SEGMENTS, seg_demands):
        scores = {}
        for r in restos:
            if r.staff_level == 0:
                scores[r.name] = 0.0
                continue

            # Facteurs traditionnels
            w = seg["type_weight"][r.type_key]
            pf = price_factor(r.price, seg["budget"], BUDGET_TOL)

            # NOUVEAU: Facteur qualité
            quality_score = get_restaurant_quality_score(r)
            quality_factor = get_quality_attractiveness_factor(quality_score, seg)

            # NOUVEAU: Facteur réputation
            reputation_factor = get_reputation_factor(r)

            # Score final intégré
            scores[r.name] = w * pf * quality_factor * reputation_factor

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

    # NOUVEAU: Calcul de la satisfaction client
    quality_score = get_restaurant_quality_score(r)
    price_quality_ratio = r.price / max(1.0, quality_score)  # Prix par étoile de qualité

    # Satisfaction basée sur qualité vs prix (0-5)
    if price_quality_ratio <= 2.0:  # Excellent rapport qualité/prix
        customer_satisfaction = 5.0
    elif price_quality_ratio <= 3.0:  # Bon rapport
        customer_satisfaction = 4.0
    elif price_quality_ratio <= 4.0:  # Correct
        customer_satisfaction = 3.0
    elif price_quality_ratio <= 5.0:  # Cher
        customer_satisfaction = 2.0
    else:  # Très cher
        customer_satisfaction = 1.0

    # Mise à jour de la réputation
    r.update_reputation(customer_satisfaction)

    return {
        "revenue": ca,
        "cogs": cogs,
        "staff": staff,
        "fixed": fixed,
        "profit": ebit,
        "quality_score": quality_score,
        "customer_satisfaction": customer_satisfaction,
        "reputation": r.reputation,
        "price_quality_ratio": price_quality_ratio,
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
    print("-" * 100)
    print(f"{'Resto':16} | {'Cap.':>4} | {'Servi':>5} | {'Util.':>5} | {'CA €':>8} | {'Résultat €':>9} | {'Qualité':>8} | {'Satisf.':>7} | {'Réputation':>10}")
    print("-" * 100)
    for r in restos:
        served = alloc[r.name]["served"]
        cap = alloc[r.name]["capacity"]
        pnl = compute_pnl(r, served)
        util = 0 if cap == 0 else int(round(100 * served / cap))

        # Nouvelles métriques
        quality_stars = "⭐" * int(pnl['quality_score'])
        satisfaction = f"{pnl['customer_satisfaction']:.1f}/5"
        reputation = f"{pnl['reputation']:.1f}/10"

        print(
            f"{r.name:16} | {cap:>4} | {served:>5} | {util:>4}% | "
            f"{pnl['revenue']:>8.0f} | {pnl['profit']:>9.0f} | {quality_stars:>8} | {satisfaction:>7} | {reputation:>10}"
        )
    print("-" * 100)

    # Affichage détaillé de la qualité
    print("\nDÉTAIL QUALITÉ:")
    for r in restos:
        pnl = compute_pnl(r, alloc[r.name]["served"])
        print(f"  {r.name}: {r.get_quality_description()} (Ratio prix/qualité: {pnl['price_quality_ratio']:.1f}€/⭐)")
        if r.ingredient_choices:
            ingredients_desc = ", ".join([f"{k}:{v}⭐" for k, v in r.ingredient_choices.items()])
            print(f"    Ingrédients: {ingredients_desc}")
    print()


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
            print(f"\n{r.name} ({cfg['label']}) - Qualité actuelle: {r.get_quality_description()}")
            print(f"  Réputation: {r.reputation:.1f}/10")

            r.price = ask_float(
                f"  Prix TTC (€) [ex. {suggestion:.1f}] ? ", 5.0, 40.0
            )
            r.staff_level = ask_int("  Staffing 0=fermé,1=léger,2=normal,3=renforcé ? ", 0, 3)

            # NOUVEAU: Choix de qualité des ingrédients
            if turn == 1 or input("  Modifier la qualité des ingrédients ? (o/N) ").lower().startswith('o'):
                print("  Qualité des ingrédients principaux:")
                print("    1=⭐ Économique (-30% coût, -20% satisfaction)")
                print("    2=⭐⭐ Standard (prix normal)")
                print("    3=⭐⭐⭐ Supérieur (+25% coût, +15% satisfaction)")
                print("    4=⭐⭐⭐⭐ Premium (+50% coût, +30% satisfaction)")
                print("    5=⭐⭐⭐⭐⭐ Luxe (+100% coût, +50% satisfaction)")

                meat_quality = ask_int("    Viande (1-5) ? ", 1, 5)
                vegetable_quality = ask_int("    Légumes (1-5) ? ", 1, 5)

                r.set_ingredient_quality("meat", meat_quality)
                r.set_ingredient_quality("vegetables", vegetable_quality)

                print(f"    → Nouvelle qualité globale: {r.get_quality_description()}")
                print(f"    → Nouveau coût matières: {r.cogs_rate():.1%}")

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
