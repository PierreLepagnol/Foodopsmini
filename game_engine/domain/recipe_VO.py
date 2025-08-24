from typing import List, Dict, Tuple, Optional
from enum import Enum
from game_engine.domain.menu.ingredients_VO import Ingredient, FoodGrade
from game_engine.domain.types_VO import RestaurantType

from pydantic import BaseModel, Field


class Technique(str, Enum):
    FROID = "froid"
    GRILLE = "grillé"
    SAUTE = "poêlé"
    FOUR = "au four"  # cuisson au four / rôtir
    ROTI = "rôti"  # ✅ alias rétro-compat: Technique.ROTI existe
    FRIT = "frit"
    VAPEUR = "vapeur"


class Complexity(str, Enum):
    SIMPLE = "simple"
    COMPLEXE = "complexe"
    COMBO = "combo"


# Multiplicateurs matière (€/kg effectif) par gamme
GRADE_COST_MULT = {
    FoodGrade.G1_FRAIS_BRUT: 1.00,
    FoodGrade.G2_CONSERVE: 0.95,
    FoodGrade.G3_SURGELE: 0.92,
    FoodGrade.G4_CRU_PRET: 1.08,  # prêt à l'emploi souvent plus cher/kg net
    FoodGrade.G5_CUIT_SOUS_VIDE: 1.12,
}

# Coût “main d'oeuvre + énergie + consommables” par portion (euros)
# (modèle simple, on affinera plus tard via RH réels)
LABOUR_ENERGY_PER_PORTION_BASE = 0.40
TECH_FACTOR = {
    Technique.FROID: 0.8,
    Technique.GRILLE: 1.1,
    Technique.SAUTE: 1.0,
    Technique.ROTI: 1.1,
    Technique.FRIT: 1.15,
    Technique.VAPEUR: 0.9,
}
CPLX_FACTOR = {
    Complexity.SIMPLE: 1.0,
    Complexity.COMPLEXE: 1.25,
}

FOOD_COST_TARGET = {
    RestaurantType.FAST_FOOD: 0.30,
    RestaurantType.BISTRO: 0.28,
    RestaurantType.GASTRO: 0.25,
}

DEFAULT_MARGIN_PER_PORTION = {
    RestaurantType.FAST_FOOD: 2.5,
    RestaurantType.BISTRO: 4.0,
    RestaurantType.GASTRO: 7.0,
}


class PricePolicy(str, Enum):
    FOOD_COST_TARGET = "FOOD_COST_TARGET"  # prix conseillé en visant % matière cible
    MARGIN_PER_PORTION = "MARGIN_PER_PORTION"  # prix conseillé avec marge € cible


class PrepStep(BaseModel):
    """Étape de prépa impactant la masse utile (parage, cuisson, évaporation, etc.)."""

    name: str
    loss_ratio: float = Field(ge=0, le=1)  # ex: 0.1 = -10%


class RecipeLine(BaseModel):
    ingredient: Ingredient
    quantity_grams: float
    preparation_steps: List[PrepStep] = Field(default_factory=list)

    def net_quantity_grams(self) -> float:
        """Quantité nette après pertes techniques (enchaînement des losses)."""
        net_quantity = self.quantity_grams
        for step in self.preparation_steps:
            # TODO: à remplacer par la fonction apply_loss
            # net_quantity = costing.apply_loss(net_quantity, step.loss_ratio)
            net_quantity = net_quantity * (1 - step.loss_ratio)
        return max(0.0, net_quantity)

    def line_cost(self, price_overrides: Dict[str, float] | None = None) -> float:
        """Coût d'achat pour la quantité brute (avant pertes) avec prix €/kg (overrides possible)."""
        unit_price = (price_overrides or {}).get(
            self.ingredient.name,
            self.ingredient.base_priceformat_currency_eur_per_kg,
        )
        return (self.quantity_grams / 1000.0) * unit_price


