from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, Optional, Tuple, Type

import numpy as np
from pydantic import BaseModel

from FoodOPS_V1.core.accounting import Ledger, TypeOperation, post_opening
from FoodOPS_V1.domain.ingredients import FoodGrade
from FoodOPS_V1.domain.inventory import Inventory
from FoodOPS_V1.domain.local import Local
from FoodOPS_V1.domain.recipe import SimpleRecipe
from FoodOPS_V1.domain.scenario import FinancingPlan
from FoodOPS_V1.domain.staff import Employe
from FoodOPS_V1.domain.types import RestaurantType

MARGIN_BY_RESTO = {"FAST_FOOD": 2.5, "BISTRO": 3.0, "GASTRO": 3.8}


class Restaurant(BaseModel):
    """Base restaurant with shared behavior/fields."""

    # Per-subclass constants
    TYPE: ClassVar[RestaurantType] = RestaurantType.FAST_FOOD
    DEFAULT_MARGIN: ClassVar[float] = 2.5
    SERVICE_SPEED: ClassVar[float] = 1.00
    SERVICE_MINUTES_PER_COVER: ClassVar[float] = 0.0
    preferences: List[FoodGrade] = field(default_factory=list)

    # Common fields
    name: str
    local: Local
    notoriety: float = 0.5  # entre 0.0 et 1.0
    equipe: List[Employe] = field(default_factory=list)
    marketing_budget: float = 0.0
    menu: List[SimpleRecipe] = field(default_factory=list)
    funds: float = 0.0
    ledger: Ledger = None
    equipment_invest: float = 0.0
    bpi_outstanding: float = 0.0
    bpi_rate_annual: float = 0.0
    monthly_bpi: float = 0.0
    bank_outstanding: float = 0.0
    bank_rate_annual: float = 0.0
    monthly_bank: float = 0.0
    charges_reccurentes: float = 0.0
    inventory: Inventory = field(default_factory=Inventory)
    turn_cogs: float = 0.0
    service_minutes_left: float = 0.0
    kitchen_minutes_left: float = 0.0
    rh_satisfaction: float = 0.0

    # Optional override per instance (kept if you need flexibility)
    margin_override: Optional[float] = None

    # Canonical margin always comes from subclass unless overridden
    @property
    def margin(self) -> float:
        return (
            self.margin_override
            if self.margin_override is not None
            else self.DEFAULT_MARGIN
        )

    # If you still want a "type" string for JSON/DB
    @property
    def type(self) -> str:
        return self.TYPE

    @property
    def service_speed(self) -> float:
        return self.SERVICE_SPEED

    def add_recipe_to_menu(self, recipe: SimpleRecipe) -> None:
        if all(r.name != recipe.name for r in self.menu):
            self.menu.append(recipe)

    def reset_rh_minutes(self) -> None:
        total_service = 0
        total_kitchen = 0
        for e in self.equipe or []:
            if hasattr(e, "compute_minutes"):
                e.compute_minutes()
            total_service += getattr(e, "service_minutes", 0)
            total_kitchen += getattr(e, "kitchen_minutes", 0)
        self.service_minutes_left = int(total_service)
        self.kitchen_minutes_left = int(total_kitchen)

    def consume_service_minutes(self, minutes: int) -> None:
        self.service_minutes_left = max(0, self.service_minutes_left - int(minutes))

    def consume_kitchen_minutes(self, minutes: int) -> None:
        self.kitchen_minutes_left = max(0, self.kitchen_minutes_left - int(minutes))

    def calculate_staff_workload_ratio(self) -> float:
        """Calcule le taux d'utilisation du personnel (entre 0 et 1).
        
        Returns:
            0.0 = personnel complètement inactif
            0.5 = utilisation modérée (idéal)
            1.0 = personnel à fond en permanence
        """
        # Total de minutes disponibles dans l'équipe
        total_available_minutes = (
            getattr(self, "service_minutes_left", 0) + 
            getattr(self, "kitchen_minutes_left", 0)
        )
        
        # Minutes effectivement utilisées par l'équipe
        minutes_actually_used = 0
        for employee in self.equipe or []:
            minutes_actually_used += (
                getattr(employee, "service_minutes", 0) + 
                getattr(employee, "kitchen_minutes", 0)
            )
        
        # Calcule le ratio d'utilisation
        if total_available_minutes == 0:
            return 0.0
        return minutes_actually_used / total_available_minutes
    
    def determine_satisfaction_change_based_on_workload(self, workload_ratio: float) -> float:
        """Détermine comment la satisfaction évolue selon la charge de travail.
        
        Args:
            workload_ratio: Taux d'utilisation du personnel (0.0 à 1.0)
            
        Returns:
            Changement de satisfaction (évolution mensuelle)
        """
        if workload_ratio > 0.95:  # Plus de 95% d'utilisation
            return -0.06  # Burn-out : grosse baisse de satisfaction
        elif workload_ratio > 0.85:  # Entre 85% et 95%
            return -0.03  # Sur-stress : légère baisse
        elif workload_ratio < 0.35:  # Moins de 35% d'utilisation
            return -0.02  # Ennui : baisse de satisfaction
        elif workload_ratio < 0.55:  # Entre 35% et 55%
            return +0.01  # Rythme tranquille : légère hausse
        else:  # Entre 55% et 85% (zone idéale)
            return +0.02  # Équilibre parfait : bonne hausse
    
    def update_rh_satisfaction(self) -> None:
        """Met à jour la satisfaction du personnel selon sa charge de travail.
        
        Un personnel trop sollicité (burn-out) ou pas assez (ennui) voit sa 
        satisfaction baisser. L'idéal est une charge de travail équilibrée.
        """
        workload_ratio = self.calculate_staff_workload_ratio()
        satisfaction_change = self.determine_satisfaction_change_based_on_workload(workload_ratio)
        
        # Applique le changement en restant dans les bornes [0.0, 1.0]
        current_satisfaction = getattr(self, "rh_satisfaction", 0.8)  # Défaut : 0.8
        new_satisfaction = current_satisfaction + satisfaction_change
        self.rh_satisfaction = max(0.0, min(1.0, new_satisfaction))

    def compute_maximum_monthly_customers(self) -> int:
        """
        Calcule combien de clients ce restaurant peut servir au maximum en un mois.

        Dans la vraie vie, un restaurant ne peut pas servir un nombre infini de clients.
        Sa capacité dépend de :
        
        1. **Nombre de places assises** : combien de personnes peuvent manger en même temps
        2. **Services par jour** : déjeuner + dîner = 2 services
        3. **Jours d'ouverture** : on considère 30 jours par mois
        4. **Vitesse de service** : 
           - Fast-food : service rapide → plus de rotations possibles
           - Bistro : service normal
           - Gastro : service lent (expérience longue) → moins de rotations

        Returns:
            Nombre maximum de clients que le restaurant peut servir en un mois.
            
        Exemple concret :
            Restaurant de 20 places :
            - Théorique max : 20 places × 2 services × 30 jours = 1200 clients/mois
            - Si bistro (vitesse 0.8) : 1200 × 0.8 = 960 clients réels maximum
        """
        # Hypothèses de calcul réalistes
        SERVICES_PER_DAY = 2    # Déjeuner + Dîner
        DAYS_PER_MONTH = 30     # Mois de 30 jours
        
        # Capacité théorique si le restaurant était plein en permanence
        theoretical_maximum = (
            self.local.capacite_clients *  # Nombre de places assises
            SERVICES_PER_DAY *            # 2 services par jour
            DAYS_PER_MONTH                # 30 jours
        )
        
        # Capacité réelle tenant compte de la vitesse de service du concept
        realistic_maximum = theoretical_maximum * self.service_speed
        
        return max(0, int(realistic_maximum))

    # Enregistrement des écritures comptables

    def post_opening(self, financing_plan: FinancingPlan):
        lines = post_opening(
            cash=self.funds,  # tréso initiale
            equipment=self.equipment_invest,  # immobilisations
            loans_total=financing_plan.bank_loan
            + financing_plan.bpi_loan,  # dette initiale
        )
        self.ledger.post(0, "Ouverture", lines)

    def post_sales(self, tour: int, chiffre_affaires: float):
        if chiffre_affaires > 0:
            self.ledger.post(
                tour,
                "Ventes",
                [
                    ("512", chiffre_affaires, TypeOperation.DEBIT),
                    ("70", chiffre_affaires, TypeOperation.CREDIT),
                ],
            )
        else:
            print(f"Chiffre d'affaires négatif: {chiffre_affaires}")

    def post_cogs(self, tour: int, cogs: float):
        """Enregistre les achats consommés (CoGS) du tour."""
        if cogs > 0:
            self.ledger.post(
                tour,
                "Achats consommés (matières)",
                [
                    ("60", cogs, TypeOperation.DEBIT),
                    ("512", cogs, TypeOperation.CREDIT),
                ],
            )
        else:
            print(f"Coût des matières premières négatif: {cogs}")

    def post_services_ext(self, tour: int, amount: float):
        """Enregistre les services extérieurs (loyer, abonnements, marketing)."""
        if amount > 0:
            self.ledger.post(
                tour,
                "Services extérieurs (loyer, abonnements, marketing)",
                [
                    ("61", amount, TypeOperation.DEBIT),
                    ("512", amount, TypeOperation.CREDIT),
                ],
            )
        else:
            print(f"Montant des services extérieurs négatif: {amount}")

    def post_payroll(self, tour: int, payroll_total: float):
        """Enregistre les charges de personnel.

        Args:
            ledger: Grand livre à alimenter.
            tour: Tour courant (mois).
            payroll_total: Masse salariale totale (salaires + charges) payée.
        """
        if payroll_total > 0:
            lines = [
                ("64", payroll_total, TypeOperation.DEBIT),
                ("512", payroll_total, TypeOperation.CREDIT),
            ]
            self.ledger.post(tour, "Charges de personnel", lines)
        else:
            print(f"Montant des charges de personnel négatif: {payroll_total}")

    def post_depreciation(self, tour: int, dotation: float):
        """Enregistre la dotation aux amortissements du tour.

        Args:
            ledger: Grand livre à alimenter.
            tour: Tour courant (mois).
            dotation: Montant de la dotation de la période.
        """
        if dotation > 0:
            lines = [
                ("681", dotation, TypeOperation.DEBIT),
                ("2815", dotation, TypeOperation.CREDIT),
            ]
            self.ledger.post(tour, "Dotations aux amortissements", lines)
        else:
            print(f"Montant des dotations aux amortissements négatif: {dotation}")

    def post_loan_payment(
        self, tour: int, interest: float, principal: float, label: str
    ):
        """Enregistre un remboursement d'emprunt (intérêts et/ou capital).

        Args:
            ledger: Grand livre à alimenter.
            tour: Tour courant (mois).
            interest: Part d'intérêts payée (charge 66).
            principal: Part de capital remboursée (diminution du 164).
            label: Suffixe descriptif du prêt (ex: "banque A").
        """
        lines: List[Tuple[str, float, TypeOperation]] = []
        if interest < 0 or principal < 0:
            print(
                f"Montant d'intérêts ou de capital négatif: {interest} ou {principal}"
            )
        if interest > 0:
            lines.extend(
                [
                    ("66", interest, TypeOperation.DEBIT),
                    ("512", interest, TypeOperation.CREDIT),
                ]
            )
        if principal > 0:
            lines.extend(
                [
                    ("164", principal, TypeOperation.DEBIT),
                    ("512", principal, TypeOperation.CREDIT),
                ]
            )
        if lines:
            self.ledger.post(tour, f"Remboursement {label}", lines)

    def month_amortization(self) -> float:
        """Calcule la dotation d'amortissement mensuelle linéaire.

        La durée d'amortissement provient de `EQUIP_AMORT_YEARS`. Un tour
        correspond à un mois.

        Returns:
            Montant mensuel de la dotation (arrondi à 2 décimales). Retourne 0 si
            `amount <= 0`.
        """
        amount = self.equipment_invest
        EQUIP_AMORT_YEARS = 5  # Amortissement linéaire des équipements (années)
        months = EQUIP_AMORT_YEARS * 12  # Nombre de mois d'amortissement
        return 0.0 if amount <= 0 else round(amount / months, 2)

    # FIN - Enregistrement des écritures comptables

    def compute_median_price(self) -> float:
        """Prix médian des menus du restaurant."""
        prix_des_items = [item.price for item in self.menu if item is not None]
        return np.median(prix_des_items) if prix_des_items else 0.0

    def get_available_portions(self) -> int:
        """Retourne le nombre total de portions finies disponibles en stock.

        Returns:
            Nombre total de portions finies disponibles, ou 0 si aucune
        """
        return self.inventory.total_finished_portions()

    def _fixed_costs_of(self) -> float:
        """Calcule les coûts fixes mensuels totaux du restaurant.

        Args:
            restaurant: Restaurant dont calculer les coûts fixes

        Returns:
            Somme du loyer du local et des charges récurrentes mensuelles
        """
        # Somme du loyer du local et des charges récurrentes mensuelles
        return self.local.loyer + self.charges_reccurentes

    def _rh_cost_of(self) -> float:
        """Calcule le coût salarial mensuel total de l'équipe.

        Args:
            restaurant: Restaurant avec l'équipe à évaluer

        Returns:
            Somme de tous les salaires totaux de l'équipe, arrondie à 2 décimales
        """
        # Additionne tous les salaires de l'équipe et arrondit à 2 décimales
        return round(sum([employee.salaire_total for employee in self.equipe]), 2)

    def _service_minutes_per_cover(self) -> float:
        """Retourne le temps de service standard par couvert selon le type de restaurant.

        Args:
            rtype: Type de restaurant (FAST_FOOD, BISTRO, GASTRO)

        Returns:
            Durée en minutes pour servir un couvert de ce type de restaurant
        """
        # Récupère la durée de service depuis la constante globale selon le type de restaurant
        return float(self.SERVICE_MINUTES_PER_COVER)


