#!/usr/bin/env python3
"""
Démonstration directe du jeu FoodOps Pro.
"""

def demo_tour_complet():
    """Démonstration d'un tour complet de jeu."""
    print("🍔 DÉMONSTRATION FOODOPS PRO")
    print("=" * 50)
    
    # État initial du restaurant
    restaurant = {
        "name": "Demo Restaurant",
        "budget": 10000,
        "price": 12.50,
        "quality": 2,  # 1-5
        "staff": 2,    # 1-3
        "reputation": 5.0
    }
    
    print(f"\n🏪 Restaurant: {restaurant['name']}")
    print(f"💰 Budget: {restaurant['budget']}€")
    print(f"💵 Prix: {restaurant['price']}€")
    print(f"⭐ Qualité: {restaurant['quality']}/5")
    print(f"👥 Personnel: Niveau {restaurant['staff']}")
    print(f"🌟 Réputation: {restaurant['reputation']}/10")
    
    # Simulation de marché
    print(f"\n📊 SIMULATION MARCHÉ:")
    
    segments = {
        "étudiants": {"budget": 11.0, "clients_potentiels": 150},
        "familles": {"budget": 17.0, "clients_potentiels": 180}, 
        "foodies": {"budget": 25.0, "clients_potentiels": 90}
    }
    
    total_clients = 0
    
    for segment, data in segments.items():
        # Attractivité basée sur prix vs budget du segment
        price_ratio = restaurant['price'] / data['budget']
        
        if price_ratio <= 0.8:
            attractiveness = 1.2  # Très attractif
        elif price_ratio <= 1.0:
            attractiveness = 1.0  # Attractif
        elif price_ratio <= 1.3:
            attractiveness = 0.7  # Acceptable
        else:
            attractiveness = 0.3  # Cher
        
        # Bonus qualité
        quality_bonus = 0.8 + (restaurant['quality'] - 1) * 0.1
        
        # Clients du segment
        segment_clients = int(data['clients_potentiels'] * 0.3 * attractiveness * quality_bonus)
        total_clients += segment_clients
        
        print(f"   {segment}: {segment_clients} clients (prix {price_ratio:.1f}x budget)")
    
    # Limiter par capacité
    capacities = {1: 120, 2: 150, 3: 180}
    max_capacity = capacities[restaurant['staff']]
    total_clients = min(total_clients, max_capacity)
    
    print(f"\n👥 Total clients servis: {total_clients}/{max_capacity}")
    
    # Calculs financiers
    print(f"\n💰 CALCULS FINANCIERS:")
    
    # Revenus
    revenue = restaurant['price'] * total_clients
    print(f"   Chiffre d'affaires: {revenue:.2f}€")
    
    # Coûts
    ingredient_costs = {1: 2.94, 2: 4.20, 3: 5.25, 4: 6.30, 5: 8.40}
    ingredient_cost = ingredient_costs[restaurant['quality']] * total_clients
    
    staff_costs = {1: 2200, 2: 2800, 3: 3600}
    staff_cost = staff_costs[restaurant['staff']]
    
    overhead = 1200
    
    total_costs = ingredient_cost + staff_cost + overhead
    
    print(f"   Coûts ingrédients: {ingredient_cost:.2f}€")
    print(f"   Coûts personnel: {staff_cost:.2f}€")
    print(f"   Charges fixes: {overhead:.2f}€")
    print(f"   Total coûts: {total_costs:.2f}€")
    
    # Profit
    profit = revenue - total_costs
    print(f"   {'📈' if profit >= 0 else '📉'} Profit: {profit:+.2f}€")
    
    # Marge
    if revenue > 0:
        margin = profit / revenue * 100
        print(f"   📊 Marge: {margin:.1f}%")
    
    # Satisfaction
    base_satisfaction = 2.0 + (restaurant['quality'] - 1) * 0.5
    price_penalty = max(0, (restaurant['price'] - 15) * 0.1)
    satisfaction = max(1.0, min(5.0, base_satisfaction - price_penalty))
    
    print(f"   😊 Satisfaction: {satisfaction:.1f}/5")
    
    # Nouveau budget
    new_budget = restaurant['budget'] + profit
    print(f"   💰 Nouveau budget: {new_budget:.2f}€")
    
    return {
        "clients": total_clients,
        "revenue": revenue,
        "profit": profit,
        "satisfaction": satisfaction,
        "new_budget": new_budget
    }

