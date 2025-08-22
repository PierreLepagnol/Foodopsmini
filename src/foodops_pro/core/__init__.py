"""
Logique métier centrale pour FoodOps Pro.

Ce module contient les algorithmes et calculs principaux :
- Allocation de marché et concurrence
- Calcul des coûts de recettes
- Comptabilité française (PCG)
- Gestion de la paie française
"""

from .market import MarketEngine, AllocationResult
from .costing import RecipeCostCalculator, CostBreakdown
from .ledger import Ledger, AccountingEntry, VATCalculator
from .payroll import PayrollCalculator, PayrollResult

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