class FastFoodRestaurant(Restaurant):
    TYPE: ClassVar[RestaurantType] = RestaurantType.FAST_FOOD
    DEFAULT_MARGIN: ClassVar[float] = 2.5
    SERVICE_SPEED: ClassVar[float] = 1.00
    preferences: List[FoodGrade] = [FoodGrade.G3_SURGELE, FoodGrade.G1_FRAIS_BRUT]
    SERVICE_MINUTES_PER_COVER: ClassVar[float] = 1.5


class BistroRestaurant(Restaurant):
    TYPE: ClassVar[RestaurantType] = RestaurantType.BISTRO
    DEFAULT_MARGIN: ClassVar[float] = 3.0
    SERVICE_SPEED: ClassVar[float] = 0.80
    preferences: List[FoodGrade] = [FoodGrade.G1_FRAIS_BRUT, FoodGrade.G3_SURGELE]
    SERVICE_MINUTES_PER_COVER: ClassVar[float] = 4.0


class GastroRestaurant(Restaurant):
    TYPE: ClassVar[RestaurantType] = RestaurantType.GASTRO
    DEFAULT_MARGIN: ClassVar[float] = 3.8
    SERVICE_SPEED: ClassVar[float] = 0.50
    preferences: List[FoodGrade] = [FoodGrade.G1_FRAIS_BRUT, FoodGrade.G3_SURGELE]
    SERVICE_MINUTES_PER_COVER: ClassVar[float] = 7.0


def make_restaurant(kind: str | RestaurantType, **kwargs) -> Restaurant:
    """Factory that creates a restaurant subclass instance from kind.

    Accepts either a string (e.g., "FAST_FOOD") or a `RestaurantType` enum.
    """
    if isinstance(kind, str):
        kind = RestaurantType[kind]

    if kind == RestaurantType.FAST_FOOD:
        return FastFoodRestaurant(**kwargs)
    elif kind == RestaurantType.BISTRO:
        return BistroRestaurant(**kwargs)
    elif kind == RestaurantType.GASTRO:
        return GastroRestaurant(**kwargs)
