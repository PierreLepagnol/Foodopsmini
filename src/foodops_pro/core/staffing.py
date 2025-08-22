from __future__ import annotations

"""Services de planification du personnel."""

from decimal import Decimal


class StaffPlanner:
    """Planification simple du personnel."""

    _level_cost_factor = {
        0: Decimal("0"),
        1: Decimal("0.7"),
        2: Decimal("1.0"),
        3: Decimal("1.3"),
    }
    _satisfaction_adjustments = {
        0: Decimal("-1.0"),
        1: Decimal("-0.5"),
        2: Decimal("0"),
        3: Decimal("0.5"),
    }

    def calculate_daily_cost(self, restaurant, staffing_level: int) -> Decimal:
        """Calcule le coût salarial quotidien selon le niveau de staffing."""
        base_daily = restaurant.monthly_staff_cost / Decimal("30")
        factor = self._level_cost_factor.get(staffing_level, Decimal("1.0"))
        return (base_daily * factor).quantize(Decimal("0.01"))

    def apply_plan(self, restaurant, staffing_level: int) -> Decimal:
        """Applique un plan de staffing et déduit le coût."""
        cost = self.calculate_daily_cost(restaurant, staffing_level)
        restaurant.staffing_level = staffing_level
        if hasattr(restaurant, "update_cash"):
            restaurant.update_cash(-cost, "Coût personnel")
        if hasattr(restaurant, "last_staff_cost"):
            restaurant.last_staff_cost = cost
        return cost

    @classmethod
    def adjust_satisfaction(cls, base: Decimal, staffing_level: int) -> Decimal:
        """Ajuste un score de satisfaction selon le staffing."""
        adjust = cls._satisfaction_adjustments.get(staffing_level, Decimal("0"))
        value = base + adjust
        return max(Decimal("1.0"), min(Decimal("5.0"), value))
