"""Génération de recettes et de menus à partir du catalogue d'ingrédients.

Ce module fournit des utilitaires pour:
- déterminer les combinaisons d'ingrédients compatibles selon leurs catégories,
- choisir une technique culinaire adaptée à la catégorie principale,
- estimer des coûts matières par portion et un prix de vente indicatif selon le type de restaurant,
- générer des recettes simples et des *combos* (association de deux ingrédients),
- construire un menu varié pour un type de restaurant donné.

Les fonctions internes (préfixées par « _ ») sont conçues pour être testables
"""

from typing import List, Dict
import random

from FoodOPS_V1.domain.recipe_VO import SimpleRecipe, Technique, Complexity
from FoodOPS_V1.domain.restaurant_VO import MARGIN_BY_RESTO, Restaurant, RestaurantType
from game_engine.domain.menu.ingredients_VO import (
    IngredientCategory,
    FoodGrade,
    Ingredient,
    CATALOG,
    Tier,
)

_COMPATIBLE_INGREDIENT_COMBINATIONS = (
    (IngredientCategory.VIANDE, IngredientCategory.LEGUME),
    (IngredientCategory.VIANDE, IngredientCategory.FECULENT),
    (IngredientCategory.POISSON, IngredientCategory.LEGUME),
    (IngredientCategory.POISSON, IngredientCategory.FECULENT),
)

_COOKING_TECHNIQUES_BY_CATEGORY = {
    IngredientCategory.VIANDE: [Technique.GRILLE, Technique.SAUTE],
    IngredientCategory.POISSON: [Technique.FOUR, Technique.SAUTE, Technique.FROID],
    IngredientCategory.LEGUME: [Technique.FOUR, Technique.SAUTE, Technique.FROID],
    IngredientCategory.FECULENT: [Technique.FOUR, Technique.SAUTE],
    IngredientCategory.CONDIMENT: [Technique.FROID, Technique.SAUTE],
    IngredientCategory.BOULANGERIE: [Technique.FOUR, Technique.FROID],
    IngredientCategory.PRODUIT_LAITIER: [Technique.FROID, Technique.SAUTE],
}


# portions (kg) indicatives par catégorie (pour 1 portion)
PORTION_KG = {
    IngredientCategory.VIANDE: 0.15,
    IngredientCategory.POISSON: 0.12,
    IngredientCategory.LEGUME: 0.10,
    IngredientCategory.FECULENT: 0.08,
    IngredientCategory.PRODUIT_LAITIER: 0.05,
    IngredientCategory.BOULANGERIE: 0.08,
    IngredientCategory.CONDIMENT: 0.01,
}


def _allowed_for_type(ingredient: Ingredient, rtype: RestaurantType) -> bool:
    """
    Vérifie si un ingredient du catalogue est accessible au type de restaurant.

    Paramètres
    ----------
    ingredient : Ingredient
        L'élément du catalogue à tester (contient la clé `tier`).
    rtype : RestaurantType
        Type de restaurant pour lequel on teste l'éligibilité.

    Retour
    ------
    bool
        ``True`` si l'ingrédient est disponible pour ce type de restaurant.

    Notes
    -----
    La logique s'appuie sur `ingredient.tier`:
    - ``ALL``: disponible partout
    - ``BISTRO_PLUS``: disponible en ``BISTRO`` et ``GASTRO``
    - ``GASTRO_ONLY``: uniquement en ``GASTRO``

    """
    if ingredient.tier == Tier.ALL:
        return True
    if ingredient.tier == Tier.BISTRO_PLUS:
        return rtype in (RestaurantType.BISTRO, RestaurantType.GASTRO)
    if ingredient.tier == Tier.GASTRO_ONLY:
        return rtype == RestaurantType.GASTRO
    return False


