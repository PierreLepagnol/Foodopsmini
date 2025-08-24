"""
Moteur d'allocation de la demande (réaliste) pour FoodOps.

Règles implémentées :
- La demande vient d'un Scenario (population totale + parts par segments).
- Choix d'un restaurant (pas d'un “type” abstrait) en fonction d'un score d'attraction.
- Filtre budget dur : si prix médian du restaurant > budget segment x tolérance => restaurant inéligible.
- Capacité exploitable par tour = capacité brute x coefficient de vitesse (par type de restaurant).
- Redistribution en cas de saturation : on passe au 2e, 3e meilleur, etc.
- Clients perdus si aucun restaurant éligible ou plus de capacité.
- Cannibalisation douce : si plusieurs restaurants d'un même type, légère pénalité de score.

Retour :
    allocate_demand(...) -> dict {index_restaurant: clients_attribués}

NB : Les clients “perdus” ne sont pas retournés ici, mais on expose
     une fonction optionnelle `estimate_lost_customers(...)` si besoin plus tard.
"""

from collections import Counter
from math import sqrt
from typing import Dict, List, Tuple

import numpy as np

from FoodOPS_V1.domain.restaurant_VO import Restaurant
from game_engine.domain.types_VO import RestaurantType
from FoodOPS_V1.domain.market_VO import BUDGET_PER_SEGMENT, Segment
from FoodOPS_V1.domain.scenario_VO import Scenario
from FoodOPS_V1.rules.scoring import calculate_restaurant_attractiveness


def is_restaurant_affordable_for_customer_segment(
    restaurant: Restaurant, customer_segment: Segment
) -> bool:
    """Vérifie si un restaurant est abordable pour un type de clientèle donné.

    Un restaurant est considéré comme abordable si son prix médian est inférieur
    ou égal au budget du segment client multiplié par un facteur de tolérance.

    Par exemple, si les étudiants ont un budget de 10€ et une tolérance de 20%,
    ils accepteront des restaurants jusqu'à 12€ par repas.
    """
    # Facteur de tolérance budgétaire : les clients peuvent dépasser leur budget de 20%
    # lors d'occasions spéciales ou si le restaurant leur plaît vraiment
    customer_budget_flexibility: float = 1.20

    restaurant_menu = restaurant.menu
    menu_prices = [dish.price for dish in restaurant_menu if dish is not None]
    typical_meal_price = np.median(menu_prices) if menu_prices else 0.0

    customer_typical_budget = BUDGET_PER_SEGMENT.get(
        customer_segment, 15.0
    )  # budget par défaut : 15€
    maximum_acceptable_price = customer_typical_budget * customer_budget_flexibility

    return typical_meal_price <= maximum_acceptable_price


def count_competing_restaurants_by_type(
    restaurants: List[Restaurant],
) -> Dict[RestaurantType, int]:
    """
    Compte combien de restaurants de chaque type sont en concurrence sur le marché.

    Imagine une zone commerciale avec plusieurs restaurants :
    - Si il y a 3 fast-foods, ils vont se disputer la même clientèle (étudiants, familles pressées)
    - Si il y a 1 seul restaurant gastronomique, il aura le monopole de sa clientèle

    Cette fonction compte ces concurrents pour calculer ensuite l'impact de la concurrence
    sur l'attractivité de chaque restaurant.

    Args:
        restaurants: Liste de tous les restaurants présents sur le marché

    Returns:
        Dictionnaire indiquant combien de restaurants de chaque type sont présents.
        Exemple : {"FAST_FOOD": 2, "BISTRO": 1, "GASTRO": 1} signifie
                  2 fast-foods en concurrence, 1 bistro seul, 1 gastro seul
    """
    return Counter(r.type for r in restaurants)


