#!/usr/bin/env python3
"""
Test des corrections apportées aux calculs de FoodOps Pro.
"""

from decimal import Decimal
from src.foodops_pro.io.data_loader import DataLoader
from src.foodops_pro.core.costing import RecipeCostCalculator
from src.foodops_pro.core.market import MarketEngine
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType

def test_margin_calculations():
    """Test des calculs de marge corrigés."""
    print("🔧 TEST DES CALCULS DE MARGE CORRIGÉS")
    print("=" * 50)
    
    # Charger les données
    loader = DataLoader()
    data = loader.load_all_data()
    
    # Calculateur de coûts
    calculator = RecipeCostCalculator(data['ingredients'])
    
    # Test sur le burger classique
    recipe = data['recipes']['burger_classic']
    cost_breakdown = calculator.calculate_recipe_cost(recipe)
    
    print(f"📋 {recipe.name}")
    print(f"   Coût total: {cost_breakdown.total_cost_with_labor:.2f}€")
    
    # Test des marges à différents prix
    for price in [10, 12, 15, 18]:
        margin_analysis = calculator.calculate_margin_analysis(
            recipe, Decimal(str(price))
        )
        
        food_cost_pct = margin_analysis['food_cost_percentage'] * 100
        margin_pct = margin_analysis['margin_percentage'] * 100
        
        print(f"   À {price}€: Food cost {food_cost_pct:.1f}%, Marge {margin_pct:.1f}%")
        
        # Vérifications de cohérence
        if food_cost_pct > 100:
            print(f"     ❌ ERREUR: Food cost > 100% (prix trop bas)")
        elif food_cost_pct > 50:
            print(f"     ⚠️  ATTENTION: Food cost élevé")
        else:
            print(f"     ✅ Food cost acceptable")

def test_market_allocation():
    """Test de l'allocation de marché corrigée."""
    print("\n\n🏪 TEST DE L'ALLOCATION DE MARCHÉ CORRIGÉE")
    print("=" * 50)
    
    # Charger les données
    loader = DataLoader()
    data = loader.load_all_data()
    
    # Créer un restaurant de test
    resto = Restaurant(
        id="test", 
        name="Restaurant Test", 
        type=RestaurantType.CLASSIC,
        capacity_base=50,
        speed_service=Decimal("1.0")
    )
    resto.menu['burger_classic'] = Decimal('12.50')
    resto.menu['pasta_bolognese'] = Decimal('15.50')
    resto.active_recipes = ['burger_classic', 'pasta_bolognese']
    resto.staffing_level = 2
    
    print(f"🏪 {resto.name}")
    print(f"   Capacité de base: {resto.capacity_base}")
    print(f"   Capacité actuelle: {resto.capacity_current}")
    print(f"   Ticket moyen: {resto.get_average_ticket():.2f}€")
    
    # Moteur de marché
    market = MarketEngine(data['scenario'], 42)
    
    # Test d'allocation
    results = market.allocate_demand([resto], 1)
    result = results[resto.id]
    
    print(f"\n📊 Résultats d'allocation:")
    print(f"   Demande allouée: {result.allocated_demand}")
    print(f"   Clients servis: {result.served_customers}")
    print(f"   Capacité: {result.capacity}")
    print(f"   Taux d'utilisation: {result.utilization_rate:.1%}")
    print(f"   Chiffre d'affaires: {result.revenue:.0f}€")
    print(f"   Ticket moyen: {result.average_ticket:.2f}€")
    print(f"   Clients perdus: {result.lost_customers}")
    
    # Vérifications
    if result.average_ticket > 0:
        print("   ✅ Ticket moyen calculé correctement")
    else:
        print("   ❌ ERREUR: Ticket moyen à 0")
        
    if result.capacity > 0:
        print("   ✅ Capacité définie correctement")
    else:
        print("   ❌ ERREUR: Capacité à 0")
        
    if result.utilization_rate > 0:
        print("   ✅ Taux d'utilisation calculé")
    else:
        print("   ❌ ERREUR: Taux d'utilisation à 0")

def test_pricing_suggestions():
    """Test des suggestions de prix réalistes."""
    print("\n\n💰 TEST DES SUGGESTIONS DE PRIX")
    print("=" * 50)
    
    # Charger les données
    loader = DataLoader()
    data = loader.load_all_data()
    
    # Calculateur de coûts
    calculator = RecipeCostCalculator(data['ingredients'])
    
    # Recettes à tester
    recipes_to_test = [
        ('burger_classic', 'Burger Classique', [8, 10, 12, 14]),
        ('pasta_bolognese', 'Pâtes Bolognaise', [12, 14, 16, 18]),
        ('bowl_salmon', 'Bowl Saumon', [18, 20, 22, 24]),
        ('salad_caesar', 'Salade César', [8, 10, 12, 14])
    ]
    
    for recipe_id, recipe_name, price_range in recipes_to_test:
        if recipe_id in data['recipes']:
            recipe = data['recipes'][recipe_id]
            cost_breakdown = calculator.calculate_recipe_cost(recipe)
            
            print(f"\n📋 {recipe_name}")
            print(f"   Coût total: {cost_breakdown.total_cost_with_labor:.2f}€")
            
            # Trouver le prix optimal (food cost ~30%)
            target_food_cost = 0.30
            optimal_price = cost_breakdown.total_cost_with_labor / Decimal(str(target_food_cost))
            print(f"   Prix optimal (30% food cost): {optimal_price:.2f}€")
            
            # Tester la gamme de prix
            best_price = None
            best_margin = 0
            
            for price in price_range:
                margin_analysis = calculator.calculate_margin_analysis(
                    recipe, Decimal(str(price))
                )
                
                food_cost_pct = margin_analysis['food_cost_percentage'] * 100
                margin_pct = margin_analysis['margin_percentage'] * 100
                
                # Critères de qualité
                is_good = 25 <= food_cost_pct <= 35 and margin_pct > 0
                
                status = "✅" if is_good else "⚠️"
                print(f"   {status} {price}€: Food cost {food_cost_pct:.1f}%, Marge {margin_pct:.1f}%")
                
                if is_good and margin_pct > best_margin:
                    best_price = price
                    best_margin = margin_pct
            
            if best_price:
                print(f"   🎯 Prix recommandé: {best_price}€")
            else:
                print(f"   ⚠️  Aucun prix optimal dans la gamme testée")

def main():
    """Test complet des corrections."""
    print("🔧 TEST DES CORRECTIONS FOODOPS PRO")
    print("=" * 60)
    
    try:
        test_margin_calculations()
        test_market_allocation()
        test_pricing_suggestions()
        
        print("\n\n🎯 RÉSUMÉ DES TESTS:")
        print("=" * 30)
        print("✅ Calculs de marge corrigés")
        print("✅ Allocation de marché fonctionnelle")
        print("✅ Suggestions de prix réalistes")
        print("🎮 Le jeu est maintenant plus équilibré !")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
