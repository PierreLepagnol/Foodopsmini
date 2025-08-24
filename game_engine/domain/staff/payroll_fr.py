"""
Calcul de la paie française pour FoodOps Pro.
"""

from dataclasses import dataclass
from decimal import Decimal

from game_engine.domain.staff.employee import Employee, EmployeeContract


@dataclass
class PayrollResult:
    """
    Résultat du calcul de paie pour un employé.

    Attributes:
        employee_id: ID de l'employé
        employee_name: Nom de l'employé
        period: Période de paie
        gross_salary: Salaire brut
        social_charges_employee: Charges salariales
        social_charges_employer: Charges patronales
        net_salary: Salaire net
        total_cost: Coût total employeur
        overtime_hours: Heures supplémentaires
        overtime_pay: Rémunération heures sup
        sunday_hours: Heures dimanche
        sunday_premium: Prime dimanche
    """

    employee_id: str
    employee_name: str
    period: str
    gross_salary: Decimal
    social_charges_employee: Decimal = Decimal("0")
    social_charges_employer: Decimal = Decimal("0")
    net_salary: Decimal = Decimal("0")
    total_cost: Decimal = Decimal("0")
    overtime_hours: Decimal = Decimal("0")
    overtime_pay: Decimal = Decimal("0")
    sunday_hours: Decimal = Decimal("0")
    sunday_premium: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        """Calcule les totaux après initialisation."""
        self.net_salary = self.gross_salary - self.social_charges_employee
        self.total_cost = self.gross_salary + self.social_charges_employer


