"""
Modèles des employés pour FoodOps Pro (droit du travail français).
"""

from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator


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


class Employee(BaseModel):
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
    salary_gross_monthly: Decimal = Field(ge=0)
    productivity: Decimal = Field(
        default=Decimal("1.0"), ge=Decimal("0.5"), le=Decimal("2.0")
    )
    experience_months: int = Field(default=0, ge=0)
    is_part_time: bool = False
    part_time_ratio: Decimal = Field(default=Decimal("1.0"), gt=0, le=1)
    sunday_work: bool = False
    overtime_eligible: bool = True

    @field_validator("salary_gross_monthly", "experience_months", "part_time_ratio")
    @classmethod
    def validate_contract_rules(cls, v, info):
        """Validation des règles selon le type de contrat."""
        if "contract" in info.data:
            contract = info.data["contract"]
            field_name = info.field_name

            if (
                field_name == "experience_months"
                and contract == EmployeeContract.APPRENTI
                and v > 24
            ):
                raise ValueError(
                    "Un apprenti ne peut pas avoir plus de 24 mois d'expérience"
                )

            if (
                field_name == "salary_gross_monthly"
                and contract == EmployeeContract.STAGE
                and v > 0
            ):
                raise ValueError(
                    "Un stagiaire ne peut pas avoir de salaire (gratification uniquement)"
                )

        return v

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

        base_contribution = base_capacity * position_factors.get(
            self.position, Decimal("0.1")
        )

        # Application des modificateurs
        contribution = base_contribution * self.productivity * self.part_time_ratio

        # Bonus d'expérience
        experience_bonus = min(
            Decimal("0.2"), Decimal(self.experience_months) / Decimal("120")
        )  # Max 20% après 10 ans
        contribution *= Decimal("1") + experience_bonus

        return int(contribution)

    def is_eligible_for_overtime(self) -> bool:
        """Vérifie si l'employé peut faire des heures supplémentaires."""
        return (
            self.overtime_eligible
            and self.contract in [EmployeeContract.CDI, EmployeeContract.CDD]
            and not self.is_part_time
        )

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
