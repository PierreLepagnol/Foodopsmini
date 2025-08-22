"""Gestion de l'hygiène et des inspections pour FoodOps Pro."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional
import random


@dataclass
class HygieneTask:
    """Tâche d'hygiène planifiée.

    Attributes:
        name: Description de la tâche.
        cost: Coût de réalisation.
        frequency: Fréquence en nombre de tours entre deux réalisations.
        last_done: Tour de la dernière réalisation.
    """

    name: str
    cost: Decimal
    frequency: int
    last_done: int = 0


@dataclass
class InspectionResult:
    """Résultat d'une inspection sanitaire."""

    turn: int
    score: int
    fine: Decimal = Decimal("0")


class HygieneManager:
    """Planifie les tâches d'hygiène et gère les inspections."""

    def __init__(self, inspection_probability: float = 0.1) -> None:
        self.tasks: List[HygieneTask] = []
        self.inspections: List[InspectionResult] = []
        self.inspection_probability = inspection_probability
        self.attendance_modifier: Decimal = Decimal("1.0")
        self._rng = random.Random()

    # Planifier des tâches
    def plan_task(self, task: HygieneTask) -> None:
        self.tasks.append(task)

    # Exécuter les tâches dues pour un tour et retourner le coût total
    def run_tasks(self, current_turn: int) -> Decimal:
        total_cost = Decimal("0")
        for task in self.tasks:
            if current_turn - task.last_done >= task.frequency:
                total_cost += task.cost
                task.last_done = current_turn
        return total_cost

    # Déclenchement potentiel d'une inspection
    def maybe_inspect(self, current_turn: int) -> Optional[InspectionResult]:
        if self._rng.random() > self.inspection_probability:
            self.attendance_modifier = Decimal("1.0")
            return None

        overdue = sum(1 for t in self.tasks if current_turn - t.last_done > t.frequency)
        score = max(0, 100 - overdue * 20)
        fine = Decimal("0")
        modifier = Decimal("1.0")
        if score < 70:
            modifier -= Decimal("0.10")
            fine = Decimal("500")
        if score < 50:
            modifier -= Decimal("0.20")
            fine = Decimal("1000")
        self.attendance_modifier = modifier
        result = InspectionResult(turn=current_turn, score=score, fine=fine)
        self.inspections.append(result)
        return result

    def get_attendance_modifier(self) -> Decimal:
        return self.attendance_modifier

    def get_inspection_summary(self) -> List[InspectionResult]:
        return list(self.inspections)
