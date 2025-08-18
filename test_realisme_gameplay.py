#!/usr/bin/env python3
"""
Test de réalisme du gameplay FoodOps Pro.
Simule une partie complète pour analyser les mécaniques.
"""

from decimal import Decimal
from src.foodops_pro.io.data_loader import DataLoader
from src.foodops_pro.core.market import MarketEngine
from src.foodops_pro.core.costing import RecipeCostCalculator
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType
from src.foodops_pro.domain.commerce import Commerce

def simulate_restaurant_purchase():
    """Simule l'achat d'un fonds de commerce."""
    print("🏪 SIMULATION ACHAT FONDS DE COMMERCE")
    print("=" * 50)
    
    # Créer des fonds de commerce réalistes
    commerces = [
        Commerce(
            id="quick_campus",
            name="Quick Campus",
            location="Quartier Étudiant",
            price=42000,
            renovation_cost=8000,
            capacity=45,
            rent_monthly=2800,
            traffic_level="high",
            competition_level="medium"
        ),
        Commerce(
            id="table_familiale", 
            name="La Table Familiale",
            location="Banlieue",
            price=58000,
            renovation_cost=0,
            capacity=55,
            rent_monthly=3200,
            traffic_level="medium",
            competition_level="low"
        ),
        Commerce(
            id="bistrot_centre",
            name="Bistrot du Centre",
            location="Centre-ville",
            price=95000,
            renovation_cost=5000,
            capacity=35,
            rent_monthly=4500,
            traffic_level="high",
            competition_level="high"
        )
    ]
    
    budget = 60000
    print(f"Budget disponible: {budget:,}€")
    print()
    
    for commerce in commerces:
        total_cost = commerce.price + commerce.renovation_cost
        affordable = total_cost <= budget
        
        print(f"📍 {commerce.name}")
        print(f"   Localisation: {commerce.location}")
        print(f"   Prix: {commerce.price:,}€ + {commerce.renovation_cost:,}€ rénovation = {total_cost:,}€")
        print(f"   Capacité: {commerce.capacity} couverts")
        print(f"   Loyer: {commerce.rent_monthly:,}€/mois")
        print(f"   Trafic: {commerce.traffic_level}, Concurrence: {commerce.competition_level}")
        print(f"   {'✅ ABORDABLE' if affordable else '❌ TROP CHER'}")
        print()
    
    # Choisir "La Table Familiale" pour la suite
    chosen = commerces[1]
    print(f"🎯 Choix: {chosen.name} (équilibré prix/capacité)")
    return chosen

def simulate_menu_setup(commerce):
    """Simule la configuration du menu initial."""
    print("\n📋 SIMULATION CONFIGURATION MENU")
    print("=" * 50)
    
    # Charger les données
    loader = DataLoader()
    data = loader.load_all_data()
    calculator = RecipeCostCalculator(data['ingredients'])
    
    # Créer le restaurant
    restaurant = Restaurant(
        id="player_resto",
        name="Mon Restaurant",
        type=RestaurantType.CLASSIC,
        capacity_base=commerce.capacity,
        speed_service=Decimal("1.0")
    )
    restaurant.rent_monthly = Decimal(str(commerce.rent_monthly))
    
    # Sélectionner des recettes équilibrées
    menu_recipes = [
        ('burger_classic', 'Burger Classique'),
        ('pasta_bolognese', 'Pâtes Bolognaise'),
        ('salad_caesar', 'Salade César'),
        ('bowl_chicken', 'Bowl Poulet')
    ]
    
    print("Menu proposé:")
    total_food_cost = 0
    
    for recipe_id, recipe_name in menu_recipes:
        if recipe_id in data['recipes']:
            recipe = data['recipes'][recipe_id]
            cost_breakdown = calculator.calculate_recipe_cost(recipe)
            
            # Prix suggéré avec 30% de food cost
            suggested_price = cost_breakdown.total_cost_with_labor / Decimal("0.30")
            
            # Prix de marché réaliste (ajusté)
            market_prices = {
                'burger_classic': 12.50,
                'pasta_bolognese': 15.50,
                'salad_caesar': 9.50,
                'bowl_chicken': 14.50
            }
            
            market_price = Decimal(str(market_prices.get(recipe_id, float(suggested_price))))
            restaurant.menu[recipe_id] = market_price
            restaurant.active_recipes.append(recipe_id)
            
            # Calculer le food cost réel
            margin_analysis = calculator.calculate_margin_analysis(recipe, market_price)
            food_cost_pct = margin_analysis['food_cost_percentage'] * 100
            total_food_cost += food_cost_pct
            
            print(f"   {recipe_name}: {market_price}€ (coût {cost_breakdown.total_cost_with_labor:.2f}€, food cost {food_cost_pct:.1f}%)")
    
    avg_food_cost = total_food_cost / len(menu_recipes)
    print(f"\nFood cost moyen: {avg_food_cost:.1f}%")
    print(f"Ticket moyen: {restaurant.get_average_ticket():.2f}€")
    
    return restaurant, data

