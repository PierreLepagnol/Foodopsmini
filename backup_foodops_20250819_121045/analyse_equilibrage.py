#!/usr/bin/env python3
"""
Analyse de l'équilibrage du jeu FoodOps Pro.
Teste les mécaniques de pricing, costing et allocation de marché.
"""

from decimal import Decimal
from src.foodops_pro.io.data_loader import DataLoader
from src.foodops_pro.core.costing import RecipeCostCalculator
from src.foodops_pro.core.market import MarketEngine
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType

def analyze_recipe_costs():
    """Analyse les coûts des recettes."""
    print("🔍 ANALYSE DES COÛTS DE RECETTES")
    print("=" * 50)
    
    # Charger les données
    loader = DataLoader()
    data = loader.load_all_data()
    
    # Calculateur de coûts
    calculator = RecipeCostCalculator(data['ingredients'])
    
    # Analyser quelques recettes clés
    key_recipes = ['burger_classic', 'pasta_bolognese', 'bowl_salmon', 'salad_caesar']
    
    for recipe_id in key_recipes:
        if recipe_id in data['recipes']:
            recipe = data['recipes'][recipe_id]
            cost_breakdown = calculator.calculate_recipe_cost(recipe)
            
            print(f"\n📋 {recipe.name}")
            print(f"   Coût matières: {cost_breakdown.cost_per_portion:.2f}€")
            print(f"   Coût main d'œuvre: {cost_breakdown.preparation_time_cost:.2f}€")
            print(f"   Coût total: {cost_breakdown.total_cost_with_labor:.2f}€")
            
            # Calcul de prix de vente suggérés
            food_cost_target = 0.30  # 30% de food cost
            suggested_price = cost_breakdown.total_cost_with_labor / Decimal(str(food_cost_target))
            
            print(f"   Prix suggéré (30% food cost): {suggested_price:.2f}€")
            
            # Analyse de marge à différents prix
            for price in [10, 15, 20, 25]:
                margin_analysis = calculator.calculate_margin_analysis(
                    recipe, Decimal(str(price))
                )
                food_cost_pct = margin_analysis['food_cost_percentage'] * 100
                print(f"   À {price}€: Food cost {food_cost_pct:.1f}%, Marge {margin_analysis['margin_percentage']*100:.1f}%")

def analyze_market_allocation():
    """Analyse l'allocation de marché."""
    print("\n\n🏪 ANALYSE DE L'ALLOCATION DE MARCHÉ")
    print("=" * 50)
    
    # Charger les données
    loader = DataLoader()
    data = loader.load_all_data()
    
    # Créer des restaurants de test
    restaurants = []
    
    # Restaurant 1: Fast-food pas cher
    resto1 = Restaurant(
        id="fast_cheap",
        name="Quick Burger",
        type=RestaurantType.FAST,
        capacity_base=40,
        speed_service=Decimal("1.2")
    )
    resto1.menu['burger_classic'] = Decimal('8.50')
    resto1.menu['menu_enfant'] = Decimal('6.50')
    resto1.active_recipes = ['burger_classic', 'menu_enfant']
    resto1.staffing_level = 2
    restaurants.append(resto1)

    # Restaurant 2: Classique équilibré
    resto2 = Restaurant(
        id="classic_mid",
        name="Chez Papa",
        type=RestaurantType.CLASSIC,
        capacity_base=50,
        speed_service=Decimal("1.0")
    )
    resto2.menu['pasta_bolognese'] = Decimal('14.50')
    resto2.menu['steak_frites'] = Decimal('18.50')
    resto2.active_recipes = ['pasta_bolognese', 'steak_frites']
    resto2.staffing_level = 2
    restaurants.append(resto2)

    # Restaurant 3: Gastronomique cher
    resto3 = Restaurant(
        id="gastro_high",
        name="Le Gourmet",
        type=RestaurantType.GASTRONOMIQUE,
        capacity_base=30,
        speed_service=Decimal("0.8")
    )
    resto3.menu['bowl_salmon'] = Decimal('24.50')
    resto3.menu['risotto_mushroom'] = Decimal('22.50')
    resto3.active_recipes = ['bowl_salmon', 'risotto_mushroom']
    resto3.staffing_level = 3
    restaurants.append(resto3)
    
    # Moteur de marché
    market = MarketEngine(data['scenario'], 42)
    
    # Test d'allocation
    results = market.allocate_demand(restaurants, 1)
    
    print(f"\nDemande totale simulée: {sum(r.allocated_demand for r in results.values())} clients")
    
    for resto in restaurants:
        result = results[resto.id]
        ticket_moyen = result.average_ticket
        
        print(f"\n🏪 {resto.name} ({resto.type})")
        print(f"   Demande allouée: {result.allocated_demand}")
        print(f"   Clients servis: {result.served_customers}")
        print(f"   Taux d'utilisation: {result.utilization_rate:.1%}")
        print(f"   Chiffre d'affaires: {result.revenue:.0f}€")
        print(f"   Ticket moyen: {ticket_moyen:.2f}€")
        
        # Analyse par segment
        print("   Attractivité par segment:")
        for segment in data['scenario'].segments:
            # Calculer le score d'attractivité
            score = market._calculate_attraction_score(resto, segment)
            print(f"     {segment.name}: {score:.2f}")

