#!/usr/bin/env python3
"""
Test simple du CLI pour identifier les problèmes.
"""

try:
    print("=== TEST CLI SIMPLE ===")

    # Test 1: Import du module CLI
    print("1. Test import CLI...")
    from src.foodops_pro.cli import FoodOpsGame

    print("   ✓ Import réussi")

    # Test 2: Initialisation du jeu
    print("2. Test initialisation...")
    game = FoodOpsGame(debug=True)
    print("   ✓ Initialisation réussie")

    # Test 3: Création d'un restaurant simple
    print("3. Test création restaurant...")
    from src.foodops_pro.domain.restaurant import RestaurantType

    restaurant = game._create_restaurant(
        "Test Restaurant", RestaurantType.CLASSIC, is_player=True
    )
    print(f"   ✓ Restaurant créé: {restaurant.name}")
    print(f"   ✓ Capacité: {restaurant.capacity_current}")
    print(f"   ✓ Menu actif: {len(restaurant.get_active_menu())} recettes")

    # Test 4: Test du formatage des résultats
    print("4. Test formatage résultats...")
    from src.foodops_pro.core.market import AllocationResult
    from decimal import Decimal

    result = AllocationResult(
        restaurant_id="test",
        allocated_demand=50,
        served_customers=45,
        capacity=50,
        revenue=Decimal("675.00"),
    )

    # Test du formatage problématique
    utilization_pct = f"{result.utilization_rate:.1%}"
    print(f"   ✓ Formatage taux utilisation: {utilization_pct}")

    # Test de la ligne complète
    line = (
        f"{'Test Restaurant':<20} "
        f"{result.allocated_demand:<8} "
        f"{result.served_customers:<8} "
        f"{result.capacity:<10} "
        f"{utilization_pct:<6} "
        f"{result.revenue:<10.0f}"
    )
    print(f"   ✓ Ligne formatée: {line}")

    print("\n✅ TOUS LES TESTS PASSENT - LE CLI DEVRAIT FONCTIONNER")

except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback

    traceback.print_exc()
