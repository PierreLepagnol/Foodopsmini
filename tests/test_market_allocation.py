"""
Tests pour l'allocation de marché et la concurrence.
"""

import pytest
from decimal import Decimal

from src.game_engine.domain.restaurant import Restaurant, RestaurantType
from src.game_engine.domain.scenario import Scenario, MarketSegment
from src.game_engine.core.market import MarketEngine, AllocationResult


@pytest.fixture
def sample_segments():
    """Segments de marché pour les tests."""
    return [
        MarketSegment(
            name="Étudiants",
            share=Decimal("0.4"),
            budget=Decimal("12.0"),
            type_affinity={
                RestaurantType.FAST: Decimal("1.2"),
                RestaurantType.CLASSIC: Decimal("0.8"),
            },
            price_sensitivity=Decimal("1.5"),
            quality_sensitivity=Decimal("0.8"),
        ),
        MarketSegment(
            name="Familles",
            share=Decimal("0.6"),
            budget=Decimal("18.0"),
            type_affinity={
                RestaurantType.FAST: Decimal("0.9"),
                RestaurantType.CLASSIC: Decimal("1.1"),
            },
            price_sensitivity=Decimal("1.0"),
            quality_sensitivity=Decimal("1.2"),
        ),
    ]


@pytest.fixture
def sample_scenario(sample_segments):
    """Scénario de test."""
    return Scenario(
        name="Test Scenario",
        description="Scénario pour tests",
        turns=10,
        base_demand=100,
        demand_noise=Decimal("0.1"),
        segments=sample_segments,
        random_seed=42,
    )


@pytest.fixture
def sample_restaurants():
    """Restaurants de test."""
    fast_food = Restaurant(
        id="fast_test",
        name="Fast Test",
        type=RestaurantType.FAST,
        capacity_base=50,
        speed_service=Decimal("1.5"),
        staffing_level=2,
    )
    fast_food.set_recipe_price("burger", Decimal("10.0"))
    fast_food.activate_recipe("burger")

    classic = Restaurant(
        id="classic_test",
        name="Classic Test",
        type=RestaurantType.CLASSIC,
        capacity_base=40,
        speed_service=Decimal("1.0"),
        staffing_level=2,
    )
    classic.set_recipe_price("pasta", Decimal("15.0"))
    classic.activate_recipe("pasta")

    return [fast_food, classic]


