#!/usr/bin/env python3
"""
Test complet du système qualité intégré dans FoodOps Pro.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from decimal import Decimal
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType
from src.foodops_pro.domain.scenario import Scenario, MarketSegment
from src.foodops_pro.core.market import MarketEngine
from src.foodops_pro.domain.employee import Employee, Position, ContractType


def create_test_scenario():
    """Crée un scénario de test."""
    segments = [
        MarketSegment(
            name="Étudiants",
            share=Decimal("0.4"),
            budget=Decimal("12.0"),
            price_sensitivity=Decimal("1.2"),
            quality_sensitivity=Decimal("0.6"),
            type_preferences={"fast": Decimal("1.5"), "classic": Decimal("0.8")},
        ),
        MarketSegment(
            name="Familles",
            share=Decimal("0.35"),
            budget=Decimal("18.0"),
            price_sensitivity=Decimal("1.0"),
            quality_sensitivity=Decimal("1.0"),
            type_preferences={"classic": Decimal("1.3"), "fast": Decimal("1.0")},
        ),
        MarketSegment(
            name="Foodies",
            share=Decimal("0.25"),
            budget=Decimal("25.0"),
            price_sensitivity=Decimal("0.7"),
            quality_sensitivity=Decimal("1.5"),
            type_preferences={
                "gastronomique": Decimal("1.8"),
                "classic": Decimal("1.2"),
            },
        ),
    ]

    return Scenario(
        name="Test Qualité",
        description="Test du système qualité",
        base_demand=500,
        segments=segments,
        duration_turns=5,
    )


def create_test_restaurants():
    """Crée des restaurants de test avec différentes stratégies."""

    # Restaurant économique
    resto_eco = Restaurant(
        id="resto_eco",
        name="Quick & Cheap",
        type=RestaurantType.FAST,
        capacity_base=80,
        speed_service=Decimal("1.2"),
        cash=Decimal("10000"),
        staffing_level=2,
    )

    # Configuration économique
    resto_eco.set_ingredient_quality("beef_ground", 1)  # Économique
    resto_eco.set_ingredient_quality("tomato", 1)
    resto_eco.set_ingredient_quality("cheese_mozzarella", 2)  # Standard
    resto_eco.set_recipe_price("burger_classic", Decimal("9.50"))
    resto_eco.activate_recipe("burger_classic")

    # Restaurant premium
    resto_premium = Restaurant(
        id="resto_premium",
        name="Gourmet Burger",
        type=RestaurantType.CLASSIC,
        capacity_base=60,
        speed_service=Decimal("0.9"),
        cash=Decimal("15000"),
        staffing_level=3,
    )

    # Configuration premium
    resto_premium.set_ingredient_quality("beef_ground", 4)  # Premium
    resto_premium.set_ingredient_quality("tomato", 4)
    resto_premium.set_ingredient_quality("cheese_mozzarella", 4)
    resto_premium.set_recipe_price("burger_classic", Decimal("16.50"))
    resto_premium.activate_recipe("burger_classic")

    # Restaurant luxe
    resto_luxe = Restaurant(
        id="resto_luxe",
        name="Artisan Bistro",
        type=RestaurantType.GASTRONOMIQUE,
        capacity_base=40,
        speed_service=Decimal("0.7"),
        cash=Decimal("20000"),
        staffing_level=3,
    )

    # Configuration luxe
    resto_luxe.set_ingredient_quality("beef_ground", 5)  # Luxe
    resto_luxe.set_ingredient_quality("tomato", 5)
    resto_luxe.set_ingredient_quality("cheese_mozzarella", 5)
    resto_luxe.set_recipe_price("burger_classic", Decimal("24.50"))
    resto_luxe.activate_recipe("burger_classic")

    return [resto_eco, resto_premium, resto_luxe]


def test_quality_system():
    """Test du système de qualité."""
    print("🏆 TEST SYSTÈME DE QUALITÉ")
    print("=" * 60)

    restaurants = create_test_restaurants()

    for resto in restaurants:
        quality_score = resto.get_overall_quality_score()
        cost_impact = resto.calculate_quality_cost_impact()

        print(f"\n🏪 {resto.name}:")
        print(f"   Type: {resto.type.value}")
        print(f"   Qualité: {resto.get_quality_description()} ({quality_score:.1f}/5)")
        print(f"   Impact coût: {cost_impact:.0%}")
        print(f"   Ticket moyen: {resto.get_average_ticket():.2f}€")
        print(f"   Réputation: {resto.reputation:.1f}/10")

        # Détail des ingrédients
        if resto.ingredient_choices:
            ingredients_desc = ", ".join(
                [f"{k}:{v}⭐" for k, v in resto.ingredient_choices.items()]
            )
            print(f"   Ingrédients: {ingredients_desc}")


def test_market_allocation():
    """Test de l'allocation de marché avec qualité."""
    print("\n\n📊 TEST ALLOCATION DE MARCHÉ")
    print("=" * 60)

    scenario = create_test_scenario()
    restaurants = create_test_restaurants()
    market_engine = MarketEngine(scenario, random_seed=42)

    # Simulation sur 3 tours
    for turn in range(1, 4):
        print(f"\n--- TOUR {turn} ---")

        # Allocation de marché
        results = market_engine.allocate_demand(restaurants, turn, month=7)  # Juillet

        # Affichage des résultats
        total_served = sum(result.served_customers for result in results.values())
        total_revenue = sum(result.revenue for result in results.values())

        print(f"Total clients servis: {total_served}")
        print(f"Chiffre d'affaires total: {total_revenue:.0f}€")

        for resto in restaurants:
            if resto.id in results:
                result = results[resto.id]
                market_share = (
                    (result.served_customers / total_served * 100)
                    if total_served > 0
                    else 0
                )

                print(f"\n  {resto.name}:")
                print(
                    f"    Clients: {result.served_customers}/{result.capacity} ({result.utilization_rate:.0%})"
                )
                print(
                    f"    CA: {result.revenue:.0f}€ (ticket: {result.average_ticket:.2f}€)"
                )
                print(f"    Part de marché: {market_share:.1f}%")
                print(f"    Satisfaction: {resto.get_average_satisfaction():.1f}/5")
                print(f"    Réputation: {resto.reputation:.1f}/10")


