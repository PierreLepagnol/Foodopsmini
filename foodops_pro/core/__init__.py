"""
Logique métier centrale pour FoodOps Pro.

Ce module contient les algorithmes et calculs principaux :
- Allocation de marché et concurrence
- Calcul des coûts de recettes
- Comptabilité française (PCG)
- Gestion de la paie française
"""

from foodops_pro.market import MarketEngine, AllocationResult
from foodops_pro.costing import RecipeCostCalculator, CostBreakdown
from foodops_pro.ledger import Ledger, AccountingEntry, VATCalculator
from foodops_pro.payroll_fr import PayrollCalculator, PayrollResult

__all__ = [
    "MarketEngine",
    "AllocationResult",
    "RecipeCostCalculator",
    "CostBreakdown",
    "Ledger",
    "AccountingEntry",
    "VATCalculator",
    "PayrollCalculator",
    "PayrollResult",
]