def demo_strategies():
    """Démonstration de différentes stratégies."""
    print(f"\n\n🎯 COMPARAISON STRATÉGIES")
    print("=" * 50)
    
    strategies = [
        {"name": "Économique", "price": 8.50, "quality": 1, "staff": 1},
        {"name": "Standard", "price": 12.50, "quality": 2, "staff": 2},
        {"name": "Premium", "price": 18.00, "quality": 4, "staff": 3},
        {"name": "Luxe", "price": 25.00, "quality": 5, "staff": 3}
    ]
    
    print(f"{'Stratégie':<12} | {'Prix':<6} | {'Qualité':<7} | {'Clients':<8} | {'Profit':<8} | {'Marge':<6}")
    print("-" * 70)
    
    for strategy in strategies:
        # Simulation rapide
        restaurant = {
            "name": "Test",
            "budget": 10000,
            "price": strategy["price"],
            "quality": strategy["quality"],
            "staff": strategy["staff"],
            "reputation": 5.0
        }
        
        # Calcul simplifié des clients
        total_demand = 420  # Demande totale du marché
        
        # Attractivité prix (plus c'est cher, moins il y a de clients)
        price_factor = max(0.3, 1.5 - (strategy["price"] - 10) * 0.05)
        
        # Attractivité qualité
        quality_factor = 0.7 + strategy["quality"] * 0.1
        
        # Clients
        clients = int(total_demand * 0.35 * price_factor * quality_factor)
        
        # Capacité
        capacities = {1: 120, 2: 150, 3: 180}
        clients = min(clients, capacities[strategy["staff"]])
        
        # Profit simplifié
        revenue = strategy["price"] * clients
        
        ingredient_costs = {1: 2.94, 2: 4.20, 3: 5.25, 4: 6.30, 5: 8.40}
        costs = (ingredient_costs[strategy["quality"]] * clients + 
                {1: 2200, 2: 2800, 3: 3600}[strategy["staff"]] + 1200)
        
        profit = revenue - costs
        margin = (profit / revenue * 100) if revenue > 0 else 0
        
        print(f"{strategy['name']:<12} | {strategy['price']:>5.2f}€ | {strategy['quality']:>7}/5 | {clients:>8} | {profit:>+7.0f}€ | {margin:>5.1f}%")
    
    print(f"\n💡 OBSERVATIONS:")
    print(f"   • Économique: Volume élevé, marge faible")
    print(f"   • Standard: Équilibre optimal")
    print(f"   • Premium: Marge élevée, volume modéré")
    print(f"   • Luxe: Très haute marge, volume limité")