class Recipe(BaseModel):
    name: str
    lines: List[RecipeLine]
    yield_portions: int
    selling_price: float = 0.0  # le joueur peut forcer; sinon on proposera via policy
    base_quality: float = 0.0  # on calcule une qualité de base à partir des grades

    # --------- COÛTS ---------
    def raw_cost(self, price_overrides: Dict[str, float] | None = None) -> float:
        """Coût total matières (quantités brutes)."""
        return sum(line.line_cost(price_overrides) for line in self.lines)

    def cost_per_portion(
        self, price_overrides: Dict[str, float] | None = None
    ) -> float:
        """Coût matières / portion en tenant compte du rendement."""
        if self.yield_portions <= 0:
            return 0.0
        total_cost = self.raw_cost(price_overrides)
        # V1 simple : on répartit le coût matières sur le nombre de portions annoncé
        return total_cost / self.yield_portions

    # --------- QUALITÉ ---------
    def estimate_quality(self) -> float:
        """Qualité perçue (0..1) selon les grades + pénalités/pertes (V1 : moyenne pondérée simple)."""
        if not self.lines:
            return 0.0
        weights = []
        vals = []
        for line in self.lines:
            # TODO: à remplacer par la fonction grade_quality_weight
            # g_weight = costing.GRADE_QUALITY_WEIGHTS.get(line.ingredient.grade, 0.6)
            g_weight = 0.6
            vals.append(g_weight)
            weights.append(max(1.0, line.qty_g))  # pondération par masse
        q = sum(v * w for v, w in zip(vals, weights)) / sum(weights)
        self.base_quality = q
        return q

    # --------- PRIX CONSEILLÉ ---------
    def suggest_price(self, policy: PricePolicy) -> float:
        """Prix conseillé FR en fonction d'une politique type (fast/bistro/gastro)."""
        cm = self.cost_per_portion()
        return suggest_price(cm, policy)


class SimpleRecipe(BaseModel):
    name: str
    # Deux formats acceptés
    ingredients: Optional[list] = None
    main_ingredient: Optional[object] = None
    portion_kg: float = 0.0

    technique: Optional[Technique] = None
    complexity: Optional[Complexity] = None

    base_quality: float = Field(default=0.8, ge=0.0, le=1.0)
    base_cost: float = Field(default=0.0, ge=0.0)

    price: float = Field(default=0.0, ge=0.0)
    selling_price: float = Field(default=0.0, ge=0.0)

    def profit_margin(self) -> float:
        if self.selling_price <= 0:
            return 0.0
        return (self.selling_price - self.base_cost) / self.selling_price

    def clone_with_price(self, new_price: float):
        return SimpleRecipe(
            name=self.name,
            base_quality=self.base_quality,
            base_cost=self.base_cost,
            selling_price=new_price,
            price=new_price,
            technique=self.technique,
            complexity=self.complexity,
        )

    @property
    def effective_price(self) -> float:
        return float(self.price or self.selling_price or 0.0)

    def set_price(self, value):
        v = float(value)
        self.price = v
        self.selling_price = v


def suggest_price(
    restaurant_type: RestaurantType,
    recipe: SimpleRecipe,
    policy: PricePolicy = PricePolicy.FOOD_COST_TARGET,
) -> float:
    """Propose un prix de vente selon une politique donnée.

    Formules
    --------
    Politique FOOD_COST_TARGET (par défaut):
        price = COGS / food_cost_target_percentage

    Politique MARGIN_PER_PORTION:
        price = COGS + fixed_margin_per_portion

    Paramètres par type de restaurant:
    - FOOD_COST_TARGET: FAST_FOOD=30%, BISTRO=28%, GASTRO=25%
    - DEFAULT_MARGIN_PER_PORTION: FAST_FOOD=2.5€, BISTRO=4.0€, GASTRO=7.0€

    Note: Le food_cost_target est plafonné à minimum 5% pour éviter les divisions par zéro.

    Exemple
    -------
    >>> from FoodOPS_V1.domain.types import RestaurantType
    >>> from FoodOPS_V1.domain.recipe import SimpleRecipe, Technique, Complexity
    >>> from FoodOPS_V1.domain.ingredients import Ingredient, IngredientCategory, FoodGrade
    >>> ing = Ingredient(
    ...     name="Poulet", base_priceformat_currency_eur_per_kg=7.5,
    ...     category=IngredientCategory.VIANDE, grade=FoodGrade.G1_FRAIS_BRUT, perish_days=5
    ... )
    >>> r = SimpleRecipe(
    ...     name="Poulet poêlé", main_ingredient=ing, portion_kg=0.15,
    ...     technique=Technique.SAUTE, complexity=Complexity.SIMPLE
    ... )
    >>> r.grade = FoodGrade.G1_FRAIS_BRUT
    >>> suggest_price(RestaurantType.BISTRO, r)
    5.46
    >>> suggest_price(RestaurantType.BISTRO, r, PricePolicy.MARGIN_PER_PORTION)
    5.53
    """
    cogs = compute_recipe_cogs(recipe)
    if policy == PricePolicy.MARGIN_PER_PORTION:
        margin = DEFAULT_MARGIN_PER_PORTION.get(restaurant_type, 3.0)
        return round(cogs + margin, 2)
    # par défaut : % coût matière cible
    fc = FOOD_COST_TARGET.get(restaurant_type, 0.30)
    price = cogs / max(0.05, fc)
    return round(price, 2)