def _name_simple(ingredient_name: str, tech: Technique, rtype: RestaurantType) -> str:
    """Construit un nom de recette simple adapté au concept.

    Paramètres
    ----------
    ingredient_name : str
        Nom de l'ingrédient principal.
    tech : Technique
        Technique culinaire retenue.
    rtype : RestaurantType
        Type de restaurant (influence certains intitulés).

    Retour
    ------
    str
        Nom lisible de la recette.

    Notes
    -----
    Cas particuliers pour ``FAST_FOOD`` (ex. burger, fish & chips), sinon
    une formulation générique est utilisée (ex. « rôti », « poêlé »).

    Exemple
    -------
    >>> _name_simple("Poulet", Technique.SAUTE, RestaurantType.FAST_FOOD)
    'Burger de poulet'
    >>> _name_simple("Asperge", Technique.FOUR, RestaurantType.BISTRO)
    'Asperge rôti'
    """
    # Fast food special cases
    if rtype == RestaurantType.FAST_FOOD:
        if "Boeuf haché" in ingredient_name:
            return "Burger classique"
        if "Poulet" in ingredient_name:
            return "Burger de poulet"
        if "Cabillaud" in ingredient_name:
            return "Fish & Chips"

    # Generic technique-based naming
    technique_labels = {
        Technique.GRILLE: "grillé",
        Technique.SAUTE: "poêlé",
        Technique.FOUR: "rôti",
        Technique.FROID: "froid",
    }
    return f"{ingredient_name} {technique_labels[tech]}"


def _name_combo(a: str, b: str, tech: Technique, rtype: RestaurantType) -> str:
    """Construit un nom lisible pour une recette combo.

    Paramètres
    ----------
    a, b : str
        Noms des deux ingrédients.
    tech : Technique
        Technique retenue pour le combo.
    rtype : RestaurantType
        Type de restaurant (influe sur la mise en forme du nom).

    Retour
    ------
    str
        Intitulé lisible du combo.

    Notes
    -----
    En ``GASTRO``, la conjonction « & » et une ponctuation plus valorisante
    sont utilisées.

    Exemple
    -------
    >>> _name_combo("Saumon", "Asperge", Technique.FOUR, RestaurantType.BISTRO)
    'Saumon + Asperge (au four)'
    >>> _name_combo("Saumon", "Asperge", Technique.FOUR, RestaurantType.GASTRO)
    'Saumon & Asperge, au four'
    """
    tech_labels = {
        Technique.GRILLE: "grillé",
        Technique.SAUTE: "poêlé",
        Technique.FOUR: "au four",
        Technique.FROID: "froid",
    }

    label = tech_labels[tech]

    if rtype == RestaurantType.GASTRO:
        return f"{a} & {b}, {label}"
    return f"{a} + {b} ({label})"


def _choose_grade(prices_by_grade: Dict[FoodGrade, float]) -> FoodGrade:
    """Choisit une gamme d'ingrédient cohérente avec le type de resto.

    Paramètres
    ----------
    prices_by_grade : Dict[FoodGrade, float]
        Prix au kg disponibles par gamme pour l'ingrédient.
    rtype : RestaurantType
        Type de restaurant, conditionnant l'ordre de préférence.

    Retour
    ------
    FoodGrade
        Gamme sélectionnée parmi celles disponibles.

    Notes
    -----
    Préférences par défaut:
    - ``FAST_FOOD``: pratique/surgelé prioritaire
    - ``BISTRO``: frais prioritaire, puis surgelé
    - ``GASTRO``: frais prioritaire
    """
    # Ordre de préférence par type de restaurant

    return next(iter(prices_by_grade.keys()))


def _fit_for_ing(ingredient_name: str, restaurant: Restaurant) -> float:
    """Retourne un score de fit catalogue (0..1) pour un ingrédient et un concept.

    Paramètres
    ----------
    ingredient_name : str
        Nom de l'ingrédient dans le catalogue.
    rtype : RestaurantType
        Type de restaurant.

    Retour
    ------
    float
        Score de compatibilité catalogue pour ce concept.
    """
    item = CATALOG[ingredient_name]
    return float(item.fit_score[restaurant.type.name])


def _quality_from_ingredients(
    ingredients: List[Ingredient], restaurant: Restaurant
) -> float:
    """Estime la qualité perçue basée sur le fit moyen des ingrédients.

    Retour: qualité perçue (0-1), calculée comme moyenne des fits * 0.7.
    """
    # qualité perçue = moyenne des fit * un petit base (0.7)
    if not ingredients:
        return 0.0
    fits = [_fit_for_ing(ingredient, restaurant) for ingredient in ingredients]
    return round(0.7 * (sum(fits) / len(fits)), 3)