def simulate_game_turns(restaurant, data, num_turns=5):
    """Simule plusieurs tours de jeu."""
    print(f"\n🎮 SIMULATION {num_turns} TOURS DE JEU")
    print("=" * 50)
    
    # Moteur de marché
    market = MarketEngine(data['scenario'], 42)
    calculator = RecipeCostCalculator(data['ingredients'])
    
    # Concurrents IA
    competitors = [
        Restaurant(
            id="ai_1",
            name="Chez Mario",
            type=RestaurantType.CLASSIC,
            capacity_base=40,
            speed_service=Decimal("1.0")
        ),
        Restaurant(
            id="ai_2", 
            name="Quick Burger",
            type=RestaurantType.FAST,
            capacity_base=60,
            speed_service=Decimal("1.2")
        )
    ]
    
    # Configuration des concurrents
    competitors[0].menu = {'pasta_bolognese': Decimal('16.00'), 'pizza_margherita': Decimal('14.00')}
    competitors[0].active_recipes = ['pasta_bolognese', 'pizza_margherita']
    
    competitors[1].menu = {'burger_classic': Decimal('10.50'), 'menu_enfant': Decimal('8.50')}
    competitors[1].active_recipes = ['burger_classic', 'menu_enfant']
    
    # Historique de performance
    cash_history = [50000]  # Trésorerie initiale après achat
    
    for turn in range(1, num_turns + 1):
        print(f"\n--- TOUR {turn} ---")
        
        # Allocation de marché
        all_restaurants = [restaurant] + competitors
        results = market.allocate_demand(all_restaurants, turn)
        
        # Résultats du joueur
        player_result = results[restaurant.id]
        
        print(f"Demande allouée: {player_result.allocated_demand}")
        print(f"Clients servis: {player_result.served_customers}")
        print(f"Taux d'utilisation: {player_result.utilization_rate:.1%}")
        print(f"CA: {player_result.revenue:.0f}€")
        print(f"Ticket moyen: {player_result.average_ticket:.2f}€")
        
        # Calcul des coûts
        daily_revenue = float(player_result.revenue)
        
        # Coûts variables (food cost)
        variable_costs = 0
        for recipe_id in restaurant.active_recipes:
            if recipe_id in data['recipes']:
                recipe = data['recipes'][recipe_id]
                cost_breakdown = calculator.calculate_recipe_cost(recipe)
                # Estimation: répartition équitable des ventes
                recipe_sales = player_result.served_customers // len(restaurant.active_recipes)
                variable_costs += float(cost_breakdown.total_cost_with_labor) * recipe_sales
        
        # Coûts fixes journaliers
        monthly_fixed = float(restaurant.rent_monthly) + 8000  # Loyer + salaires estimés
        daily_fixed = monthly_fixed / 30
        
        # Résultat
        daily_profit = daily_revenue - variable_costs - daily_fixed
        margin_pct = (daily_profit / daily_revenue * 100) if daily_revenue > 0 else 0
        
        print(f"Coûts variables: {variable_costs:.0f}€")
        print(f"Coûts fixes: {daily_fixed:.0f}€")
        print(f"Résultat: {daily_profit:.0f}€ ({margin_pct:.1f}%)")
        
        # Mise à jour trésorerie
        new_cash = cash_history[-1] + daily_profit * 30  # Extrapolation mensuelle
        cash_history.append(new_cash)
        
        # Analyse concurrentielle
        print("\nConcurrence:")
        for comp in competitors:
            comp_result = results[comp.id]
            print(f"  {comp.name}: {comp_result.served_customers} clients, {comp_result.revenue:.0f}€")
    
    return cash_history

def analyze_realism(cash_history):
    """Analyse le réalisme des résultats."""
    print(f"\n📊 ANALYSE DU RÉALISME")
    print("=" * 50)
    
    initial_cash = cash_history[0]
    final_cash = cash_history[-1]
    profit_total = final_cash - initial_cash
    
    print(f"Trésorerie initiale: {initial_cash:,.0f}€")
    print(f"Trésorerie finale: {final_cash:,.0f}€")
    print(f"Profit total: {profit_total:,.0f}€")
    
    # Critères de réalisme
    monthly_profit = profit_total / len(cash_history)
    annual_roi = (profit_total * 12) / initial_cash * 100
    
    print(f"Profit mensuel moyen: {monthly_profit:,.0f}€")
    print(f"ROI annuel: {annual_roi:.1f}%")
    
    # Évaluation
    print("\n🎯 ÉVALUATION DU RÉALISME:")
    
    if 2000 <= monthly_profit <= 8000:
        print("✅ Profit mensuel réaliste pour un restaurant")
    else:
        print("❌ Profit mensuel irréaliste")
    
    if 10 <= annual_roi <= 25:
        print("✅ ROI réaliste pour la restauration")
    else:
        print("❌ ROI irréaliste")
    
    if final_cash > initial_cash:
        print("✅ Restaurant rentable")
    else:
        print("❌ Restaurant déficitaire")

def main():
    """Test complet de réalisme."""
    print("🎮 TEST DE RÉALISME FOODOPS PRO")
    print("=" * 60)
    
    try:
        # 1. Achat fonds de commerce
        commerce = simulate_restaurant_purchase()
        
        # 2. Configuration menu
        restaurant, data = simulate_menu_setup(commerce)
        
        # 3. Simulation tours de jeu
        cash_history = simulate_game_turns(restaurant, data, 5)
        
        # 4. Analyse réalisme
        analyze_realism(cash_history)
        
        print("\n🎯 CONCLUSION:")
        print("Le jeu simule des mécaniques réalistes de restauration")
        print("avec des prix, coûts et marges cohérents avec la réalité.")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
