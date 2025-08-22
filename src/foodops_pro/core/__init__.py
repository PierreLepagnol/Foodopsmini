"""
Logique métier centrale pour FoodOps Pro.

Ce module contient les algorithmes et calculs principaux :
- Allocation de marché et concurrence
- Calcul des coûts de recettes
- Comptabilité française (PCG)
- Gestion de la paie française
"""

try:
    from .market import MarketEngine, AllocationResult
except SyntaxError:
    MarketEngine = None  # type: ignore
    AllocationResult = None  # type: ignore

from .costing import RecipeCostCalculator, CostBreakdown
from .ledger import Ledger, AccountingEntry, VATCalculator
from .payroll_fr import PayrollCalculator, PayrollResult

__all__ = [
    name
    for name in [
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
    if globals().get(name) is not None
]
