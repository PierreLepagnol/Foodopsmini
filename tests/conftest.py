"""
Configuration pytest pour FoodOps Pro.
"""

import pytest
from pathlib import Path
from decimal import Decimal

from src.foodops_pro.io.data_loader import DataLoader
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType
from src.foodops_pro.domain.employee import Employee, EmployeePosition, EmployeeContract


@pytest.fixture(scope="session")
def test_data_path():
    """Chemin vers les données de test."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def data_loader():
    """Chargeur de données pour les tests."""
    return DataLoader()


@pytest.fixture
def sample_restaurant():
    """Restaurant de test standard."""
    restaurant = Restaurant(
        id="test_restaurant",
        name="Restaurant Test",
        type=RestaurantType.CLASSIC,
        capacity_base=60,
        speed_service=Decimal("1.0"),
        cash=Decimal("10000"),
        rent_monthly=Decimal("3000"),
        fixed_costs_monthly=Decimal("1500")
    )
    
    # Ajout d'employés de base
    chef = Employee(
        id="chef_test",
        name="Chef Test",
        position=EmployeePosition.CUISINE,
        contract=EmployeeContract.CDI,
        salary_gross_monthly=Decimal("2500")
    )
    
    serveur = Employee(
        id="serveur_test",
        name="Serveur Test",
        position=EmployeePosition.SALLE,
        contract=EmployeeContract.CDI,
        salary_gross_monthly=Decimal("2000")
    )
    
    restaurant.add_employee(chef)
    restaurant.add_employee(serveur)
    
    # Menu de base
    restaurant.set_recipe_price("burger_classic", Decimal("12.50"))
    restaurant.set_recipe_price("pasta_bolognese", Decimal("15.00"))
    restaurant.activate_recipe("burger_classic")
    restaurant.activate_recipe("pasta_bolognese")
    
    return restaurant


@pytest.fixture
def decimal_precision():
    """Précision pour les comparaisons de Decimal."""
    return Decimal("0.01")


# Configuration des markers pytest
def pytest_configure(config):
    """Configuration des markers personnalisés."""
    config.addinivalue_line(
        "markers", "integration: marque les tests d'intégration"
    )
    config.addinivalue_line(
        "markers", "slow: marque les tests lents"
    )
    config.addinivalue_line(
        "markers", "unit: marque les tests unitaires"
    )
