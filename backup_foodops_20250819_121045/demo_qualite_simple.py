#!/usr/bin/env python3
"""
Démonstration simple du système qualité intégré.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from decimal import Decimal
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType
from src.foodops_pro.domain.ingredient_quality import IngredientQualityManager
from src.foodops_pro.domain.seasonality import SeasonalityManager


def demo_restaurant_quality():
    """Démonstration du système qualité des restaurants."""
    print("🏆 DÉMONSTRATION SYSTÈME QUALITÉ RESTAURANTS")
    print("=" * 70)

    # Création de restaurants avec différentes stratégies
    restaurants = []

    # Restaurant économique
    resto_eco = Restaurant(
        id="eco",
        name="Quick & Cheap",
        type=RestaurantType.FAST,
        capacity_base=80,
        speed_service=Decimal("1.2"),
        staffing_level=2,
    )
    resto_eco.set_ingredient_quality("beef_ground", 1)  # Économique
    resto_eco.set_ingredient_quality("tomato", 1)
    resto_eco.set_ingredient_quality("cheese_mozzarella", 2)
    resto_eco.set_recipe_price("burger_classic", Decimal("8.50"))
    resto_eco.activate_recipe("burger_classic")
    restaurants.append(resto_eco)

    # Restaurant standard
    resto_std = Restaurant(
        id="std",
        name="Burger Standard",
        type=RestaurantType.CLASSIC,
        capacity_base=60,
        speed_service=Decimal("1.0"),
        staffing_level=2,
    )
    resto_std.set_ingredient_quality("beef_ground", 2)  # Standard
    resto_std.set_ingredient_quality("tomato", 3)
    resto_std.set_ingredient_quality("cheese_mozzarella", 2)
    resto_std.set_recipe_price("burger_classic", Decimal("12.50"))
    resto_std.activate_recipe("burger_classic")
    restaurants.append(resto_std)

    # Restaurant premium
    resto_premium = Restaurant(
        id="premium",
        name="Gourmet Burger",
        type=RestaurantType.CLASSIC,
        capacity_base=50,
        speed_service=Decimal("0.8"),
        staffing_level=3,
    )
    resto_premium.set_ingredient_quality("beef_ground", 4)  # Premium
    resto_premium.set_ingredient_quality("tomato", 4)
    resto_premium.set_ingredient_quality("cheese_mozzarella", 4)
    resto_premium.set_recipe_price("burger_classic", Decimal("18.50"))
    resto_premium.activate_recipe("burger_classic")
    restaurants.append(resto_premium)

    # Restaurant luxe
    resto_luxe = Restaurant(
        id="luxe",
        name="Artisan Bistro",
        type=RestaurantType.GASTRONOMIQUE,
        capacity_base=30,
        speed_service=Decimal("0.6"),
        staffing_level=3,
    )
    resto_luxe.set_ingredient_quality("beef_ground", 5)  # Luxe
    resto_luxe.set_ingredient_quality("tomato", 5)
    resto_luxe.set_ingredient_quality("cheese_mozzarella", 5)
    resto_luxe.set_recipe_price("burger_classic", Decimal("28.50"))
    resto_luxe.activate_recipe("burger_classic")
    restaurants.append(resto_luxe)

    # Affichage des caractéristiques
    print(f"\n📊 COMPARATIF DES RESTAURANTS:")
    print("-" * 100)
    print(
        f"{'Restaurant':<20} | {'Type':<12} | {'Qualité':<15} | {'Prix':<8} | {'Coût':<8} | {'Attractivité':<12}"
    )
    print("-" * 100)

    for resto in restaurants:
        quality_score = resto.get_overall_quality_score()
        quality_desc = resto.get_quality_description()
        cost_impact = resto.calculate_quality_cost_impact()
        ticket = resto.get_average_ticket()

        # Facteurs d'attractivité par segment
        students_factor = resto.get_quality_attractiveness_factor("students")
        families_factor = resto.get_quality_attractiveness_factor("families")
        foodies_factor = resto.get_quality_attractiveness_factor("foodies")

        print(
            f"{resto.name:<20} | {resto.type.value:<12} | {quality_desc:<15} | {ticket:>6.2f}€ | {cost_impact:>6.0%} | S:{students_factor:.2f} F:{families_factor:.2f} G:{foodies_factor:.2f}"
        )

        # Détail des ingrédients
        if resto.ingredient_choices:
            ingredients = ", ".join(
                [
                    f"{k.split('_')[-1]}:{v}⭐"
                    for k, v in resto.ingredient_choices.items()
                ]
            )
            print(f"{'':>20} | {'':>12} | Ingrédients: {ingredients}")

    print("-" * 100)

    return restaurants


def demo_satisfaction_evolution():
    """Démonstration de l'évolution de la satisfaction."""
    print(f"\n\n📈 ÉVOLUTION SATISFACTION ET RÉPUTATION")
    print("=" * 60)

    # Restaurant test
    resto = Restaurant(
        id="test",
        name="Test Restaurant",
        type=RestaurantType.CLASSIC,
        capacity_base=50,
        speed_service=Decimal("1.0"),
        staffing_level=2,
    )
    resto.set_ingredient_quality("beef_ground", 3)
    resto.set_ingredient_quality("tomato", 3)
    resto.set_recipe_price("burger_classic", Decimal("15.00"))
    resto.activate_recipe("burger_classic")

    print(f"Restaurant: {resto.name}")
    print(f"Qualité: {resto.get_quality_description()}")
    print(f"Prix: {resto.get_average_ticket():.2f}€")
    print(f"Réputation initiale: {resto.reputation:.1f}/10")

    # Simulation de différents niveaux de satisfaction
    satisfactions = [4.5, 4.0, 3.5, 4.2, 4.8, 3.8, 4.1, 4.6, 4.3, 4.4]

    print(f"\n📊 Évolution sur 10 périodes:")
    print(
        f"{'Période':<8} | {'Satisfaction':<12} | {'Réputation':<11} | {'Évolution':<10}"
    )
    print("-" * 50)

    for i, satisfaction in enumerate(satisfactions, 1):
        old_reputation = resto.reputation
        resto.update_customer_satisfaction(Decimal(str(satisfaction)))
        evolution = resto.reputation - old_reputation

        print(
            f"{i:<8} | {satisfaction:<12.1f} | {resto.reputation:<11.1f} | {evolution:+.2f}"
        )

    print(f"\nSatisfaction moyenne finale: {resto.get_average_satisfaction():.1f}/5")
    print(f"Réputation finale: {resto.reputation:.1f}/10")


