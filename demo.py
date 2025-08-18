#!/usr/bin/env python3
"""
Script de démonstration pour FoodOps Pro.
"""

from decimal import Decimal
from src.foodops_pro.io.data_loader import DataLoader
from src.foodops_pro.core.market import MarketEngine
from src.foodops_pro.core.costing import RecipeCostCalculator
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType


def demo_data_loading():
    """Démonstration du chargement des données."""
    print("=== DÉMONSTRATION CHARGEMENT DES DONNÉES ===")
    
    loader = DataLoader()
    data = loader.load_all_data()
    
    print(f"✓ {len(data['ingredients'])} ingrédients chargés")
    print(f"✓ {len(data['recipes'])} recettes chargées")
    print(f"✓ {len(data['suppliers'])} fournisseurs chargés")
    print(f"✓ Scénario '{data['scenario'].name}' chargé")
    
    # Affichage de quelques ingrédients
    print("\nQuelques ingrédients :")
    for i, (id, ingredient) in enumerate(data['ingredients'].items()):
        if i >= 5:
            break
        print(f"  - {ingredient.name}: {ingredient.cost_ht}€ HT/{ingredient.unit}")
    
    # Affichage de quelques recettes
    print("\nQuelques recettes :")
    for i, (id, recipe) in enumerate(data['recipes'].items()):
        if i >= 5:
            break
        print(f"  - {recipe.name}: {len(recipe.items)} ingrédients, {recipe.temps_total_min}min")
    
    return data


def demo_recipe_costing(data):
    """Démonstration du calcul de coûts de recettes."""
    print("\n=== DÉMONSTRATION CALCUL DE COÛTS ===")
    
    calculator = RecipeCostCalculator(data['ingredients'])
    
    # Test sur le burger classique
    burger_recipe = data['recipes']['burger_classic']
    breakdown = calculator.calculate_recipe_cost(burger_recipe)
    
    print(f"\nCoût de la recette '{burger_recipe.name}' :")
    print(f"  Coût total HT: {breakdown.total_cost_ht:.2f}€")
    print(f"  Coût par portion: {breakdown.cost_per_portion:.2f}€")
    print(f"  Coût main d'œuvre: {breakdown.preparation_time_cost:.2f}€")
    print(f"  Coût total avec MO: {breakdown.total_cost_with_labor:.2f}€")
    
    print("\nDétail par ingrédient :")
    for ingredient_cost in breakdown.ingredient_costs:
        print(f"  - {ingredient_cost.ingredient_name}: "
              f"{ingredient_cost.quantity_used} × {ingredient_cost.unit_cost_ht:.2f}€ = "
              f"{ingredient_cost.total_cost_ht:.2f}€")
    
    # Analyse de marge
    selling_price = Decimal("12.50")
    margin_analysis = calculator.calculate_margin_analysis(
        burger_recipe, selling_price, Decimal("0.10")
    )
    
    print(f"\nAnalyse de marge (prix de vente: {selling_price}€ TTC) :")
    print(f"  Prix HT: {margin_analysis['selling_price_ht']:.2f}€")
    print(f"  Marge HT: {margin_analysis['margin_ht']:.2f}€")
    print(f"  Marge %: {margin_analysis['margin_percentage']:.1f}%")
    print(f"  Food cost %: {margin_analysis['food_cost_percentage']:.1f}%")


def demo_market_simulation(data):
    """Démonstration de la simulation de marché."""
    print("\n=== DÉMONSTRATION SIMULATION DE MARCHÉ ===")
    
    # Création de deux restaurants
    fast_food = Restaurant(
        id="demo_fast",
        name="Demo Fast Food",
        type=RestaurantType.FAST,
        capacity_base=80,
        speed_service=Decimal("1.4"),
        staffing_level=2
    )
    
    classic = Restaurant(
        id="demo_classic",
        name="Demo Restaurant Classique",
        type=RestaurantType.CLASSIC,
        capacity_base=50,
        speed_service=Decimal("1.0"),
        staffing_level=2
    )
    
    # Configuration des menus
    fast_food.set_recipe_price("burger_classic", Decimal("10.50"))
    fast_food.set_recipe_price("burger_chicken", Decimal("11.00"))
    fast_food.activate_recipe("burger_classic")
    fast_food.activate_recipe("burger_chicken")
    
    classic.set_recipe_price("pasta_bolognese", Decimal("16.00"))
    classic.set_recipe_price("steak_frites", Decimal("22.00"))
    classic.activate_recipe("pasta_bolognese")
    classic.activate_recipe("steak_frites")
    
    restaurants = [fast_food, classic]
    
    # Simulation de marché
    scenario = data['scenario']
    market_engine = MarketEngine(scenario, random_seed=42)
    
    print(f"\nSimulation sur {scenario.base_demand} clients potentiels")
    print(f"Segments de marché :")
    for segment in scenario.segments:
        print(f"  - {segment.name}: {segment.share:.1%} (budget: {segment.budget}€)")
    
    # Simulation de 3 tours
    for turn in range(1, 4):
        print(f"\n--- TOUR {turn} ---")
        results = market_engine.allocate_demand(restaurants, turn=turn)
        
        for restaurant in restaurants:
            result = results[restaurant.id]
            print(f"{restaurant.name}:")
            print(f"  Capacité: {result.capacity} couverts")
            print(f"  Demande allouée: {result.allocated_demand}")
            print(f"  Clients servis: {result.served_customers}")

            # Calcul manuel des métriques pour l'affichage
            utilization = (result.served_customers / result.capacity * 100) if result.capacity > 0 else 0
            print(f"  Taux d'utilisation: {utilization:.1f}%")
            print(f"  Chiffre d'affaires: {result.revenue:.0f}€")

            if result.served_customers > 0:
                avg_ticket = result.revenue / result.served_customers
                print(f"  Ticket moyen: {avg_ticket:.2f}€")
    
    # Analyse finale
    analysis = market_engine.get_market_analysis()
    print(f"\nAnalyse du marché (dernier tour) :")
    print(f"  Total clients servis: {analysis['total_served']}")
    print(f"  CA total: {analysis['total_revenue']:.0f}€")
    print(f"  Taux d'utilisation marché: {analysis['market_utilization']:.1%}")
    print(f"  Satisfaction demande: {analysis['demand_satisfaction']:.1%}")


def main():
    """Fonction principale de démonstration."""
    print("🎮 FOODOPS PRO - DÉMONSTRATION")
    print("=" * 50)
    
    try:
        # Chargement des données
        data = demo_data_loading()
        
        # Calcul de coûts
        demo_recipe_costing(data)
        
        # Simulation de marché
        demo_market_simulation(data)
        
        print("\n✅ Démonstration terminée avec succès !")
        print("\nPour jouer, lancez : python -m src.foodops_pro.cli")
        
    except Exception as e:
        print(f"\n❌ Erreur durant la démonstration : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