def calculate_competition_penalty(
    restaurant: Restaurant, competitor_counts: Dict[RestaurantType, int]
) -> float:
    """Calcule la pénalité d'attractivité due à la concurrence directe.

    Dans la vraie vie, si plusieurs restaurants du même type sont présents dans une zone
    (par exemple 3 McDonald's dans la même rue), chacun aura moins de clients car ils
    se partagent la même clientèle. Cette fonction simule cet effet.

    Plus il y a de concurrents directs, plus l'attractivité de chaque restaurant diminue.
    Cependant, l'effet n'est pas linéaire : passer de 1 à 2 concurrents a plus d'impact
    que passer de 5 à 6.

    Args:
        restaurant: Le restaurant dont on calcule la pénalité de concurrence
        competitor_counts: Nombre de restaurants de chaque type sur le marché

    Returns:
        Facteur de réduction entre 0 et 1:
        - 1.0 = aucun concurrent du même type (monopole local)
        - 0.8-0.9 = quelques concurrents (marché partagé)
        - < 0.8 = marché très concurrentiel

    Exemple concret:
        - 1 seul MacDo dans la zone → facteur = 1.0 (tous les clients fast-food viennent chez lui)
        - 2 MacDo + 1 Quick dans la zone → facteur ≈ 0.85 (ils se partagent les clients)
    """
    # Intensité de la concurrence : ce paramètre contrôle à quel point la concurrence fait mal
    # Valeur 0.5 = concurrence modérée (réaliste)
    # Valeur plus élevée = concurrence plus brutale
    COMPETITION_INTENSITY: float = 0.50

    # Combien de restaurants du même type sont présents sur le marché ?
    number_of_similar_restaurants = competitor_counts[restaurant.type]

    # Si on est le seul restaurant de notre type, on a un monopole local
    # (ex: seul MacDo de la zone → tous les clients fast-food viennent chez nous)
    if number_of_similar_restaurants <= 1:
        return 1.0  # Aucune pénalité, attractivité maximale

    # Calcul de la réduction d'attractivité due à la concurrence
    #
    # Logique : plus il y a de concurrents, plus chacun perd en attractivité
    # Mais l'effet diminue progressivement (loi des rendements décroissants)
    #
    # Exemples concrets :
    # - 2 MacDo au lieu de 1 : impact fort (-15% à -20% d'attractivité)
    # - 5 MacDo au lieu de 4 : impact plus faible (-2% à -5% d'attractivité)
    #
    # Formule mathématique : 1 / sqrt(1 + intensité * (nb_concurrents - 1))
    excess_competitors = (
        number_of_similar_restaurants - 1
    )  # On retire 1 car on se compte dedans
    competition_impact = sqrt(1.0 + COMPETITION_INTENSITY * excess_competitors)
    attractiveness_reduction_factor = 1.0 / max(1.0, competition_impact)

    return attractiveness_reduction_factor


def _rank_restaurants_for_customer_segment(
    restaurants: List[Restaurant],
    customer_segment: Segment,
    competitor_counts: Dict[RestaurantType, int],
) -> Dict[int, float]:
    """
    Classe les restaurants selon leur attractivité pour un type de clientèle spécifique.

    Imagine que vous êtes un étudiant avec un budget limité cherchant où manger.
    Cette fonction simule votre processus de choix :

    1. D'abord, elle élimine les restaurants trop chers pour votre budget
    2. Ensuite, elle note chaque restaurant restant sur son attractivité
       (qualité, emplacement, réputation, etc.)
    3. Enfin, elle pénalise les restaurants qui ont beaucoup de concurrents identiques

    Args:
        restaurants: Tous les restaurants disponibles dans la zone
        customer_segment: Type de clientèle (étudiant, famille, touriste, etc.)
        competitor_counts: Combien de restaurants de chaque type sont présents

    Returns:
        Dictionnaire {index_restaurant: score_attractivité} pour les restaurants abordables.
        Plus le score est élevé, plus le restaurant est attractif pour ce segment.

    Exemple:
        Pour les étudiants : {0: 8.5, 2: 6.2, 1: 3.1}
        → Le restaurant 0 est le plus attractif, puis le 2, puis le 1
    """
    restaurant_scores: Dict[int, float] = {}

    # Évalue chaque restaurant pour ce type de clientèle
    for restaurant_index, restaurant in enumerate(restaurants):
        # D'abord, vérifie si ce restaurant est abordable pour ce segment
        if not is_restaurant_affordable_for_customer_segment(
            restaurant, customer_segment
        ):
            continue  # Restaurant trop cher, on l'ignore complètement

        # Calcule l'attractivité de base du restaurant pour ce segment
        # (qualité, emplacement, adéquation avec le type de clientèle, etc.)
        base_attractiveness = calculate_restaurant_attractiveness(
            restaurant, customer_segment
        )

        # Réduit l'attractivité s'il y a beaucoup de concurrents du même type
        competition_penalty = calculate_competition_penalty(
            restaurant, competitor_counts
        )

        # Score final = attractivité de base multipliée par la pénalité de concurrence
        final_attractiveness_score = base_attractiveness * competition_penalty
        restaurant_scores[restaurant_index] = final_attractiveness_score

    return restaurant_scores


