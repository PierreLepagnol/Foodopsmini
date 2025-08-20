"""
Modèles des employés pour FoodOps Pro (droit du travail français).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from decimal import Decimal


class EmployeePosition(Enum):
    """Postes disponibles dans un restaurant."""
    CUISINE = "cuisine"
    SALLE = "salle"
    MANAGER = "manager"
    PLONGE = "plonge"
    CAISSE = "caisse"


class EmployeeContract(Enum):
    """Types de contrats selon le droit français."""
    CDI = "cdi"
    CDD = "cdd"
    EXTRA = "extra"
    APPRENTI = "apprenti"
    STAGE = "stage"

# Backward-compatibility aliases for tests
# Some tests expect Position and ContractType names
Position = EmployeePosition
ContractType = EmployeeContract


@dataclass
class Employee:
    """
    Représente un employé avec ses caractéristiques RH françaises.

    Attributes:
        id: Identifiant unique
        name: Nom de l'employé
        position: Poste occupé
        contract: Type de contrat
        salary_gross_monthly: Salaire brut mensuel (base 35h)
        productivity: Coefficient de productivité (0.5-2.0)
        experience_months: Expérience en mois
        is_part_time: Travail à temps partiel
        part_time_ratio: Ratio temps partiel (ex: 0.5 pour mi-temps)
        sunday_work: Autorisé à travailler le dimanche
        overtime_eligible: Éligible aux heures supplémentaires
    """

    id: str
    name: str
    position: EmployeePosition
    contract: EmployeeContract
    salary_gross_monthly: Decimal
    productivity: Decimal = Decimal("1.0")
    experience_months: int = 0
    is_part_time: bool = False
    part_time_ratio: Decimal = Decimal("1.0")
    sunday_work: bool = False
    overtime_eligible: bool = True

    def __post_init__(self) -> None:
        """Validation des données."""
        if self.salary_gross_monthly < 0:
            raise ValueError(f"Le salaire brut doit être positif: {self.salary_gross_monthly}")
        if not (0.5 <= self.productivity <= 2.0):
            raise ValueError(f"La productivité doit être entre 0.5 et 2.0: {self.productivity}")
        if self.experience_months < 0:
            raise ValueError(f"L'expérience doit être positive: {self.experience_months}")
        if not (0 < self.part_time_ratio <= 1):
            raise ValueError(f"Le ratio temps partiel doit être entre 0 et 1: {self.part_time_ratio}")

        # Validation selon le type de contrat
        if self.contract == EmployeeContract.APPRENTI and self.experience_months > 24:
            raise ValueError("Un apprenti ne peut pas avoir plus de 24 mois d'expérience")
        if self.contract == EmployeeContract.STAGE and self.salary_gross_monthly > 0:
            raise ValueError("Un stagiaire ne peut pas avoir de salaire (gratification uniquement)")

    @property
    def effective_salary_monthly(self) -> Decimal:
        """Salaire effectif selon le temps de travail."""
        return self.salary_gross_monthly * self.part_time_ratio

    @property
    def hourly_rate(self) -> Decimal:
        """Taux horaire brut (base 35h/semaine)."""
        monthly_hours = Decimal("151.67")  # 35h * 52 semaines / 12 mois
        return self.effective_salary_monthly / monthly_hours

    @property
    def seniority_bonus(self) -> Decimal:
        """Prime d'ancienneté selon l'expérience."""
        if self.experience_months < 12:
            return Decimal("0")
        elif self.experience_months < 24:
            return Decimal("0.02")  # 2%
        elif self.experience_months < 60:
            return Decimal("0.05")  # 5%
        else:
            return Decimal("0.10")  # 10%

    def calculate_capacity_contribution(self, base_capacity: int) -> int:
        """
        Calcule la contribution de l'employé à la capacité du restaurant.

        Args:
            base_capacity: Capacité de base du restaurant

        Returns:
            Contribution en nombre de couverts
        """
        # Facteurs selon le poste
        position_factors = {
            EmployeePosition.CUISINE: Decimal("0.4"),
            EmployeePosition.SALLE: Decimal("0.3"),
            EmployeePosition.MANAGER: Decimal("0.2"),
            EmployeePosition.PLONGE: Decimal("0.05"),
            EmployeePosition.CAISSE: Decimal("0.05"),
        }

        base_contribution = base_capacity * position_factors.get(self.position, Decimal("0.1"))

        # Application des modificateurs
        contribution = base_contribution * self.productivity * self.part_time_ratio

        # Bonus d'expérience
        experience_bonus = min(Decimal("0.2"), Decimal(self.experience_months) / Decimal("120"))  # Max 20% après 10 ans
        contribution *= (Decimal("1") + experience_bonus)

        return int(contribution)

    def is_eligible_for_overtime(self) -> bool:
        """Vérifie si l'employé peut faire des heures supplémentaires."""
        return (self.overtime_eligible and
                self.contract in [EmployeeContract.CDI, EmployeeContract.CDD] and
                not self.is_part_time)

    def get_contract_charges_rate(self) -> Decimal:
        """
        Retourne le taux de charges patronales selon le contrat.

        Returns:
            Taux de charges patronales (ex: 0.42 pour 42%)
        """
        # Taux indicatifs - à paramétrer dans les données
        rates = {
            EmployeeContract.CDI: Decimal("0.42"),
            EmployeeContract.CDD: Decimal("0.44"),  # Légèrement plus élevé
            EmployeeContract.EXTRA: Decimal("0.45"),
            EmployeeContract.APPRENTI: Decimal("0.11"),  # Taux réduit
            EmployeeContract.STAGE: Decimal("0.00"),  # Pas de charges sur gratification
        }
        return rates.get(self.contract, Decimal("0.42"))

    def __str__(self) -> str:
        contract_str = self.contract.value.upper()
        time_str = f" ({self.part_time_ratio:.0%})" if self.is_part_time else ""
        return f"{self.name} - {self.position.value.title()} {contract_str}{time_str}"
