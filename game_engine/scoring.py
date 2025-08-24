from pathlib import Path
from typing import Annotated, Dict, Optional

import numpy as np
from pydantic import BaseModel, Field

from FoodOPS_V1.domain.restaurant_VO import Restaurant
from FoodOPS_V1.domain.market_VO import BUDGET_PER_SEGMENT, Segment
from game_engine.domain.types_VO import RestaurantType
from FoodOPS_V1.domain.recipe_VO import SimpleRecipe
from game_engine.utilsV0 import load_and_validate

# ==========================
# Poids des critères (somme ~ 1)
# ==========================


# ==========================
# Petits helpers génériques
# ==========================

# =====================================================
# Qualité perçue du menu
#  - Combine la qualité des recettes (moyenne)
#  - Applique un ajustement "exigence du concept"
#  - Applique la satisfaction RH (optionnelle)
# =====================================================


def _recipe_grade_hint(recipe: SimpleRecipe) -> Optional[str]:
    """
    Retourne un hint de "gamme ingrédient" si disponible.
    Ex. 'G1','G3','G5' ou 'fresh','frozen','sousvide'. None si indéterminé.

    Exemple
    -------
    'G3'
    """
    # Essais souples de champs potentiels
    for attr in ("grade_hint", "grade_tag", "grade", "food_grade", "ing_grade"):
        v = getattr(recipe, attr, None)
        if v is None:
            continue
        # Enum -> str
        if hasattr(v, "name"):
            return v.name.upper()
        if hasattr(v, "value"):
            try:
                return str(v.value).upper()
            except Exception:
                return str(v)
        try:
            return str(v).upper()
        except Exception:
            pass
    return None


# Attente de "prestige" par type de restaurant : pénalités si la recette paraît "trop simple"
# Les valeurs sont multipliées (1.0 = neutre, <1 = malus)
_CONCEPT_EXPECTATION_PENALTY = {
    RestaurantType.FAST_FOOD: {
        "G5": 0.95,  # trop "haut de gamme" n'apporte pas grand-chose ici (neutre-)
        "G1": 1.00,  # très bien si frais
        "G3": 0.95,  # surgelé OK
        None: 0.98,
    },
    RestaurantType.BISTRO: {
        "G5": 0.98,  # 5ème gamme OK si bien exécuté
        "G1": 1.00,  # frais cohérent
        "G3": 0.95,  # surgelé léger malus
        None: 0.98,
    },
    RestaurantType.GASTRO: {
        "G5": 1.00,  # du sous-vide haute qualité peut être OK en gastro
        "G1": 1.00,  # frais attendu
        "G3": 0.85,  # surgelé mal vu en gastro
        None: 0.92,  # indéterminé : petit malus par prudence
    },
}


def _apply_concept_quality_adjust(restaurant: Restaurant, q: float, recipe) -> float:
    """
    Ajuste la qualité d'une recette selon les attentes du concept.
    Ex: surgelé en gastro → malus.

    Exemple
    -------
    0.765
    """
    # Extract restaurant type value, handling both enum and string cases
    restaurant_type = restaurant.type
    table = _CONCEPT_EXPECTATION_PENALTY[restaurant_type]
    hint = _recipe_grade_hint(recipe)

    # Normalise certains mots-clés
    if hint in ("FRESH", "FRAIS"):
        hint_norm = "G1"
    elif hint in ("FROZEN", "SURGELE", "SURGELÉ", "G3"):
        hint_norm = "G3"
    elif hint in ("SOUSVIDE", "SOUS_VIDE", "G5"):
        hint_norm = "G5"
    else:
        hint_norm = None

    mult = table.get(hint_norm, table.get(None, 1.0))
    return q * float(mult)


def calculate_perceived_menu_quality(restaurant: Restaurant) -> float:
    """
    Calcule la qualité que les clients perçoivent du menu d'un restaurant.

    Comme dans la vraie vie, la qualité perçue dépend de plusieurs facteurs :

    1. **Qualité des plats** : recettes bonnes ou mauvaises de base
    2. **Cohérence avec le concept** :
       - Du surgelé dans un fast-food ? Normal
       - Du surgelé dans un restaurant gastronomique ? Scandaleux !
    3. **Qualité du service** :
       - Personnel motivé → meilleure exécution des plats
       - Personnel démotivé → plats bâclés

    Args:
        restaurant: Le restaurant dont on évalue la qualité perçue

    Returns:
        Score entre 0.0 et 1.0 :
        - 0.0 = menu catastrophique ou vide
        - 0.5 = qualité correcte sans plus
        - 1.0 = excellence culinaire parfaitement exécutée
    """
    # Si le restaurant n'a pas de menu, qualité nulle
    if not restaurant.menu:
        return 0.0

    # Évalue la qualité de chaque plat du menu
    dish_quality_scores = []
    for dish in restaurant.menu:
        # Qualité de base du plat (définie par la recette)
        base_dish_quality = dish.base_quality

        # Ajustement selon la cohérence avec le concept du restaurant
        # (ex: surgelé pénalisé en gastro mais OK en fast-food)
        quality_adjusted_for_concept = _apply_concept_quality_adjust(
            restaurant, base_dish_quality, dish
        )
        dish_quality_scores.append(quality_adjusted_for_concept)

    # Calcule la qualité moyenne de tous les plats du menu
    average_menu_quality = sum(dish_quality_scores) / max(1, len(dish_quality_scores))

    # Impact de la motivation du personnel sur l'exécution
    # Personnel motivé = meilleure exécution des recettes
    staff_motivation_impact = restaurant.rh_satisfaction
    final_perceived_quality = average_menu_quality * float(staff_motivation_impact)

    return final_perceived_quality