def demo_interactive():
    """Démonstration interactive."""
    print(f"\n\n🎮 DÉMONSTRATION INTERACTIVE")
    print("=" * 50)
    
    print("Vous allez prendre quelques décisions pour voir l'impact...")
    
    try:
        # Choix du prix
        print(f"\n💵 CHOIX DU PRIX:")
        print("   Segments: Étudiants (11€), Familles (17€), Foodies (25€)")
        
        while True:
            try:
                price = float(input("Votre prix (8-30€): "))
                if 8 <= price <= 30:
                    break
                else:
                    print("Prix doit être entre 8€ et 30€")
            except ValueError:
                print("Entrez un nombre valide")
        
        # Choix de la qualité
        print(f"\n⭐ CHOIX DE LA QUALITÉ:")
        print("   1⭐ Économique  2⭐ Standard  3⭐ Supérieur  4⭐ Premium  5⭐ Luxe")
        
        while True:
            try:
                quality = int(input("Votre niveau qualité (1-5): "))
                if 1 <= quality <= 5:
                    break
                else:
                    print("Qualité doit être entre 1 et 5")
            except ValueError:
                print("Entrez un nombre valide")
        
        # Simulation avec les choix
        restaurant = {
            "name": "Votre Restaurant",
            "budget": 10000,
            "price": price,
            "quality": quality,
            "staff": 2,  # Standard
            "reputation": 5.0
        }
        
        print(f"\n📊 RÉSULTATS AVEC VOS CHOIX:")
        results = demo_tour_complet_custom(restaurant)
        
        # Évaluation
        print(f"\n🎯 ÉVALUATION:")
        if results["profit"] >= 1000:
            print("🏆 EXCELLENT ! Très bon profit")
        elif results["profit"] >= 500:
            print("✅ BIEN ! Profit correct")
        elif results["profit"] >= 0:
            print("⚠️ MOYEN. Profit faible")
        else:
            print("❌ PERTE ! Révisez votre stratégie")
        
        if results["satisfaction"] >= 4.0:
            print("😍 Clients très satisfaits")
        elif results["satisfaction"] >= 3.0:
            print("😊 Clients satisfaits")
        else:
            print("😞 Clients mécontents")
    
    except KeyboardInterrupt:
        print("\n👋 Démonstration interrompue")

def demo_tour_complet_custom(restaurant):
    """Version personnalisée du calcul de tour."""
    # Simulation simplifiée
    total_demand = 420
    
    # Attractivité prix
    avg_budget = 17.0  # Budget moyen des segments
    price_ratio = restaurant['price'] / avg_budget
    
    if price_ratio <= 0.7:
        price_factor = 1.3
    elif price_ratio <= 1.0:
        price_factor = 1.0
    elif price_ratio <= 1.5:
        price_factor = 0.7
    else:
        price_factor = 0.4
    
    # Attractivité qualité
    quality_factor = 0.6 + restaurant['quality'] * 0.15
    
    # Clients
    clients = int(total_demand * 0.35 * price_factor * quality_factor)
    clients = min(clients, 150)  # Capacité standard
    
    # Finances
    revenue = restaurant['price'] * clients
    
    ingredient_costs = {1: 2.94, 2: 4.20, 3: 5.25, 4: 6.30, 5: 8.40}
    costs = ingredient_costs[restaurant['quality']] * clients + 2800 + 1200
    
    profit = revenue - costs
    
    # Satisfaction
    satisfaction = 2.0 + (restaurant['quality'] - 1) * 0.5
    if restaurant['price'] > 20:
        satisfaction -= 0.5
    satisfaction = max(1.0, min(5.0, satisfaction))
    
    print(f"   👥 Clients: {clients}")
    print(f"   💰 Revenus: {revenue:.2f}€")
    print(f"   💸 Coûts: {costs:.2f}€")
    print(f"   {'📈' if profit >= 0 else '📉'} Profit: {profit:+.2f}€")
    print(f"   😊 Satisfaction: {satisfaction:.1f}/5")
    
    return {"clients": clients, "revenue": revenue, "profit": profit, "satisfaction": satisfaction}

def main():
    """Démonstration principale."""
    print("🎮 FOODOPS PRO - DÉMONSTRATION COMPLÈTE")
    print("=" * 60)
    
    # Tour complet
    demo_tour_complet()
    
    # Comparaison stratégies
    demo_strategies()
    
    # Démonstration interactive
    try:
        demo_interactive()
    except:
        pass
    
    print(f"\n\n🎉 DÉMONSTRATION TERMINÉE !")
    print("=" * 40)
    print("✅ Vous avez vu les mécaniques principales de FoodOps Pro")
    print("🎯 Prix, qualité, personnel impactent clients et profits")
    print("📊 Différentes stratégies sont viables")
    print("🎮 Le jeu complet offre 10 tours avec évolution")
    
    input("\nAppuyez sur Entrée pour terminer...")

if __name__ == "__main__":
    main()
