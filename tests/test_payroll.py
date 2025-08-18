"""
Tests pour le calcul de la paie française.
"""

import pytest
from decimal import Decimal

from src.foodops_pro.domain.employee import Employee, EmployeePosition, EmployeeContract
from src.foodops_pro.core.payroll_fr import PayrollCalculator, PayrollResult


@pytest.fixture
def sample_social_charges_config():
    """Configuration des charges sociales pour les tests."""
    return {
        "cdi": {
            "employee_rate": Decimal("0.22"),
            "employer_rate": Decimal("0.42")
        },
        "cdd": {
            "employee_rate": Decimal("0.22"),
            "employer_rate": Decimal("0.44")
        },
        "extra": {
            "employee_rate": Decimal("0.22"),
            "employer_rate": Decimal("0.45")
        },
        "apprenti": {
            "employee_rate": Decimal("0.05"),
            "employer_rate": Decimal("0.11")
        },
        "stage": {
            "employee_rate": Decimal("0.00"),
            "employer_rate": Decimal("0.00")
        }
    }


@pytest.fixture
def sample_employees():
    """Employés de test."""
    return [
        Employee(
            id="emp1",
            name="Jean Dupont",
            position=EmployeePosition.CUISINE,
            contract=EmployeeContract.CDI,
            salary_gross_monthly=Decimal("2200.00"),
            productivity=Decimal("1.1"),
            experience_months=24
        ),
        Employee(
            id="emp2",
            name="Marie Martin",
            position=EmployeePosition.SALLE,
            contract=EmployeeContract.CDD,
            salary_gross_monthly=Decimal("1900.00"),
            productivity=Decimal("1.0"),
            experience_months=6
        ),
        Employee(
            id="emp3",
            name="Pierre Apprenti",
            position=EmployeePosition.CUISINE,
            contract=EmployeeContract.APPRENTI,
            salary_gross_monthly=Decimal("800.00"),
            productivity=Decimal("0.8"),
            experience_months=8
        ),
        Employee(
            id="emp4",
            name="Sophie Extra",
            position=EmployeePosition.SALLE,
            contract=EmployeeContract.EXTRA,
            salary_gross_monthly=Decimal("1700.00"),
            productivity=Decimal("0.9"),
            experience_months=3,
            is_part_time=True,
            part_time_ratio=Decimal("0.5")
        )
    ]