def _cost_per_portion(ingredient_name: str, grade: FoodGrade) -> float:
    """Coût matière par portion pour un ingrédient/grade.

    Paramètres
    ----------
    ingredient_name : str
        Nom de l'ingrédient dans le catalogue.
    grade : FoodGrade
        Gamme choisie pour l'ingrédient.

    Retour
    ------
    float
        Coût matière par portion, en unité monétaire du catalogue.

    Notes
    -----
    La portion (kg) est approchée via `PORTION_KG` par catégorie principale.
    Par défaut, une portion de 0.08 kg est utilisée si la catégorie n'est pas listée.
    """
    item = CATALOG[ingredient_name]
    price_kg = item.prices_by_grade[grade]
    cats = item.categories
    # si plusieurs catégories, prend la 1ère pour la portion
    portion = PORTION_KG.get(cats[0], 0.08)
    return round(price_kg * portion, 2)


def _compute_price(
    cost_per_portion: float, restaurant: Restaurant, complexity: Complexity
) -> float:
    """Applique un multiplicateur type concept pour obtenir un prix TTC indicatif.

    Paramètres
    ----------
    cost_per_portion : float
        Coût matière estimé par portion.
    rtype : RestaurantType
        Type de restaurant (détermine la marge de base).
    complexity : Complexity
        Complexité de la recette (peut ajuster la marge).

    Retour
    ------
    float
        Prix de vente indicatif TTC.

    Notes
    -----
    Un supplément de marge est appliqué aux combos pour refléter la valeur perçue.
    """
    mult = MARGIN_BY_RESTO[restaurant.type.name]
    if complexity == Complexity.COMBO:
        mult += 0.4
    return round(cost_per_portion * mult, 2)


def _gen_simple(item: Ingredient, restaurant: Restaurant) -> SimpleRecipe:
    """Crée une recette simple à partir d'un item de catalogue.

    Paramètres
    ----------
    item : Ingredient
        Item issu du catalogue (contient prix/grades, catégories, nom).
    rtype : RestaurantType
        Type de restaurant cible.

    Retour
    ------
    SimpleRecipe
        Recette simple prête à être affichée dans un menu.

    """
    # pick une gamme cohérente
    grade = _choose_grade(item.prices_by_grade)
    tech = random.choice(_COOKING_TECHNIQUES_BY_CATEGORY[item.categories[0]])
    name = _name_simple(item.name, tech, restaurant.type)
    c_per_portion = _cost_per_portion(item.name, grade)
    price = _compute_price(c_per_portion, restaurant, Complexity.SIMPLE)
    qual = _quality_from_ingredients([item.name], restaurant)

    return SimpleRecipe(
        name=name,
        ingredients=[(item.name, grade)],
        technique=tech,
        complexity=Complexity.SIMPLE,
        base_quality=qual,
        price=price,
    )


def _compatible(a: Ingredient, b: Ingredient) -> bool:
    """Retourne True si les catégories primaires sont compatibles pour un combo.

    Paramètres
    ----------
    a, b : Ingredient
        Deux items du catalogue à associer.

    Retour
    ------
    bool
        ``True`` si la paire de catégories principales est autorisée.

    Notes
    -----
    La compatibilité est vérifiée sur la catégorie à l'index 0 de chaque item
    et est symétrique (A,B) ≡ (B,A).
    """
    ca = a.categories[0]
    cb = b.categories[0]
    pair = (ca, cb)
    rev = (cb, ca)
    return (
        pair in _COMPATIBLE_INGREDIENT_COMBINATIONS
        or rev in _COMPATIBLE_INGREDIENT_COMBINATIONS
    )