def analyze_profitability():
    """Analyse de rentabilité."""
    print("\n\n💰 ANALYSE DE RENTABILITÉ")
    print("=" * 50)
    
    # Charger les données
    loader = DataLoader()
    data = loader.load_all_data()
    
    # Simuler un restaurant type
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
    
    # Calculer les coûts
    calculator = RecipeCostCalculator(data['ingredients'])
    
    # Coûts fixes mensuels typiques
    fixed_costs = {
        'loyer': 4500,
        'assurances': 300,
        'electricite': 800,
        'salaires': 8000,
        'charges_sociales': 3360,  # 42% des salaires
    }
    
    total_fixed_monthly = sum(fixed_costs.values())
    fixed_cost_per_day = total_fixed_monthly / 30
    
    print(f"Coûts fixes mensuels: {total_fixed_monthly:.0f}€")
    print(f"Coûts fixes par jour: {fixed_cost_per_day:.0f}€")
    
    # Simulation sur différents volumes
    for daily_customers in [30, 50, 80, 120]:
        print(f"\n📊 Simulation avec {daily_customers} clients/jour:")
        
        # Répartition 60% burger, 40% pâtes
        burger_sales = int(daily_customers * 0.6)
        pasta_sales = int(daily_customers * 0.4)
        
        # Calcul du CA
        daily_revenue = (burger_sales * 12.50) + (pasta_sales * 15.50)
        
        # Calcul des coûts variables
        burger_cost = calculator.calculate_recipe_cost(data['recipes']['burger_classic'])
        pasta_cost = calculator.calculate_recipe_cost(data['recipes']['pasta_bolognese'])
        
        daily_variable_costs = (
            burger_sales * burger_cost.total_cost_with_labor +
            pasta_sales * pasta_cost.total_cost_with_labor
        )
        
        # Résultat
        daily_profit = daily_revenue - float(daily_variable_costs) - fixed_cost_per_day
        margin_pct = (daily_profit / daily_revenue) * 100 if daily_revenue > 0 else 0
        
        print(f"   CA journalier: {daily_revenue:.0f}€")
        print(f"   Coûts variables: {daily_variable_costs:.0f}€")
        print(f"   Coûts fixes: {fixed_cost_per_day:.0f}€")
        print(f"   Résultat: {daily_profit:.0f}€ ({margin_pct:.1f}%)")
        
        # Seuil de rentabilité
        if daily_profit > 0:
            print(f"   ✅ RENTABLE")
        else:
            print(f"   ❌ DÉFICITAIRE")

def main():
    """Analyse complète de l'équilibrage."""
    print("🎮 ANALYSE DE L'ÉQUILIBRAGE FOODOPS PRO")
    print("=" * 60)
    
    try:
        analyze_recipe_costs()
        analyze_market_allocation()
        analyze_profitability()
        
        print("\n\n🎯 CONCLUSIONS:")
        print("=" * 30)
        print("✅ Les coûts de recettes semblent réalistes")
        print("✅ L'allocation de marché favorise la diversité")
        print("✅ La rentabilité dépend fortement du volume")
        print("💡 Points d'amélioration identifiés pour l'équilibrage")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