class TestPayrollCalculator:
    """Tests du calculateur de paie."""
    
    def test_calculator_initialization(self, sample_social_charges_config):
        """Test de l'initialisation du calculateur."""
        calculator = PayrollCalculator(sample_social_charges_config)
        
        assert calculator.social_charges_config == sample_social_charges_config
        assert calculator.smic_hourly == Decimal("11.65")
        assert calculator.legal_working_hours == Decimal("35")
        assert calculator.overtime_rate_25 == Decimal("1.25")
        assert calculator.overtime_rate_50 == Decimal("1.50")
        assert calculator.sunday_premium_rate == Decimal("0.30")
        assert calculator.social_security_ceiling == Decimal("3864")
    
    def test_basic_payroll_calculation_cdi(self, sample_social_charges_config, sample_employees):
        """Test de calcul de paie de base pour un CDI."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[0]  # Jean Dupont, CDI
        
        result = calculator.calculate_payroll(employee, period="2024-01")
        
        # Vérifications de base
        assert isinstance(result, PayrollResult)
        assert result.employee_id == employee.id
        assert result.employee_name == employee.name
        assert result.period == "2024-01"
        assert result.gross_salary == employee.salary_gross_monthly
        
        # Vérification des charges
        expected_employee_charges = employee.salary_gross_monthly * Decimal("0.22")
        expected_employer_charges = employee.salary_gross_monthly * Decimal("0.42")
        
        assert abs(result.social_charges_employee - expected_employee_charges) < Decimal("0.01")
        assert abs(result.social_charges_employer - expected_employer_charges) < Decimal("0.01")
        
        # Vérification des totaux
        expected_net = result.gross_salary - result.social_charges_employee
        expected_total_cost = result.gross_salary + result.social_charges_employer
        
        assert result.net_salary == expected_net
        assert result.total_cost == expected_total_cost
    
    def test_payroll_calculation_apprenti(self, sample_social_charges_config, sample_employees):
        """Test de calcul pour un apprenti (taux réduits)."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[2]  # Pierre Apprenti
        
        result = calculator.calculate_payroll(employee)
        
        # Vérification des taux réduits
        expected_employee_charges = employee.salary_gross_monthly * Decimal("0.05")
        expected_employer_charges = employee.salary_gross_monthly * Decimal("0.11")
        
        assert abs(result.social_charges_employee - expected_employee_charges) < Decimal("0.01")
        assert abs(result.social_charges_employer - expected_employer_charges) < Decimal("0.01")
    
    def test_payroll_calculation_part_time(self, sample_social_charges_config, sample_employees):
        """Test de calcul pour un temps partiel."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[3]  # Sophie Extra, mi-temps
        
        result = calculator.calculate_payroll(employee)
        
        # Le salaire effectif devrait être réduit
        expected_effective_salary = employee.salary_gross_monthly * employee.part_time_ratio
        assert result.gross_salary == expected_effective_salary
        
        # Les charges sont calculées sur le salaire effectif
        expected_employer_charges = expected_effective_salary * Decimal("0.45")  # Taux extra
        assert abs(result.social_charges_employer - expected_employer_charges) < Decimal("0.01")
    
    def test_overtime_calculation_eligible(self, sample_social_charges_config, sample_employees):
        """Test du calcul des heures supplémentaires."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[0]  # CDI, éligible aux heures sup
        
        # 160 heures (151.67 normales + 8.33 heures sup)
        hours_worked = Decimal("160.0")
        
        result = calculator.calculate_payroll(employee, hours_worked=hours_worked)
        
        # Vérification des heures supplémentaires
        normal_hours = Decimal("151.67")
        overtime_hours = hours_worked - normal_hours
        
        assert result.overtime_hours == overtime_hours
        assert result.overtime_pay > Decimal("0")
        
        # Le salaire brut devrait inclure les heures sup
        assert result.gross_salary > employee.salary_gross_monthly
    
    def test_overtime_calculation_not_eligible(self, sample_social_charges_config, sample_employees):
        """Test avec employé non éligible aux heures supplémentaires."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[3]  # Temps partiel, non éligible
        
        hours_worked = Decimal("160.0")
        
        result = calculator.calculate_payroll(employee, hours_worked=hours_worked)
        
        # Pas d'heures supplémentaires
        assert result.overtime_hours == Decimal("0")
        assert result.overtime_pay == Decimal("0")
    
    def test_sunday_premium_calculation(self, sample_social_charges_config, sample_employees):
        """Test du calcul de la prime dominicale."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[0]
        employee.sunday_work = True  # Autorisé à travailler le dimanche
        
        sunday_hours = Decimal("8.0")
        
        result = calculator.calculate_payroll(employee, sunday_hours=sunday_hours)
        
        # Vérification de la prime
        assert result.sunday_hours == sunday_hours
        assert result.sunday_premium > Decimal("0")
        
        # Calcul attendu
        hourly_rate = employee.hourly_rate
        expected_premium = sunday_hours * hourly_rate * calculator.sunday_premium_rate
        
        assert abs(result.sunday_premium - expected_premium) < Decimal("0.01")
    
    def test_sunday_premium_not_authorized(self, sample_social_charges_config, sample_employees):
        """Test sans autorisation de travail dominical."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[0]
        employee.sunday_work = False  # Non autorisé
        
        sunday_hours = Decimal("8.0")
        
        result = calculator.calculate_payroll(employee, sunday_hours=sunday_hours)
        
        # Pas de prime
        assert result.sunday_premium == Decimal("0")
    
    def test_complex_payroll_calculation(self, sample_social_charges_config, sample_employees):
        """Test de calcul complexe avec heures sup et prime dimanche."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[0]
        employee.sunday_work = True
        
        hours_worked = Decimal("165.0")  # Heures supplémentaires
        sunday_hours = Decimal("7.0")   # Heures dimanche
        
        result = calculator.calculate_payroll(employee, hours_worked, sunday_hours)
        
        # Vérifications
        assert result.overtime_hours > Decimal("0")
        assert result.overtime_pay > Decimal("0")
        assert result.sunday_hours == sunday_hours
        assert result.sunday_premium > Decimal("0")
        
        # Le salaire brut devrait inclure base + heures sup + prime dimanche
        expected_gross = (employee.salary_gross_monthly + 
                         result.overtime_pay + 
                         result.sunday_premium)
        
        assert result.gross_salary == expected_gross
    
    def test_social_security_ceiling_application(self, sample_social_charges_config):
        """Test de l'application du plafond sécurité sociale."""
        calculator = PayrollCalculator(sample_social_charges_config)
        
        # Employé avec salaire au-dessus du plafond
        high_salary_employee = Employee(
            id="high_salary",
            name="Directeur",
            position=EmployeePosition.MANAGER,
            contract=EmployeeContract.CDI,
            salary_gross_monthly=Decimal("5000.00")  # Au-dessus du plafond
        )
        
        result = calculator.calculate_payroll(high_salary_employee)
        
        # Les charges devraient être plafonnées pour certaines cotisations
        # (test simplifié - dans la réalité c'est plus complexe)
        assert result.social_charges_employer > Decimal("0")
        assert result.total_cost > high_salary_employee.salary_gross_monthly
    
    def test_team_payroll_calculation(self, sample_social_charges_config, sample_employees):
        """Test de calcul pour une équipe."""
        calculator = PayrollCalculator(sample_social_charges_config)
        
        # Heures spécifiques par employé
        hours_per_employee = {
            "emp1": Decimal("155.0"),
            "emp2": Decimal("151.67"),
            "emp3": Decimal("140.0"),
            "emp4": Decimal("75.0")  # Mi-temps
        }
        
        results = calculator.calculate_team_payroll(
            sample_employees, 
            hours_per_employee=hours_per_employee,
            period="2024-01"
        )
        
        # Vérifications
        assert len(results) == len(sample_employees)
        
        for result in results:
            assert isinstance(result, PayrollResult)
            assert result.period == "2024-01"
            assert result.total_cost > result.gross_salary
    
    def test_payroll_summary(self, sample_social_charges_config, sample_employees):
        """Test du résumé de masse salariale."""
        calculator = PayrollCalculator(sample_social_charges_config)
        
        results = calculator.calculate_team_payroll(sample_employees)
        summary = calculator.get_payroll_summary(results)
        
        # Vérifications de la structure
        assert 'total_gross_salary' in summary
        assert 'total_net_salary' in summary
        assert 'total_employer_charges' in summary
        assert 'total_cost' in summary
        assert 'average_charge_rate' in summary
        
        # Vérifications de cohérence
        manual_total_gross = sum(r.gross_salary for r in results)
        manual_total_net = sum(r.net_salary for r in results)
        manual_total_charges = sum(r.social_charges_employer for r in results)
        manual_total_cost = sum(r.total_cost for r in results)
        
        assert summary['total_gross_salary'] == manual_total_gross
        assert summary['total_net_salary'] == manual_total_net
        assert summary['total_employer_charges'] == manual_total_charges
        assert summary['total_cost'] == manual_total_cost
        
        # Taux de charges moyen
        expected_rate = (manual_total_charges / manual_total_gross * 100) if manual_total_gross > 0 else Decimal("0")
        assert abs(summary['average_charge_rate'] - expected_rate) < Decimal("0.01")
    
    def test_hourly_rate_calculation(self, sample_employees):
        """Test du calcul du taux horaire."""
        employee = sample_employees[0]
        
        # Calcul manuel
        monthly_hours = Decimal("151.67")  # 35h * 52 semaines / 12 mois
        expected_hourly_rate = employee.salary_gross_monthly / monthly_hours
        
        assert abs(employee.hourly_rate - expected_hourly_rate) < Decimal("0.01")
    
    def test_part_time_hourly_rate(self, sample_employees):
        """Test du taux horaire pour temps partiel."""
        employee = sample_employees[3]  # Mi-temps
        
        # Le taux horaire devrait être basé sur le salaire effectif
        monthly_hours = Decimal("151.67")
        effective_salary = employee.salary_gross_monthly * employee.part_time_ratio
        expected_hourly_rate = effective_salary / monthly_hours
        
        assert abs(employee.hourly_rate - expected_hourly_rate) < Decimal("0.01")
    
    def test_overtime_rates_application(self, sample_social_charges_config, sample_employees):
        """Test de l'application des taux d'heures supplémentaires."""
        calculator = PayrollCalculator(sample_social_charges_config)
        employee = sample_employees[0]
        
        # 12 heures supplémentaires (8 à 25%, 4 à 50%)
        hours_worked = Decimal("163.67")  # 151.67 + 12
        
        result = calculator.calculate_payroll(employee, hours_worked=hours_worked)
        
        # Calcul manuel
        hourly_rate = employee.hourly_rate
        hours_25 = Decimal("8")
        hours_50 = Decimal("4")
        
        expected_overtime_pay = (
            hours_25 * hourly_rate * (calculator.overtime_rate_25 - 1) +
            hours_50 * hourly_rate * (calculator.overtime_rate_50 - 1)
        )
        
        assert abs(result.overtime_pay - expected_overtime_pay) < Decimal("0.01")
    
    def test_default_charge_rates(self, sample_employees):
        """Test des taux de charges par défaut."""
        # Configuration vide
        empty_config = {}
        calculator = PayrollCalculator(empty_config)
        
        employee = sample_employees[0]  # CDI
        result = calculator.calculate_payroll(employee)
        
        # Devrait utiliser les taux par défaut
        expected_employer_charges = employee.salary_gross_monthly * Decimal("0.42")
        assert abs(result.social_charges_employer - expected_employer_charges) < Decimal("0.01")