def _gen_combo(a: Ingredient, b: Ingredient, restaurant: Restaurant) -> SimpleRecipe:
    """Crée une recette combo à partir de deux items compatibles.

    Paramètres
    ----------
    a, b : Ingredient
        Items compatibles à associer dans la recette.
    rtype : RestaurantType
        Type de restaurant cible.

    Retour
    ------
    SimpleRecipe
        Recette « combo » combinant les deux ingrédients.

    Notes
    -----
    La technique est choisie dans l'intersection des techniques possibles
    pour chaque catégorie primaire, avec repli sur ``SAUTE`` s'il n'y a pas
    d'intersection.

    """
    grade_a = _choose_grade(a.prices_by_grade)
    grade_b = _choose_grade(b.prices_by_grade)
    tech = random.choice(
        list(
            set(_COOKING_TECHNIQUES_BY_CATEGORY[a.categories[0]])
            & set(_COOKING_TECHNIQUES_BY_CATEGORY[b.categories[0]])
        )
        or [Technique.SAUTE]
    )

    name = _name_combo(a.name, b.name, tech, restaurant.type)
    c_portion = _cost_per_portion(a.name, grade_a) + _cost_per_portion(b.name, grade_b)
    price = _compute_price(c_portion, restaurant, Complexity.COMBO)
    qual = _quality_from_ingredients([a.name, b.name], restaurant)

    return SimpleRecipe(
        name=name,
        ingredients=[(a.name, grade_a), (b.name, grade_b)],
        technique=tech,
        complexity=Complexity.COMBO,
        base_quality=qual,
        price=price,
    )


def build_menu_for_type(restaurant: Restaurant) -> List[SimpleRecipe]:
    """Génère un menu varié pour un type de restaurant donné.

    Crée un menu équilibré composé de recettes simples et de combos,
    adapté au niveau et au style du type de restaurant. Le nombre de
    recettes varie selon le type : 10 pour fast-food, 15 pour bistro,
    20 pour gastro.

    Paramètres
    ----------
    rtype : RestaurantType
        Type de restaurant (FAST_FOOD, BISTRO, ou GASTRO) qui détermine
        la taille du menu et les ingrédients accessibles.

    Retour
    ------
    List[SimpleRecipe]
        Liste de recettes variées pour le menu, contenant un mélange
        de recettes simples et de combos adaptés au type de restaurant.

    Notes
    -----
    - Varie l'ordre des ingrédients via un mélange pour obtenir des menus
      différents d'une exécution à l'autre.
    - Tentative exhaustive de paires compatibles jusqu'à atteindre la taille
      cible, puis repli sur des recettes simples si nécessaire (fail-safe).

    Exemple
    -------
    >>> menu = build_menu_for_type(RestaurantType.FAST_FOOD)
    >>> len(menu) == 10 and all(isinstance(m, SimpleRecipe) for m in menu)
    True
    >>> menu = build_menu_for_type(RestaurantType.GASTRO)
    >>> len(menu) == 20
    True
    """
    # Définir la taille cible du menu selon le type de restaurant

    targets = {
        "FAST_FOOD": 10,
        "BISTRO": 15,
        "GASTRO": 20,
    }
    target = targets[restaurant.type.name]

    # Filtrer le catalogue pour ne garder que les ingrédients accessibles au type de restaurant.
    # (Réduit l'espace de recherche et évite de proposer des items inadaptés au concept.)
    avail = [
        ingredient
        for ingredient in CATALOG.values()
        if _allowed_for_type(ingredient, restaurant.type)
    ]
    random.shuffle(avail)  # Mélanger pour varier les menus à chaque génération

    # 1) Générer des recettes simples (environ la moitié du menu, minimum 6)
    # Prendre les premiers ingrédients disponibles après mélange
    nombre_recettes_simples = max(6, target // 2)
    simples = [
        _gen_simple(ingredient, restaurant)
        for ingredient in avail[:nombre_recettes_simples]
    ]

    # 2) Générer des combos en testant toutes les paires d'ingrédients compatibles.
    #    On s'arrête dès que la taille cible est atteinte pour éviter un coût quadratique inutile.
    combos: List[SimpleRecipe] = []
    for i in range(len(avail)):
        for j in range(i + 1, len(avail)):
            # Arrêter si on a atteint la taille cible du menu
            if len(simples) + len(combos) >= target:
                break

            # Tester la compatibilité des deux ingrédients (catégories primaires)
            a, b = avail[i], avail[j]
            if _compatible(a, b):
                combos.append(_gen_combo(a, b, restaurant))

        # Double vérification pour sortir de la boucle externe
        if len(simples) + len(combos) >= target:
            break

    # Combiner simples et combos, en limitant à la taille cible
    menu = (simples + combos)[:target]

    # Fail-safe : si on n'a pas assez de recettes (manque de combos compatibles),
    # compléter avec des recettes simples aléatoires pour atteindre la cible.
    while len(menu) < target:
        menu.append(_gen_simple(random.choice(avail), restaurant))

    return menu
