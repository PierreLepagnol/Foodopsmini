"""Simple staff scheduling planner for FoodOps Pro."""

from dataclasses import dataclass
from decimal import Decimal
from typing import List

from ..domain.employee import Employee


@dataclass
class Shift:
    """Represents a work shift for an employee."""

    employee: Employee
    hours: Decimal


@dataclass
class StaffScheduleResult:
    """Outcome of schedule evaluation."""

    total_cost: Decimal
    satisfaction: Decimal


class StaffPlanner:
    """Evaluates staff schedules for cost and satisfaction."""

    def evaluate(self, required_hours: Decimal, shifts: List[Shift]) -> StaffScheduleResult:
        """Compute total cost and satisfaction for a schedule.

        Args:
            required_hours: Hours needed to fully satisfy demand.
            shifts: List of planned shifts.
        """
        scheduled = sum(shift.hours for shift in shifts)
        if required_hours > 0:
            satisfaction = min(Decimal("1"), Decimal(scheduled) / required_hours)
        else:
            satisfaction = Decimal("1")
        total_cost = sum(shift.employee.hourly_rate * shift.hours for shift in shifts)
        return StaffScheduleResult(total_cost=total_cost, satisfaction=satisfaction)