class TestPayrollResult:
    """Tests de la classe PayrollResult."""
    
    def test_payroll_result_creation(self):
        """Test de création d'un résultat de paie."""
        result = PayrollResult(
            employee_id="test",
            employee_name="Test Employee",
            period="2024-01",
            gross_salary=Decimal("2000.00"),
            social_charges_employee=Decimal("440.00"),
            social_charges_employer=Decimal("840.00")
        )
        
        # Vérification des calculs automatiques
        assert result.net_salary == Decimal("1560.00")  # 2000 - 440
        assert result.total_cost == Decimal("2840.00")   # 2000 + 840
    
    def test_payroll_result_with_overtime(self):
        """Test avec heures supplémentaires."""
        result = PayrollResult(
            employee_id="test",
            employee_name="Test Employee",
            period="2024-01",
            gross_salary=Decimal("2200.00"),
            social_charges_employee=Decimal("484.00"),
            social_charges_employer=Decimal("924.00"),
            overtime_hours=Decimal("8.0"),
            overtime_pay=Decimal("200.00")
        )
        
        assert result.overtime_hours == Decimal("8.0")
        assert result.overtime_pay == Decimal("200.00")
        assert result.net_salary == Decimal("1716.00")
        assert result.total_cost == Decimal("3124.00")
    
    def test_payroll_result_with_sunday_premium(self):
        """Test avec prime dominicale."""
        result = PayrollResult(
            employee_id="test",
            employee_name="Test Employee",
            period="2024-01",
            gross_salary=Decimal("2100.00"),
            social_charges_employee=Decimal("462.00"),
            social_charges_employer=Decimal("882.00"),
            sunday_hours=Decimal("6.0"),
            sunday_premium=Decimal("100.00")
        )
        
        assert result.sunday_hours == Decimal("6.0")
        assert result.sunday_premium == Decimal("100.00")
        assert result.net_salary == Decimal("1638.00")
        assert result.total_cost == Decimal("2982.00")
