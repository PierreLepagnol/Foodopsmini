"""
Modèles des restaurants pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal

from .employee import Employee
from .recipe import Recipe


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
    
    def __post_init__(self) -> None:
        """Validation des données."""
        if self.capacity_base <= 0:
            raise ValueError(f"La capacité de base doit être positive: {self.capacity_base}")
        if self.speed_service <= 0:
            raise ValueError(f"La vitesse de service doit être positive: {self.speed_service}")
        if not (0 <= self.staffing_level <= 3):
            raise ValueError(f"Le niveau de staffing doit être entre 0 et 3: {self.staffing_level}")
    
    @property
    def capacity_current(self) -> int:
        """Capacité actuelle selon le staffing et les employés."""
        if self.staffing_level == 0:
            return 0
        
        # Facteurs de capacité selon le niveau de staffing
        staffing_factors = {
            1: Decimal("0.7"),   # Léger
            2: Decimal("1.0"),   # Normal
            3: Decimal("1.3"),   # Renforcé
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
        return {recipe_id: self.menu[recipe_id] 
                for recipe_id in self.active_recipes 
                if recipe_id in self.menu}
    
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
    
    def __str__(self) -> str:
        return f"{self.name} ({self.type.value}, {self.capacity_current} couverts)"