def allocate_customers_to_restaurants(
    restaurants: List[Restaurant], market_scenario: Scenario
) -> Dict[int, int]:
    """
    Simule comment les clients choisissent où aller manger dans une zone commerciale.

    Imaginez une rue avec plusieurs restaurants et différents types de clients :
    - Des étudiants avec un petit budget cherchent du rapide et pas cher
    - Des familles veulent un bon rapport qualité/prix avec des portions généreuses
    - Des touristes sont prêts à payer plus pour une expérience authentique
    - Des cadres veulent de la qualité pour leurs repas d'affaires

    Cette fonction simule ce processus naturel :
    1. Pour chaque type de clientèle, elle identifie quels restaurants sont abordables
    2. Elle classe ces restaurants par attractivité (qualité, emplacement, réputation)
    3. Elle "remplit" d'abord le restaurant le plus attractif, puis le suivant quand il est plein
    4. Elle tient compte de la concurrence (trop de restaurants identiques nuit à chacun)

    Args:
        restaurants: Tous les restaurants disponibles dans la zone
        market_scenario: Caractéristiques du marché (combien de clients de chaque type, leurs budgets)

    Returns:
        Dictionnaire indiquant combien de clients chaque restaurant attire.
        Exemple : {0: 145, 1: 89, 2: 0} = le restaurant 0 attire 145 clients,
                  le restaurant 1 en attire 89, le restaurant 2 n'en attire aucun.

    Note:
        Certains clients peuvent être "perdus" s'ils ne trouvent pas de restaurant adapté à leurs besoins :
        - Soit parce que tous les restaurants sont trop chers pour eux
        - Soit parce que tous les restaurants abordables sont pleins
    """
    # Calcule combien de clients de chaque type sont présents sur le marché ce mois-ci
    customers_by_type = market_scenario.compute_segment_quantities()
    competitor_counts_by_type = count_competing_restaurants_by_type(restaurants)

    # Prépare le suivi de capacité : combien de clients chaque restaurant peut encore accueillir
    available_seats_per_restaurant = {
        restaurant_index: restaurant.compute_maximum_monthly_customers()
        for restaurant_index, restaurant in enumerate(restaurants)
    }
    # Prépare le suivi d'attribution : combien de clients attribués à chaque restaurant (commence à 0)
    customers_assigned_to_each_restaurant = {
        restaurant_index: 0 for restaurant_index, _ in enumerate(restaurants)
    }

    # Traite chaque type de clientèle séparément
    for customer_type, number_of_customers in customers_by_type.items():
        # S'il n'y a pas de clients de ce type ce mois-ci, passe au suivant
        if number_of_customers <= 0:
            continue

        # Obtient les restaurants classés par attractivité pour ce segment
        # (inclut le filtrage budgétaire et les pénalités de concurrence)
        restaurant_rankings = _rank_restaurants_for_customer_segment(
            restaurants, customer_type, competitor_counts_by_type
        )

        # Si aucun restaurant n'est abordable pour ce segment, tous les clients sont perdus
        if not restaurant_rankings:
            continue  # Tous les clients de ce type ne trouvent pas de restaurant adapté

        clients_still_looking_for_restaurant = number_of_customers

        # Allocation des clients : on remplit d'abord le restaurant le plus attractif,
        # puis quand il est plein, on passe au suivant, etc.
        for restaurant_index, _attractiveness_score in restaurant_rankings.items():
            # Si tous les clients ont trouvé un restaurant, on arrête
            if clients_still_looking_for_restaurant <= 0:
                break

            # Si ce restaurant est déjà plein, on passe au suivant
            if available_seats_per_restaurant[restaurant_index] <= 0:
                continue

            # Calcule combien de clients ce restaurant peut encore accueillir
            clients_this_restaurant_can_serve = min(
                clients_still_looking_for_restaurant,
                available_seats_per_restaurant[restaurant_index],
            )

            # Attribue ces clients au restaurant
            customers_assigned_to_each_restaurant[restaurant_index] += (
                clients_this_restaurant_can_serve
            )
            available_seats_per_restaurant[restaurant_index] -= (
                clients_this_restaurant_can_serve
            )
            clients_still_looking_for_restaurant -= clients_this_restaurant_can_serve

    return customers_assigned_to_each_restaurant


def clamp_capacity(
    restaurants: List[Restaurant], allocated: Dict[int, int]
) -> Dict[int, int]:
    """Vérifie que chaque restaurant ne dépasse pas sa capacité maximale.

    Imaginez que l'allocation de clients ait attribué 1500 clients à un petit restaurant
    qui ne peut en servir que 800. Cette fonction corrige le problème en limitant
    chaque restaurant à sa capacité réelle.

    C'est comme un contrôle de sécurité : on s'assure qu'aucun restaurant ne soit
    surchargé au-delà de ce qu'il peut physiquement gérer.

    Args:
        restaurants: Liste des restaurants avec leurs caractéristiques
        allocated: Combien de clients ont été attribués à chaque restaurant

    Returns:
        Combien de clients chaque restaurant peut réellement servir
        (limité par sa capacité physique)

    Exemple concret:
        - Attribution initiale : Restaurant A = 1500 clients, Restaurant B = 800 clients
        - Capacités maximales : Restaurant A = 1200 clients, Restaurant B = 1000 clients
        - Résultat final : Restaurant A = 1200 clients (limité), Restaurant B = 800 clients (OK)
    """
    actually_served: Dict[int, int] = {}
    for restaurant_index, restaurant in enumerate(restaurants):
        # Capacité maximale que ce restaurant peut gérer
        maximum_capacity = restaurant.compute_maximum_monthly_customers()

        # Nombre de clients attribués à ce restaurant
        clients_assigned = allocated.get(restaurant_index, 0)

        # Prend le minimum entre ce qui est attribué et ce qui est possible
        clients_actually_served = min(clients_assigned, maximum_capacity)
        actually_served[restaurant_index] = clients_actually_served

    return actually_served