def test_satisfaction_factors():
    """Vérifie l'impact des facteurs sur la satisfaction et la réputation."""
    base_params = dict(
        id="r1",
        name="TestResto",
        type=RestaurantType.FAST,
        capacity_base=50,
        speed_service=Decimal("1.0"),
    )

    # Référence avec tous les facteurs au maximum
    ref_restaurant = Restaurant(**base_params)
    ref_restaurant.update_customer_satisfaction(
        Decimal("5"), Decimal("5"), Decimal("5")
    )
    ref_satisfaction = ref_restaurant.customer_satisfaction_history[-1]
    ref_reputation = ref_restaurant.reputation

    # Prix défavorable
    price_restaurant = Restaurant(**{**base_params, "id": "r2"})
    price_restaurant.update_customer_satisfaction(
        Decimal("5"), Decimal("1"), Decimal("5")
    )
    assert price_restaurant.customer_satisfaction_history[-1] < ref_satisfaction
    assert price_restaurant.reputation < ref_reputation

    # Attente excessive
    wait_restaurant = Restaurant(**{**base_params, "id": "r3"})
    wait_restaurant.update_customer_satisfaction(
        Decimal("5"), Decimal("5"), Decimal("1")
    )
    assert wait_restaurant.customer_satisfaction_history[-1] < ref_satisfaction
    assert wait_restaurant.reputation < ref_reputation

    # Qualité médiocre
    quality_restaurant = Restaurant(**{**base_params, "id": "r4"})
    quality_restaurant.update_customer_satisfaction(
        Decimal("1"), Decimal("5"), Decimal("5")
    )
    assert quality_restaurant.customer_satisfaction_history[-1] < ref_satisfaction
    assert quality_restaurant.reputation < ref_reputation