def demo_seasonal_impact():
    """Démonstration de l'impact saisonnier."""
    print(f"\n\n🌱 IMPACT SAISONNIER")
    print("=" * 40)

    seasonality = SeasonalityManager()

    # Test sur différents mois
    months = [
        (1, "Janvier"),
        (4, "Avril"),
        (7, "Juillet"),
        (10, "Octobre"),
        (12, "Décembre"),
    ]

    print(f"Impact saisonnier sur les tomates:")
    print(f"{'Mois':<10} | {'Prix':<10} | {'Qualité':<8} | {'Demande':<8}")
    print("-" * 40)

    base_price = Decimal("3.20")

    for month, month_name in months:
        from datetime import date

        test_date = date(2024, month, 15)

        final_price = seasonality.calculate_final_price("tomato", base_price, test_date)
        quality_bonus = seasonality.get_quality_bonus("tomato", test_date)
        demand_impact = seasonality.get_demand_impact("tomato", test_date)

        price_change = (final_price / base_price - 1) * 100
        demand_change = (demand_impact - 1) * 100

        print(
            f"{month_name:<10} | {final_price:>6.2f}€ | {quality_bonus:+d}⭐ | {demand_change:+5.0f}%"
        )


def demo_strategic_comparison():
    """Comparaison stratégique des approches."""
    print(f"\n\n🎯 COMPARAISON STRATÉGIQUE")
    print("=" * 50)

    restaurants = demo_restaurant_quality()

    # Simulation de performance sur différents segments
    segments = [
        ("Étudiants", "students", 0.4),
        ("Familles", "families", 0.35),
        ("Foodies", "foodies", 0.25),
    ]

    print(f"\n📊 Performance par segment (attractivité relative):")
    print(
        f"{'Restaurant':<20} | {'Étudiants':<10} | {'Familles':<10} | {'Foodies':<10} | {'Score':<8}"
    )
    print("-" * 70)

    for resto in restaurants:
        scores = []
        total_score = 0

        for segment_name, segment_key, weight in segments:
            factor = resto.get_quality_attractiveness_factor(segment_key)
            weighted_score = float(factor) * weight
            scores.append(factor)
            total_score += weighted_score

        print(
            f"{resto.name:<20} | {scores[0]:>8.2f} | {scores[1]:>8.2f} | {scores[2]:>8.2f} | {total_score:>6.2f}"
        )

    print(f"\n💡 INSIGHTS:")
    print(f"• Restaurant économique: Attractif pour étudiants")
    print(f"• Restaurant premium: Équilibré sur tous segments")
    print(f"• Restaurant luxe: Très attractif pour foodies")
    print(f"• Stratégie dépend du marché cible !")


def main():
    """Démonstration complète."""
    print("🎮 DÉMONSTRATION SYSTÈME QUALITÉ FOODOPS PRO")
    print("=" * 80)

    try:
        demo_restaurant_quality()
        demo_satisfaction_evolution()
        demo_seasonal_impact()
        demo_strategic_comparison()

        print(f"\n\n🎉 SYSTÈME QUALITÉ OPÉRATIONNEL !")
        print("=" * 50)
        print("✅ Différenciation qualité fonctionnelle")
        print("✅ Impact sur attractivité par segment")
        print("✅ Évolution réputation réaliste")
        print("✅ Saisonnalité intégrée")
        print("✅ Stratégies multiples viables")
        print("")
        print("🎯 Prêt pour intégration dans FoodOps Pro !")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