def compute_recipe_cogs(r: SimpleRecipe) -> float:
    """Calcule le COGS (€/portion) d'une recette simple.

    Combine un coût matière (prix/kg x portion x multiplicateur de gamme)
    et un forfait main d'oeuvre/énergie modulé par technique et complexité.

    Formule
    -------
    COGS = mat_cost + mo_cost

    Où:
    - ing_price = base_price_per_kg x GRADE_COST_MULT[grade]
    - mat_cost = ing_price x portion_kg
    - mo_cost = LABOUR_ENERGY_PER_PORTION_BASE x TECH_FACTOR[technique] x CPLX_FACTOR[complexity]

    Détails des multiplicateurs:
    - GRADE_COST_MULT: G1_FRAIS_BRUT=1.00, G2_CONSERVE=0.95, G3_SURGELE=0.92, G4_CRU_PRET=1.08, G5_CUIT_SOUS_VIDE=1.12
    - LABOUR_ENERGY_PER_PORTION_BASE = 0.40€
    - TECH_FACTOR: FROID=0.8, GRILLE=1.1, SAUTE=1.0, ROTI=1.1, FRIT=1.15, VAPEUR=0.9
    - CPLX_FACTOR: SIMPLE=1.0, COMPLEXE=1.25

    """
    ingredient_unit_price = (
        r.main_ingredient.base_priceformat_currency_eur_per_kg
        * GRADE_COST_MULT.get(r.grade, 1.0)
    )
    mat_cost = ingredient_unit_price * r.portion_kg
    mo_cost = (
        LABOUR_ENERGY_PER_PORTION_BASE
        * TECH_FACTOR.get(r.technique, 1.0)
        * CPLX_FACTOR.get(r.complexity, 1.0)
    )
    return round(mat_cost + mo_cost, 2)


def recipe_cost_and_price(
    restaurant_type: RestaurantType, recipe: SimpleRecipe
) -> Tuple[float, float]:
    """Renvoie le couple (COGS, prix_conseillé).

    Formule
    -------
    result = (compute_recipe_cogs(recipe), suggest_price(restaurant_type, recipe, FOOD_COST_TARGET))

    Cette fonction combine:
    1. compute_recipe_cogs() pour calculer le coût de revient
    2. suggest_price() avec la politique FOOD_COST_TARGET par défaut

    Retourne un tuple (COGS_en_euros, prix_suggéré_en_euros)

    """
    c = compute_recipe_cogs(recipe)
    p = suggest_price(restaurant_type, recipe, PricePolicy.FOOD_COST_TARGET)
    return (c, p)


# minutes/portion (base) par technique
TECH_MIN_PER_PORTION = {
    Technique.FROID: 2.0,
    Technique.GRILLE: 4.0,
    Technique.SAUTE: 5.0,
    Technique.ROTI: 6.0,
    Technique.FRIT: 3.5,
    Technique.VAPEUR: 4.0,
}

# multiplicateur selon complexité
CPLX_MULT = {
    Complexity.SIMPLE: 1.0,
    Complexity.COMPLEXE: 1.3,
}


def recipe_prep_minutes_per_portion(recipe) -> float:
    """Minutes de préparation par portion estimées pour une recette.

    Base dépendant de la `Technique`, multipliée selon la `Complexity`.

    Exemple
    -------
    >>> from FoodOPS_V1.domain.recipe import SimpleRecipe, Technique, Complexity
    >>> r = SimpleRecipe(name="Salade", technique=Technique.FROID, complexity=Complexity.SIMPLE)
    >>> round(recipe_prep_minutes_per_portion(r), 2)
    2.0
    >>> r2 = SimpleRecipe(name="Poêlée", technique=Technique.SAUTE, complexity=Complexity.COMPLEXE)
    >>> round(recipe_prep_minutes_per_portion(r2), 2)
    6.5
    """
    base = TECH_MIN_PER_PORTION.get(recipe.technique, 4.0)
    mult = CPLX_MULT.get(recipe.complexity, 1.0)
    return base * mult
