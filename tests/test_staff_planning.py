from decimal import Decimal

from src.foodops_pro.core.staff_planner import StaffPlanner, Shift
from src.foodops_pro.domain.employee import Employee, EmployeePosition, EmployeeContract


def make_employee(id_: str, salary: str) -> Employee:
    return Employee(
        id=id_,
        name=id_,
        position=EmployeePosition.SALLE,
        contract=EmployeeContract.CDI,
        salary_gross_monthly=Decimal(salary),
    )


def test_staff_planner_cost_and_satisfaction():
    planner = StaffPlanner()
    emp1 = make_employee("e1", "2000")
    emp2 = make_employee("e2", "2000")
    shifts = [Shift(emp1, Decimal("8")), Shift(emp2, Decimal("4"))]

    result = planner.evaluate(Decimal("16"), shifts)
    # 12h scheduled over 16h requirement -> 0.75 satisfaction
    assert result.satisfaction == Decimal("0.75")
    hourly = emp1.hourly_rate  # same for both
    expected_cost = hourly * Decimal("12")
    assert result.total_cost == expected_cost
