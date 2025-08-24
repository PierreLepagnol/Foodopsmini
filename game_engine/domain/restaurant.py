"""
Modèles des restaurants pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
from decimal import Decimal

from game_engine.domain.employee import Employee
from game_engine.domain.recipe import Recipe
from game_engine.domain.ingredient_quality import IngredientQualityManager


class RestaurantType(Enum):
    """Types de restaurants avec leurs caractéristiques."""

    FAST = "fast"
    CLASSIC = "classic"
    GASTRONOMIQUE = "gastronomique"
    BRASSERIE = "brasserie"


@dataclass
class Restaurant:
    """
    Représente un restaurant avec ses caractéristiques opérationnelles.

    Attributes:
        id: Identifiant unique
        name: Nom du restaurant
        type: Type de restaurant
        capacity_base: Capacité de base (couverts/tour)
        speed_service: Facteur de vitesse de service
        menu: Recettes disponibles avec prix TTC
        employees: Liste des employés
        cash: Trésorerie actuelle
        equipment_value: Valeur du matériel (pour amortissements)
        rent_monthly: Loyer mensuel
        fixed_costs_monthly: Autres charges fixes mensuelles
    """

    id: str
    name: str
    type: RestaurantType
    capacity_base: int
    speed_service: Decimal
    menu: Dict[str, Decimal] = field(default_factory=dict)  # recipe_id -> prix_ttc
    employees: List[Employee] = field(default_factory=list)
    cash: Decimal = Decimal("0")
    equipment_value: Decimal = Decimal("0")
    rent_monthly: Decimal = Decimal("0")
    fixed_costs_monthly: Decimal = Decimal("0")

    # État du tour courant
    staffing_level: int = 2  # 0=fermé, 1=léger, 2=normal, 3=renforcé
    active_recipes: List[str] = field(default_factory=list)

    # NOUVEAU: Système qualité et réputation
    quality_manager: IngredientQualityManager = field(
        default_factory=IngredientQualityManager
    )
    ingredient_choices: Dict[str, int] = field(
        default_factory=dict
    )  # ingredient_id -> quality_level
    reputation: Decimal = Decimal("5.0")  # Réputation sur 10
    customer_satisfaction_history: List[Decimal] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.capacity_base <= 0:
            raise ValueError(
                f"La capacité de base doit être positive: {self.capacity_base}"
            )
        if self.speed_service <= 0:
            raise ValueError(
                f"La vitesse de service doit être positive: {self.speed_service}"
            )
        if not (0 <= self.staffing_level <= 3):
            raise ValueError(
                f"Le niveau de staffing doit être entre 0 et 3: {self.staffing_level}"
            )

    @property
    def capacity_current(self) -> int:
        """Capacité actuelle selon le staffing et les employés."""
        if self.staffing_level == 0:
            return 0

        # Facteurs de capacité selon le niveau de staffing
        staffing_factors = {
            1: Decimal("0.7"),  # Léger
            2: Decimal("1.0"),  # Normal
            3: Decimal("1.3"),  # Renforcé
        }

        base_capacity = self.capacity_base * self.speed_service
        staffing_factor = staffing_factors.get(self.staffing_level, Decimal("1.0"))

        # Contribution des employés
        employee_contribution = sum(
            emp.calculate_capacity_contribution(self.capacity_base)
            for emp in self.employees
        )

        # Capacité finale
        total_capacity = base_capacity * staffing_factor + employee_contribution
        return int(total_capacity)

    @property
    def monthly_staff_cost(self) -> Decimal:
        """Coût mensuel du personnel (salaires + charges)."""
        total_cost = Decimal("0")
        for employee in self.employees:
            gross_salary = employee.effective_salary_monthly
            charges_rate = employee.get_contract_charges_rate()
            total_cost += gross_salary * (1 + charges_rate)
        return total_cost

    @property
    def monthly_fixed_costs(self) -> Decimal:
        """Total des charges fixes mensuelles."""
        return self.rent_monthly + self.fixed_costs_monthly

    def add_employee(self, employee: Employee) -> None:
        """Ajoute un employé au restaurant."""
        if any(emp.id == employee.id for emp in self.employees):
            raise ValueError(f"Employé {employee.id} déjà présent")
        self.employees.append(employee)

    def remove_employee(self, employee_id: str) -> bool:
        """
        Supprime un employé du restaurant.

        Args:
            employee_id: ID de l'employé à supprimer

        Returns:
            True si l'employé a été supprimé
        """
        initial_count = len(self.employees)
        self.employees = [emp for emp in self.employees if emp.id != employee_id]
        return len(self.employees) < initial_count

    def set_recipe_price(self, recipe_id: str, price_ttc: Decimal) -> None:
        """
        Définit le prix TTC d'une recette.

        Args:
            recipe_id: ID de la recette
            price_ttc: Prix TTC
        """
        if price_ttc < 0:
            raise ValueError(f"Le prix doit être positif: {price_ttc}")
        self.menu[recipe_id] = price_ttc

    def activate_recipe(self, recipe_id: str) -> None:
        """Active une recette dans le menu."""
        if recipe_id not in self.menu:
            raise ValueError(f"Recette {recipe_id} non présente dans le menu")
        if recipe_id not in self.active_recipes:
            self.active_recipes.append(recipe_id)

    def deactivate_recipe(self, recipe_id: str) -> None:
        """Désactive une recette du menu."""
        if recipe_id in self.active_recipes:
            self.active_recipes.remove(recipe_id)

    def get_active_menu(self) -> Dict[str, Decimal]:
        """Retourne le menu actif avec les prix."""
        return {
            recipe_id: self.menu[recipe_id]
            for recipe_id in self.active_recipes
            if recipe_id in self.menu
        }

    def get_average_ticket(self) -> Decimal:
        """Calcule le ticket moyen du menu actif."""
        active_menu = self.get_active_menu()
        if not active_menu:
            return Decimal("0")
        return sum(active_menu.values()) / len(active_menu)

    def get_staff_by_position(self, position) -> List[Employee]:
        """Retourne les employés d'un poste donné."""
        return [emp for emp in self.employees if emp.position == position]

    def calculate_service_time_factor(self, recipes: List[Recipe]) -> Decimal:
        """
        Calcule le facteur de temps de service selon les recettes actives.

        Args:
            recipes: Liste des recettes du menu

        Returns:
            Facteur multiplicateur du temps de service
        """
        if not self.active_recipes:
            return Decimal("1.0")

        # Temps moyen des recettes actives
        total_time = 0
        count = 0
        for recipe in recipes:
            if recipe.id in self.active_recipes:
                total_time += recipe.temps_service_min
                count += 1

        if count == 0:
            return Decimal("1.0")

        avg_time = total_time / count

        # Facteur basé sur le temps moyen (référence: 10 minutes)
        reference_time = 10
        return Decimal(str(avg_time / reference_time))

    def update_cash(self, amount: Decimal, description: str = "") -> None:
        """
        Met à jour la trésorerie.

        Args:
            amount: Montant (positif ou négatif)
            description: Description de l'opération
        """
        self.cash += amount

    # === MÉTHODES QUALITÉ ===

    def set_ingredient_quality(self, ingredient_id: str, quality_level: int) -> None:
        """
        Définit le niveau de qualité pour un ingrédient.

        Args:
            ingredient_id: ID de l'ingrédient
            quality_level: Niveau de qualité (1-5)
        """
        if not (1 <= quality_level <= 5):
            raise ValueError(
                f"Le niveau de qualité doit être entre 1 et 5: {quality_level}"
            )

        self.ingredient_choices[ingredient_id] = quality_level

    def get_overall_quality_score(self) -> Decimal:
        """
        Calcule le score de qualité global du restaurant.

        Returns:
            Score de qualité (1.0 à 5.0)
        """
        if not self.ingredient_choices:
            # Score de base selon le type de restaurant
            base_scores = {
                RestaurantType.FAST: Decimal("2.0"),
                RestaurantType.CLASSIC: Decimal("2.5"),
                RestaurantType.BRASSERIE: Decimal("3.0"),
                RestaurantType.GASTRONOMIQUE: Decimal("3.5"),
            }
            return base_scores.get(self.type, Decimal("2.5"))

        # Score moyen des ingrédients choisis
        avg_ingredient_quality = sum(self.ingredient_choices.values()) / len(
            self.ingredient_choices
        )

        # Score de base selon le type
        base_quality = {
            RestaurantType.FAST: 1.5,
            RestaurantType.CLASSIC: 2.0,
            RestaurantType.BRASSERIE: 2.5,
            RestaurantType.GASTRONOMIQUE: 3.0,
        }.get(self.type, 2.0)

        # Bonus staff (formation)
        staff_bonus = (self.staffing_level - 1) * 0.2

        # Score final
        final_score = base_quality + (avg_ingredient_quality - 2.0) * 0.6 + staff_bonus
        return Decimal(str(min(5.0, max(1.0, final_score))))

    def get_quality_description(self) -> str:
        """Retourne une description textuelle de la qualité."""
        score = float(self.get_overall_quality_score())

        if score >= 4.5:
            return "⭐⭐⭐⭐⭐ Luxe"
        elif score >= 3.5:
            return "⭐⭐⭐⭐ Premium"
        elif score >= 2.5:
            return "⭐⭐⭐ Supérieur"
        elif score >= 1.5:
            return "⭐⭐ Standard"
        else:
            return "⭐ Économique"

    def update_customer_satisfaction(self, satisfaction: Decimal) -> None:
        """
        Met à jour la satisfaction client et la réputation.

        Args:
            satisfaction: Score de satisfaction (0-5)
        """
        # Ajouter à l'historique
        self.customer_satisfaction_history.append(satisfaction)

        # Garder seulement les 10 dernières mesures
        if len(self.customer_satisfaction_history) > 10:
            self.customer_satisfaction_history = self.customer_satisfaction_history[
                -10:
            ]

        # Mise à jour progressive de la réputation
        target_reputation = satisfaction * 2  # Satisfaction 0-5 -> Réputation 0-10
        reputation_change = (target_reputation - self.reputation) * Decimal("0.15")
        self.reputation = max(
            Decimal("0"), min(Decimal("10"), self.reputation + reputation_change)
        )

    def get_average_satisfaction(self) -> Decimal:
        """Retourne la satisfaction moyenne récente."""
        if not self.customer_satisfaction_history:
            return Decimal("2.5")  # Neutre par défaut

        return sum(self.customer_satisfaction_history) / len(
            self.customer_satisfaction_history
        )

    def calculate_quality_cost_impact(self) -> Decimal:
        """
        Calcule l'impact de la qualité sur les coûts.

        Returns:
            Multiplicateur de coût (ex: 1.25 = +25%)
        """
        if not self.ingredient_choices:
            return Decimal("1.0")

        # Multiplicateurs de coût par niveau de qualité
        cost_multipliers = {
            1: Decimal("0.70"),  # -30%
            2: Decimal("1.00"),  # Standard
            3: Decimal("1.25"),  # +25%
            4: Decimal("1.50"),  # +50%
            5: Decimal("2.00"),  # +100%
        }

        # Moyenne pondérée des multiplicateurs
        total_multiplier = Decimal("0")
        for quality_level in self.ingredient_choices.values():
            total_multiplier += cost_multipliers.get(quality_level, Decimal("1.0"))

        return total_multiplier / len(self.ingredient_choices)

    def get_quality_attractiveness_factor(
        self, customer_segment: str = "general"
    ) -> Decimal:
        """
        Calcule le facteur d'attractivité basé sur la qualité.

        Args:
            customer_segment: Segment de clientèle

        Returns:
            Multiplicateur d'attractivité
        """
        quality_score = float(self.get_overall_quality_score())

        # Sensibilité à la qualité par segment
        quality_sensitivity = {
            "students": 0.5,  # Moins sensibles
            "families": 1.0,  # Sensibilité normale
            "foodies": 1.5,  # Très sensibles
            "general": 1.0,  # Par défaut
        }.get(customer_segment, 1.0)

        # Facteur de base selon le score
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

        # Ajustement selon la sensibilité
        if base_factor > 1.0:
            bonus = (base_factor - 1.0) * quality_sensitivity
            return Decimal(str(1.0 + bonus))
        else:
            malus = (1.0 - base_factor) * quality_sensitivity
            return Decimal(str(1.0 - malus))

    def __str__(self) -> str:
        quality_desc = self.get_quality_description()
        return f"{self.name} ({self.type.value}, {self.capacity_current} couverts, {quality_desc})"