# =====================================================
# Prix & budget
# =====================================================


def calculate_price_affordability(meal_price: float, customer_budget: float) -> float:
    """
    Calcule à quel point un prix de repas convient au budget d'un client.

    Dans la vraie vie, plus un restaurant est cher par rapport au budget du client,
    moins il est attractif. Cette fonction simule cette relation :

    - Prix = budget du client → parfait (score 1.0)
    - Prix < budget → très attractif (score 1.0)
    - Prix > budget → attractivité décroissante jusqu'à 0

    Exemples :
        - Client avec budget 15€, restaurant à 12€ → score 1.0 (parfait)
        - Client avec budget 15€, restaurant à 18€ → score 0.8 (un peu cher)
        - Client avec budget 15€, restaurant à 30€ → score 0.0 (hors budget)
    """
    # Si le budget du client est invalide, pas d'attractivité
    if customer_budget <= 0:
        return 0.0

    # Si le restaurant est dans le budget, c'est parfait
    if meal_price <= customer_budget:
        return 1.0

    # Calcul de l'écart de prix (en pourcentage du budget)
    # Exemple : budget 15€, prix 18€ → écart = (18-15)/15 = 0.2 (20% au-dessus)
    price_overshoot_ratio = (meal_price - customer_budget) / customer_budget

    # Plus l'écart est grand, plus l'attractivité baisse
    # Score = 1.0 - écart (mais jamais négatif)
    affordability_score = 1.0 - max(0.0, price_overshoot_ratio)
    return affordability_score


# =====================================================
# Score d'attraction final
# =====================================================


# Matrice concept <==> segment (fit structurel)
class ConceptFitModel(BaseModel):
    FAST_FOOD: Dict[Segment, Annotated[float, Field(strict=True, ge=0, le=1)]]
    BISTRO: Dict[Segment, Annotated[float, Field(strict=True, ge=0, le=1)]]
    GASTRO: Dict[Segment, Annotated[float, Field(strict=True, ge=0, le=1)]]

    def __getitem__(self, key):
        # Allows dict-like access
        return getattr(self, key)


directory = Path("/home/lepagnol/Documents/Perso/Games/foodopsV0TL/FoodOPS_V1/data")
path = directory / "concept_fit.json"
CONCEPT_FIT = load_and_validate(path, ConceptFitModel)


class ScoreWeightsModel(BaseModel):
    fit: float  # adéquation concept <==> segment
    prix: float  # accessibilité prix vs budget
    qualite: float  # qualité perçue (recettes, RH, adéquation gamme)
    notoriete: float  # "marque", bouche-à-oreille
    visibility: float  # emplacement/visibilité du local

    def __getitem__(self, key):
        # Allows dict-like access
        return getattr(self, key)


path = directory / "scoring_weights.json"
SCORING_WEIGHTS = load_and_validate(path, ScoreWeightsModel)


def calculate_restaurant_attractiveness(
    restaurant: Restaurant, customer_type: Segment
) -> float:
    """
    Calcule à quel point un restaurant attire un type de client spécifique.

    Comme dans la vraie vie, l'attractivité d'un restaurant dépend de plusieurs facteurs :

    1. **Adéquation concept/clientèle** : Un fast-food attire plus les étudiants qu'un gastro
    2. **Prix abordable** : Les clients ont un budget, pas question de le dépasser trop
    3. **Qualité perçue** : Bon menu bien exécuté par une équipe motivée
    4. **Réputation** : Bouche-à-oreille et avis clients
    5. **Visibilité** : Un restaurant caché attire moins qu'un restaurant en vitrine

    Returns:
        Score d'attractivité entre 0.0 et 1.0 :
        - 0.0 = restaurant pas du tout attractif pour ce type de client
        - 0.5 = attractivité moyenne
        - 1.0 = restaurant parfaitement attractif pour ce type de client
    """
    # Calcule le prix typique d'un repas (prix médian du menu)
    restaurant_menu = restaurant.menu
    menu_prices = [dish.price for dish in restaurant_menu if dish is not None]
    typical_meal_price = np.median(menu_prices) if menu_prices else 0.0

    # Évalue les différents aspects qui rendent un restaurant attractif
    perceived_quality = calculate_perceived_menu_quality(restaurant)
    location_visibility = (
        restaurant.local.visibility_normalized
    )  # Bien placé ? Visible ?
    reputation = restaurant.notoriety  # Bouche-à-oreille, avis clients

    # Adéquation entre le type de restaurant et le type de clientèle
    # (ex: fast-food attire plus les étudiants, gastro attire plus les cadres)
    concept_customer_fit = CONCEPT_FIT[restaurant.type.name][customer_type]

    # Vérifie si le restaurant est abordable pour ce type de clientèle
    typical_customer_budget = BUDGET_PER_SEGMENT.get(customer_type, 15.0)
    price_affordability = calculate_price_affordability(
        typical_meal_price, typical_customer_budget
    )

    # Combine tous les facteurs d'attractivité avec leurs poids respectifs
    attractiveness_factors = {
        "fit": concept_customer_fit,  # Adéquation concept/clientèle
        "prix": price_affordability,  # Prix abordable
        "qualite": perceived_quality,  # Qualité perçue du menu
        "notoriete": reputation,  # Réputation/bouche-à-oreille
        "visibility": location_visibility,  # Visibilité de l'emplacement
    }

    # Calcule le score final d'attractivité en pondérant chaque facteur
    total_attractiveness_score = sum(
        SCORING_WEIGHTS[factor_name] * attractiveness_factors[factor_name]
        for factor_name in SCORING_WEIGHTS.model_fields
    )

    # S'assure que le score reste positif (minimum 0.0)
    return max(0.0, total_attractiveness_score)