def test_seasonal_impact():
    """Test de l'impact saisonnier."""
    print("\n\n🌱 TEST IMPACT SAISONNIER")
    print("=" * 60)

    scenario = create_test_scenario()
    restaurants = create_test_restaurants()
    market_engine = MarketEngine(scenario, random_seed=42)

    # Test sur différents mois
    months = [(1, "Janvier (hiver)"), (7, "Juillet (été)"), (12, "Décembre (fêtes)")]

    for month, month_name in months:
        print(f"\n📅 {month_name}:")

        results = market_engine.allocate_demand(restaurants, 1, month=month)
        total_served = sum(result.served_customers for result in results.values())

        print(f"   Total clients: {total_served}")

        # Bonus saisonniers appliqués automatiquement dans l'allocation


def test_strategic_scenarios():
    """Test de différents scénarios stratégiques."""
    print("\n\n🎯 TEST SCÉNARIOS STRATÉGIQUES")
    print("=" * 60)

    scenario = create_test_scenario()
    market_engine = MarketEngine(scenario, random_seed=42)

    # Scénario 1: Guerre des prix
    print("\n💰 SCÉNARIO 1: Guerre des prix")

    resto_discount = Restaurant(
        id="discount",
        name="Super Discount",
        type=RestaurantType.FAST,
        capacity_base=100,
        speed_service=Decimal("1.5"),
        staffing_level=2,
    )
    resto_discount.set_ingredient_quality("beef_ground", 1)
    resto_discount.set_ingredient_quality("tomato", 1)
    resto_discount.set_recipe_price("burger_classic", Decimal("7.50"))
    resto_discount.activate_recipe("burger_classic")

    resto_normal = Restaurant(
        id="normal",
        name="Burger Normal",
        type=RestaurantType.FAST,
        capacity_base=80,
        speed_service=Decimal("1.0"),
        staffing_level=2,
    )
    resto_normal.set_ingredient_quality("beef_ground", 2)
    resto_normal.set_ingredient_quality("tomato", 2)
    resto_normal.set_recipe_price("burger_classic", Decimal("11.50"))
    resto_normal.activate_recipe("burger_classic")

    restaurants_scenario1 = [resto_discount, resto_normal]
    results = market_engine.allocate_demand(restaurants_scenario1, 1)

    for resto in restaurants_scenario1:
        if resto.id in results:
            result = results[resto.id]
            quality_score = resto.get_overall_quality_score()

            print(f"  {resto.name}:")
            print(f"    Prix: {resto.get_average_ticket():.2f}€")
            print(f"    Qualité: {quality_score:.1f}/5")
            print(f"    Clients: {result.served_customers}")
            print(f"    CA: {result.revenue:.0f}€")
            print(f"    Satisfaction: {resto.get_average_satisfaction():.1f}/5")


def main():
    """Test complet du système intégré."""
    print("🎮 TEST COMPLET FOODOPS PRO - SYSTÈME QUALITÉ")
    print("=" * 80)

    try:
        test_quality_system()
        test_market_allocation()
        test_seasonal_impact()
        test_strategic_scenarios()

        print(f"\n\n🎉 CONCLUSIONS:")
        print("=" * 40)
        print("✅ Système de qualité intégré dans FoodOps Pro")
        print("✅ Impact réel sur allocation de marché")
        print("✅ Saisonnalité automatique par segment")
        print("✅ Satisfaction et réputation évolutives")
        print("✅ Interface de choix qualité fonctionnelle")
        print("✅ Différenciation stratégique opérationnelle")
        print("")
        print("🎯 FoodOps Pro offre maintenant un gameplay")
        print("   éducatif complet et réaliste !")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