class PayrollCalculator:
    """
    Calculateur de paie selon la réglementation française.
    """

    def __init__(self, social_charges_config: dict[str, dict[str, Decimal]]) -> None:
        """
        Initialise le calculateur avec la configuration des charges.

        Args:
            social_charges_config: Configuration des taux de charges par contrat
        """
        self.social_charges_config = social_charges_config

        # Paramètres légaux français (à jour 2024)
        self.smic_hourly = Decimal("11.65")  # SMIC horaire 2024
        self.legal_working_hours = Decimal("35")  # 35h/semaine
        self.overtime_rate_25 = Decimal("1.25")  # Majoration 25% (heures 36-43)
        self.overtime_rate_50 = Decimal("1.50")  # Majoration 50% (heures 44+)
        self.sunday_premium_rate = Decimal("0.30")  # Prime dimanche 30%

        # Plafond sécurité sociale 2024 (mensuel)
        self.social_security_ceiling = Decimal("3864")

    def calculate_payroll(
        self,
        employee: Employee,
        hours_worked: Decimal = Decimal("151.67"),
        sunday_hours: Decimal = Decimal("0"),
        period: str = "",
    ) -> PayrollResult:
        """
        Calcule la paie d'un employé.

        Args:
            employee: Employé concerné
            hours_worked: Heures travaillées dans le mois
            sunday_hours: Heures travaillées le dimanche
            period: Période de paie

        Returns:
            Résultat du calcul de paie
        """
        # Heures normales et supplémentaires
        monthly_normal_hours = Decimal("151.67")  # 35h * 52 semaines / 12 mois
        min(hours_worked, monthly_normal_hours)
        overtime_hours = max(Decimal("0"), hours_worked - monthly_normal_hours)

        # Salaire de base
        base_salary = employee.effective_salary_monthly

        # Calcul des heures supplémentaires
        overtime_pay = self._calculate_overtime_pay(employee, overtime_hours)

        # Prime dimanche
        sunday_premium = self._calculate_sunday_premium(employee, sunday_hours)

        # Salaire brut total
        gross_salary = base_salary + overtime_pay + sunday_premium

        # Charges sociales
        employee_charges = self._calculate_employee_charges(employee, gross_salary)
        employer_charges = self._calculate_employer_charges(employee, gross_salary)

        return PayrollResult(
            employee_id=employee.id,
            employee_name=employee.name,
            period=period,
            gross_salary=gross_salary,
            social_charges_employee=employee_charges,
            social_charges_employer=employer_charges,
            overtime_hours=overtime_hours,
            overtime_pay=overtime_pay,
            sunday_hours=sunday_hours,
            sunday_premium=sunday_premium,
        )

    def _calculate_overtime_pay(
        self, employee: Employee, overtime_hours: Decimal
    ) -> Decimal:
        """
        Calcule la rémunération des heures supplémentaires.

        Args:
            employee: Employé concerné
            overtime_hours: Nombre d'heures supplémentaires

        Returns:
            Montant des heures supplémentaires
        """
        if not employee.is_eligible_for_overtime() or overtime_hours <= 0:
            return Decimal("0")

        hourly_rate = employee.hourly_rate

        # Répartition des heures sup (25% puis 50%)
        hours_25 = min(overtime_hours, Decimal("8"))  # 8 premières heures à 25%
        hours_50 = max(Decimal("0"), overtime_hours - Decimal("8"))  # Au-delà à 50%

        overtime_pay = hours_25 * hourly_rate * (
            self.overtime_rate_25 - 1
        ) + hours_50 * hourly_rate * (self.overtime_rate_50 - 1)

        return overtime_pay

    def _calculate_sunday_premium(
        self, employee: Employee, sunday_hours: Decimal
    ) -> Decimal:
        """
        Calcule la prime de travail dominical.

        Args:
            employee: Employé concerné
            sunday_hours: Heures travaillées le dimanche

        Returns:
            Montant de la prime dimanche
        """
        if not employee.sunday_work or sunday_hours <= 0:
            return Decimal("0")

        hourly_rate = employee.hourly_rate
        return sunday_hours * hourly_rate * self.sunday_premium_rate

    def _calculate_employee_charges(
        self, employee: Employee, gross_salary: Decimal
    ) -> Decimal:
        """
        Calcule les charges salariales.

        Args:
            employee: Employé concerné
            gross_salary: Salaire brut

        Returns:
            Montant des charges salariales
        """
        contract_type = employee.contract.value

        if contract_type not in self.social_charges_config:
            return Decimal("0")

        config = self.social_charges_config[contract_type]
        employee_rate = config.get("employee_rate", Decimal("0.22"))  # ~22% en moyenne

        # Application du plafond sécurité sociale pour certaines cotisations
        capped_salary = min(gross_salary, self.social_security_ceiling)

        return capped_salary * employee_rate

    def _calculate_employer_charges(
        self, employee: Employee, gross_salary: Decimal
    ) -> Decimal:
        """
        Calcule les charges patronales.

        Args:
            employee: Employé concerné
            gross_salary: Salaire brut

        Returns:
            Montant des charges patronales
        """
        contract_type = employee.contract.value

        if contract_type not in self.social_charges_config:
            # Taux par défaut selon le contrat
            default_rates = {
                "cdi": Decimal("0.42"),
                "cdd": Decimal("0.44"),
                "extra": Decimal("0.45"),
                "apprenti": Decimal("0.11"),
                "stage": Decimal("0.00"),
            }
            employer_rate = default_rates.get(contract_type, Decimal("0.42"))
        else:
            config = self.social_charges_config[contract_type]
            employer_rate = config.get("employer_rate", Decimal("0.42"))

        # Réductions spécifiques
        if employee.contract == EmployeeContract.APPRENTI:
            # Réduction apprentissage
            return gross_salary * employer_rate

        # Application du plafond pour certaines cotisations
        capped_salary = min(gross_salary, self.social_security_ceiling)
        uncapped_salary = gross_salary

        # Cotisations plafonnées (retraite, chômage) + non plafonnées (famille, accidents)
        capped_charges = capped_salary * Decimal("0.25")  # ~25% plafonnées
        uncapped_charges = uncapped_salary * Decimal("0.17")  # ~17% non plafonnées

        return capped_charges + uncapped_charges

    def calculate_team_payroll(
        self,
        employees: list[Employee],
        hours_per_employee: dict[str, Decimal] = None,
        sunday_hours_per_employee: dict[str, Decimal] = None,
        period: str = "",
    ) -> list[PayrollResult]:
        """
        Calcule la paie pour une équipe d'employés.

        Args:
            employees: Liste des employés
            hours_per_employee: Heures par employé (optionnel)
            sunday_hours_per_employee: Heures dimanche par employé (optionnel)
            period: Période de paie

        Returns:
            Liste des résultats de paie
        """
        results = []

        for employee in employees:
            hours = (
                hours_per_employee.get(employee.id, Decimal("151.67"))
                if hours_per_employee
                else Decimal("151.67")
            )
            sunday_hours = (
                sunday_hours_per_employee.get(employee.id, Decimal("0"))
                if sunday_hours_per_employee
                else Decimal("0")
            )

            result = self.calculate_payroll(employee, hours, sunday_hours, period)
            results.append(result)

        return results

    def get_payroll_summary(
        self, payroll_results: list[PayrollResult]
    ) -> dict[str, Decimal]:
        """
        Génère un résumé de la masse salariale.

        Args:
            payroll_results: Résultats de paie

        Returns:
            Résumé avec totaux
        """
        total_gross = sum(result.gross_salary for result in payroll_results)
        total_net = sum(result.net_salary for result in payroll_results)
        total_employer_charges = sum(
            result.social_charges_employer for result in payroll_results
        )
        total_cost = sum(result.total_cost for result in payroll_results)

        return {
            "total_gross_salary": total_gross,
            "total_net_salary": total_net,
            "total_employer_charges": total_employer_charges,
            "total_cost": total_cost,
            "average_charge_rate": (total_employer_charges / total_gross * 100)
            if total_gross > 0
            else Decimal("0"),
        }
