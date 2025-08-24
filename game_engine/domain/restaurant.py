"""
Modèles des restaurants
"""

import csv
from decimal import Decimal

from pydantic import BaseModel, Field

from game_engine.domain.commerce import CommerceLocation
from game_engine.domain.recipe.ingredient_quality import IngredientQualityManager
from game_engine.domain.recipe.recipe import Recipe, RecipeItem
from game_engine.domain.staff.employee import Employee
from game_engine.domain.types import RestaurantType


class Restaurant(BaseModel):
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
    capacity_base: int = Field(gt=0)
    speed_service: Decimal = Field(gt=0)

    staff_manager: StaffManager = Field(default_factory=StaffManager)
    recipe_manager: RecipeManager = Field(default_factory=RecipeManager)
    financial_manager: FinancialManager = Field(default_factory=FinancialManager)

    menu: dict[str, Decimal] = Field(default_factory=dict)  # recipe_id -> prix_ttc
    employees: list[Employee] = Field(default_factory=list)
    cash: Decimal = Decimal("0")
    equipment_value: Decimal = Decimal("0")
    rent_monthly: Decimal = Decimal("0")
    fixed_costs_monthly: Decimal = Decimal("0")

    # État du tour courant
    staffing_level: int = Field(
        default=2, ge=0, le=3
    )  # 0=fermé, 1=léger, 2=normal, 3=renforcé
    active_recipes: list[str] = Field(default_factory=list)

    # NOUVEAU: Système qualité et réputation
    quality_manager: IngredientQualityManager = Field(
        default_factory=IngredientQualityManager
    )
    ingredient_choices: dict[str, int] = Field(
        default_factory=dict
    )  # ingredient_id -> quality_level
    reputation: Decimal = Decimal("5.0")  # Réputation sur 10
    customer_satisfaction_history: list[Decimal] = Field(default_factory=list)

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

    def load_recipes(self) -> dict[str, Recipe]:
        """
        Charge les recettes depuis les fichiers CSV.

        Returns:
            Dictionnaire des recettes par ID
        """
        # Chargement des recettes de base (métadonnées seulement)
        recipe_metadata = {}
        recipes_csv = self.data_path / "recipes.csv"

        with open(recipes_csv, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipe_metadata[row["id"]] = {
                    "id": row["id"],
                    "name": row["name"],
                    "temps_prepa_min": int(row["temps_prepa_min"]),
                    "temps_service_min": int(row["temps_service_min"]),
                    "portions": int(row["portions"]),
                    "category": row["category"],
                    "difficulty": int(row["difficulty"]),
                    "description": row["description"],
                }

        # Chargement des ingrédients des recettes
        items_csv = self.data_path / "recipe_items.csv"
        recipe_items = {}

        with open(items_csv, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipe_id = row["recipe_id"]
                if recipe_id not in recipe_items:
                    recipe_items[recipe_id] = []

                item = RecipeItem(
                    ingredient_id=row["ingredient_id"],
                    qty_brute=Decimal(row["qty_brute"]),
                    rendement_prepa=Decimal(row["rendement_prepa"]),
                    rendement_cuisson=Decimal(row["rendement_cuisson"]),
                )
                recipe_items[recipe_id].append(item)

        # Création des recettes finales avec ingrédients
        recipes = {}
        for recipe_id, metadata in recipe_metadata.items():
            items = recipe_items.get(recipe_id, [])
            if items:  # Seulement si la recette a des ingrédients
                recipe = Recipe(
                    id=metadata["id"],
                    name=metadata["name"],
                    items=items,
                    temps_prepa_min=metadata["temps_prepa_min"],
                    temps_service_min=metadata["temps_service_min"],
                    portions=metadata["portions"],
                    category=metadata["category"],
                    difficulty=metadata["difficulty"],
                    description=metadata["description"],
                )
                recipes[recipe_id] = recipe

        return recipes

    def apply_decisions(self, decisions: dict) -> None:
        """
        Applique les décisions du joueur au restaurant.

        Args:
            decisions: Dictionnaire des décisions prises
        """
        from game_engine.domain.staff.employee import Employee

        # Changements de prix
        if "price_changes" in decisions:
            for recipe_id, new_price in decisions["price_changes"].items():
                self.set_recipe_price(recipe_id, new_price)

        # Recrutements
        if "recruitments" in decisions:
            for recruit_data in decisions["recruitments"]:
                employee = Employee(
                    id=f"{self.id}_new_{len(self.employees) + 1}",
                    name=f"Nouveau {recruit_data['position'].value}",
                    position=recruit_data["position"],
                    contract=recruit_data["contract"],
                    salary_gross_monthly=recruit_data["salary"],
                    productivity=Decimal("1.0"),
                    experience_months=0,
                )
                self.add_employee(employee)

        # Campagnes marketing
        if "marketing_campaigns" in decisions:
            for campaign in decisions["marketing_campaigns"]:
                # Déduction du coût
                self.update_cash(-Decimal(str(campaign["cost"])))
                # L'effet sera appliqué dans la simulation de marché

    def display_team_info(self) -> None:
        """Affiche les informations sur l'équipe."""
        from game_engine.console_ui import print_box

        # Affichage de l'équipe actuelle
        team_info_lines = [f"ÉQUIPE ACTUELLE ({len(self.employees)} employés):"]

        total_cost = Decimal("0")
        for employee in self.employees:
            monthly_cost = employee.salary_gross_monthly * Decimal(
                "1.42"
            )  # Avec charges
            total_cost += monthly_cost
            team_info_lines.append(
                f"• {employee.name} ({employee.position.value}) - "
                f"{employee.contract.value} - {monthly_cost:.0f}€/mois"
            )

        team_info_lines.append("")
        team_info_lines.append(f"Coût total équipe: {total_cost:.0f}€/mois")

        print_box(team_info_lines, style="info")

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

    def get_active_menu(self) -> dict[str, Decimal]:
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

    def get_staff_by_position(self, position) -> list[Employee]:
        """Retourne les employés d'un poste donné."""
        return [emp for emp in self.employees if emp.position == position]

    def calculate_service_time_factor(self, recipes: list[Recipe]) -> Decimal:
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

    def setup_base_employees(self, hr_tables: dict = None) -> None:
        """
        Ajoute les employés de base selon le type de restaurant.

        Args:
            hr_tables: Tables RH (non utilisé actuellement)
        """
        from game_engine.domain.staff.employee import (
            Employee,
            EmployeeContract,
            EmployeePosition,
        )

        base_configs = {
            RestaurantType.FAST: [
                (EmployeePosition.CUISINE, 2000),
                (EmployeePosition.CAISSE, 1700),
            ],
            RestaurantType.CLASSIC: [
                (EmployeePosition.CUISINE, 2300),
                (EmployeePosition.SALLE, 2000),
            ],
            RestaurantType.GASTRONOMIQUE: [
                (EmployeePosition.CUISINE, 2800),
                (EmployeePosition.SALLE, 2200),
            ],
            RestaurantType.BRASSERIE: [
                (EmployeePosition.CUISINE, 2200),
                (EmployeePosition.SALLE, 1900),
            ],
        }

        employee_configs = base_configs.get(
            self.type, base_configs[RestaurantType.CLASSIC]
        )

        for i, (position, salary) in enumerate(employee_configs):
            employee = Employee(
                id=f"{self.id}_emp_{i + 1}",
                name=f"{position.value.title()} {i + 1}",
                position=position,
                contract=EmployeeContract.CDI,
                salary_gross_monthly=Decimal(str(salary)),
                productivity=Decimal("1.0"),
                experience_months=12,
            )
            self.add_employee(employee)

    def setup_base_menu(self, recipes: dict[str, any]) -> None:
        """
        Configure le menu de base selon le type de restaurant.

        Args:
            recipes: Dictionnaire des recettes disponibles
        """
        menu_configs = {
            RestaurantType.FAST: [
                ("burger_classic", 10.50),
                ("burger_chicken", 11.00),
                ("menu_enfant", 8.50),
            ],
            RestaurantType.CLASSIC: [
                ("pasta_bolognese", 16.00),
                ("steak_frites", 22.00),
                ("salad_caesar", 14.00),
            ],
            RestaurantType.GASTRONOMIQUE: [
                ("bowl_salmon", 28.00),
                ("risotto_mushroom", 24.00),
            ],
            RestaurantType.BRASSERIE: [
                ("croque_monsieur", 11.50),
                ("omelet_cheese", 13.00),
                ("soup_tomato", 8.50),
            ],
        }

        recipes_for_type = menu_configs.get(
            self.type, menu_configs[RestaurantType.CLASSIC]
        )

        for recipe_id, price in recipes_for_type:
            if recipe_id in recipes:
                self.set_recipe_price(recipe_id, Decimal(str(price)))
                self.activate_recipe(recipe_id)

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


def create_restaurant_from_commerce(
    location: CommerceLocation, budget: Decimal, player_num: int
) -> Restaurant:
    """Crée un restaurant à partir d'un commerce acheté."""
    # Import déféré pour éviter la dépendance circulaire
    from game_engine.console_ui import get_input

    # Nom du restaurant
    restaurant_name = get_input(
        "Nom de votre restaurant", default=f"Restaurant {player_num}"
    )

    # Création du restaurant
    remaining_budget = budget - location.total_initial_cost

    restaurant = Restaurant(
        id=f"player_{player_num}",
        name=restaurant_name,
        type=location.restaurant_type,
        capacity_base=location.size,
        speed_service=RestaurantType.get_service_speed(location.restaurant_type),
        cash=remaining_budget,
        rent_monthly=location.rent_monthly,
        fixed_costs_monthly=location.rent_monthly * Decimal("0.3"),  # Estimation
        equipment_value=Decimal("50000"),  # Valeur standard
        staffing_level=2,
    )

    # Ajout d'employés de base
    restaurant.setup_base_employees()

    # Menu de base
    # restaurant.setup_base_menu(recipes)

    return restaurant