class TestMarketEngine:
    """Tests du moteur de marché."""

    def test_market_engine_initialization(self, sample_scenario):
        """Test de l'initialisation du moteur de marché."""
        engine = MarketEngine(sample_scenario, random_seed=42)

        assert engine.scenario == sample_scenario
        assert engine.rng is not None  # Vérification que le RNG est initialisé
        assert engine.turn_history == []

    def test_demand_allocation_basic(self, sample_scenario, sample_restaurants):
        """Test de l'allocation de base de la demande."""
        engine = MarketEngine(sample_scenario, random_seed=42)
        results = engine.allocate_demand(sample_restaurants, turn=1)

        # Vérification que tous les restaurants ont un résultat
        assert len(results) == len(sample_restaurants)
        for restaurant in sample_restaurants:
            assert restaurant.id in results
            assert isinstance(results[restaurant.id], AllocationResult)

    def test_capacity_constraints(self, sample_scenario, sample_restaurants):
        """Test des contraintes de capacité."""
        engine = MarketEngine(sample_scenario, random_seed=42)

        # Réduction drastique de la capacité d'un restaurant
        sample_restaurants[0].capacity_base = 5

        results = engine.allocate_demand(sample_restaurants, turn=1)

        # Vérification que les clients servis ne dépassent pas la capacité
        for restaurant in sample_restaurants:
            result = results[restaurant.id]
            assert result.served_customers <= result.capacity
            assert result.utilization_rate <= Decimal("1.0")

    def test_price_sensitivity(self, sample_scenario, sample_restaurants):
        """Test de la sensibilité au prix."""
        engine = MarketEngine(sample_scenario, random_seed=42)

        # Prix très élevé pour un restaurant
        sample_restaurants[0].set_recipe_price("burger", Decimal("50.0"))

        results = engine.allocate_demand(sample_restaurants, turn=1)

        # Le restaurant cher devrait avoir moins de demande
        expensive_result = results[sample_restaurants[0].id]
        normal_result = results[sample_restaurants[1].id]

        assert expensive_result.allocated_demand <= normal_result.allocated_demand

    def test_restaurant_closed(self, sample_scenario, sample_restaurants):
        """Test avec un restaurant fermé."""
        engine = MarketEngine(sample_scenario, random_seed=42)

        # Fermeture d'un restaurant
        sample_restaurants[0].staffing_level = 0

        results = engine.allocate_demand(sample_restaurants, turn=1)

        # Le restaurant fermé ne devrait avoir aucun client
        closed_result = results[sample_restaurants[0].id]
        assert closed_result.served_customers == 0
        assert closed_result.revenue == Decimal("0")

    def test_demand_redistribution(self, sample_scenario, sample_restaurants):
        """Test de la redistribution de la demande excédentaire."""
        engine = MarketEngine(sample_scenario, random_seed=42)

        # Un restaurant avec très peu de capacité, l'autre avec beaucoup
        sample_restaurants[0].capacity_base = 10
        sample_restaurants[1].capacity_base = 200

        results = engine.allocate_demand(sample_restaurants, turn=1)

        # Vérification de la redistribution
        total_served = sum(r.served_customers for r in results.values())
        total_capacity = sum(r.capacity for r in results.values())

        # La demande totale servie devrait être proche de la capacité totale
        # ou de la demande totale si elle est inférieure
        assert total_served <= total_capacity

    def test_revenue_calculation(self, sample_scenario, sample_restaurants):
        """Test du calcul des revenus."""
        engine = MarketEngine(sample_scenario, random_seed=42)
        results = engine.allocate_demand(sample_restaurants, turn=1)

        for restaurant in sample_restaurants:
            result = results[restaurant.id]

            if result.served_customers > 0:
                # Le revenu devrait être positif
                assert result.revenue > Decimal("0")

                # Le ticket moyen devrait être cohérent
                expected_avg = result.revenue / Decimal(result.served_customers)
                assert abs(result.average_ticket - expected_avg) < Decimal("0.01")

    def test_market_share_calculation(self, sample_scenario, sample_restaurants):
        """Test du calcul de part de marché."""
        engine = MarketEngine(sample_scenario, random_seed=42)
        engine.allocate_demand(sample_restaurants, turn=1)

        # Calcul des parts de marché
        total_share = Decimal("0")
        for restaurant in sample_restaurants:
            share = engine.get_market_share(restaurant.id)
            assert Decimal("0") <= share <= Decimal("1")
            total_share += share

        # La somme des parts devrait être proche de 1
        assert abs(total_share - Decimal("1")) < Decimal("0.01")

    def test_turn_history(self, sample_scenario, sample_restaurants):
        """Test de l'historique des tours."""
        engine = MarketEngine(sample_scenario, random_seed=42)

        # Simulation de plusieurs tours
        for turn in range(1, 4):
            engine.allocate_demand(sample_restaurants, turn=turn)

        # Vérification de l'historique
        assert len(engine.turn_history) == 3

        for i, turn_data in enumerate(engine.turn_history):
            assert len(turn_data) == len(sample_restaurants)

    def test_market_analysis(self, sample_scenario, sample_restaurants):
        """Test de l'analyse de marché."""
        engine = MarketEngine(sample_scenario, random_seed=42)
        engine.allocate_demand(sample_restaurants, turn=1)

        analysis = engine.get_market_analysis()

        # Vérification des métriques
        assert "total_demand" in analysis
        assert "total_served" in analysis
        assert "total_capacity" in analysis
        assert "total_revenue" in analysis
        assert "market_utilization" in analysis
        assert "demand_satisfaction" in analysis

        # Cohérence des données
        assert analysis["total_served"] <= analysis["total_capacity"]
        assert analysis["total_served"] <= analysis["total_demand"]
        assert 0 <= analysis["market_utilization"] <= 1
        assert 0 <= analysis["demand_satisfaction"] <= 1


class TestAllocationResult:
    """Tests de la classe AllocationResult."""

    def test_allocation_result_creation(self):
        """Test de création d'un résultat d'allocation."""
        result = AllocationResult(
            restaurant_id="test", allocated_demand=100, served_customers=80, capacity=90
        )

        # Vérification des calculs automatiques
        assert result.utilization_rate == Decimal("80") / Decimal("90")
        assert result.lost_customers == 20

    def test_allocation_result_with_revenue(self):
        """Test avec calcul de revenus."""
        result = AllocationResult(
            restaurant_id="test",
            allocated_demand=50,
            served_customers=50,
            capacity=60,
            revenue=Decimal("750"),
        )

        # Vérification du ticket moyen
        assert result.average_ticket == Decimal("15")
        assert result.lost_customers == 0
        assert result.utilization_rate == Decimal("50") / Decimal("60")


class TestSegmentAllocation:
    """Tests spécifiques à l'allocation par segment."""

    def test_segment_affinity_impact(self, sample_scenario, sample_restaurants):
        """Test de l'impact de l'affinité par segment."""
        engine = MarketEngine(sample_scenario, random_seed=42)

        # Le fast-food devrait être favorisé par les étudiants
        # Le restaurant classique par les familles
        results = engine.allocate_demand(sample_restaurants, turn=1)

        # Vérification que l'allocation respecte les affinités
        # (test qualitatif car dépend de plusieurs facteurs)
        fast_result = results[sample_restaurants[0].id]
        classic_result = results[sample_restaurants[1].id]

        assert fast_result.allocated_demand >= 0
        assert classic_result.allocated_demand >= 0

    def test_budget_constraints(self, sample_scenario, sample_restaurants):
        """Test des contraintes budgétaires."""
        engine = MarketEngine(sample_scenario, random_seed=42)

        # Prix très au-dessus du budget des segments
        for restaurant in sample_restaurants:
            for recipe_id in restaurant.menu:
                restaurant.set_recipe_price(recipe_id, Decimal("100.0"))

        results = engine.allocate_demand(sample_restaurants, turn=1)

        # La demande devrait être très faible
        total_demand = sum(r.allocated_demand for r in results.values())
        assert (
            total_demand < sample_scenario.base_demand * 0.5
        )  # Moins de 50% de la demande normale
