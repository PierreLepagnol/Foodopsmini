from decimal import Decimal

from foodops_pro.domain.hygiene import HygieneManager, HygieneTask
from foodops_pro.io.export import KPICalculator


def test_hygiene_task_cost_frequency():
    manager = HygieneManager()
    manager.plan_task(HygieneTask("Nettoyage", Decimal("50"), 1))
    assert manager.run_tasks(1) == Decimal("50")
    assert manager.run_tasks(2) == Decimal("50")


def test_inspection_penalty():
    manager = HygieneManager(inspection_probability=1.0)
    manager.plan_task(HygieneTask("Vérification", Decimal("10"), 1))
    # Ne pas exécuter la tâche pour créer un retard
    result = manager.maybe_inspect(2)
    assert result is not None
    assert result.score < 100
    assert result.fine >= Decimal("500")
    assert manager.get_attendance_modifier() < Decimal("1.0")


def test_kpi_includes_hygiene_metrics():
    restaurant_data = {
        "id": "r1",
        "hygiene": {
            "inspections": [
                {"turn": 1, "score": 80, "fine": 0},
                {"turn": 2, "score": 60, "fine": 100},
            ]
        },
    }
    kpis = KPICalculator.calculate_restaurant_kpis(restaurant_data, [])
    assert kpis["avg_hygiene_score"] == 70
    assert kpis["total_hygiene_fines"] == Decimal("100")
