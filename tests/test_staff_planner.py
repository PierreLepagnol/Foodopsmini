from decimal import Decimal
from foodops_pro.core.staffing import StaffPlanner
from foodops_pro.domain.restaurant import Restaurant, RestaurantType
from foodops_pro.domain.employee import Employee, EmployeePosition, EmployeeContract


def make_restaurant():
    r = Restaurant(
        id="r1",
        name="R",
        type=RestaurantType.FAST,
        capacity_base=50,
        speed_service=Decimal("1.0"),
    )
    emp = Employee(
        id="e1",
        name="Alice",
        position=EmployeePosition.CUISINE,
        contract=EmployeeContract.CDI,
        salary_gross_monthly=Decimal("2000"),
    )
    r.employees.append(emp)
    return r


def test_staff_cost_and_satisfaction_adjustment():
    resto = make_restaurant()
    planner = StaffPlanner()
    cost = planner.apply_plan(resto, 3)
    assert resto.staffing_level == 3
    assert cost > 0 and resto.last_staff_cost == cost
    sat = planner.adjust_satisfaction(Decimal("4.0"), 1)
    assert sat < Decimal("4.0")
