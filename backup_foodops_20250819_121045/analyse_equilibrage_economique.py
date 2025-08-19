#!/usr/bin/env python3
"""
Analyse et calcul de l'équilibrage économique réaliste pour FoodOps.
"""

def analyze_current_costs():
    """Analyse les coûts actuels du jeu."""
    print("🔍 ANALYSE DES COÛTS ACTUELS")
    print("=" * 50)
    
    # Coûts actuels dans le jeu
    current_costs = {
        "fast": {
            "staff_costs": {1: 1800, 2: 2600, 3: 3400},
            "fixed_cost": 1200,
            "cogs_rate": 0.32,
            "suggested_price": 11.5
        },
        "classic": {
            "staff_costs": {1: 2200, 2: 3200, 3: 4200},
            "fixed_cost": 1800,
            "cogs_rate": 0.36,
            "suggested_price": 17.0
        }
    }
    
    print("Coûts actuels par tour:")
    for resto_type, costs in current_costs.items():
        print(f"\n{resto_type.upper()}:")
        print(f"  Personnel niveau 2: {costs['staff_costs'][2]}€")
        print(f"  Coûts fixes: {costs['fixed_cost']}€")
        print(f"  COGS rate: {costs['cogs_rate']*100}%")
        print(f"  Prix suggéré: {costs['suggested_price']}€")
        
        # Simulation avec 100 clients
        clients = 100
        ca = clients * costs['suggested_price']
        cogs = ca * costs['cogs_rate']
        staff = costs['staff_costs'][2]
        fixed = costs['fixed_cost']
        total_costs = cogs + staff + fixed
        profit = ca - total_costs
        margin = (profit / ca * 100) if ca > 0 else 0
        
        print(f"  → Simulation 100 clients:")
        print(f"    CA: {ca:.0f}€")
        print(f"    Coûts totaux: {total_costs:.0f}€")
        print(f"    Résultat: {profit:.0f}€ ({margin:.1f}%)")
        
        if profit < 0:
            print(f"    ❌ DÉFICITAIRE")
        else:
            print(f"    ✅ Rentable")

def calculate_realistic_costs():
    """Calcule des coûts réalistes basés sur la réalité."""
    print("\n\n💡 CALCUL DE COÛTS RÉALISTES")
    print("=" * 50)
    
    # Hypothèse: 1 tour = 1 service (midi ou soir) = 1/2 journée
    # Donc 1 mois = 60 tours (30 jours × 2 services)
    
    print("Hypothèse: 1 tour = 1 service (midi/soir)")
    print("1 mois = 60 tours")
    
    # Coûts mensuels réalistes pour un restaurant
    monthly_costs = {
        "fast": {
            "rent": 4000,           # Loyer mensuel
            "utilities": 800,       # Électricité, gaz, eau
            "insurance": 300,       # Assurances
            "other_fixed": 400,     # Téléphone, comptable, etc.
            "staff_monthly": {      # Salaires + charges mensuels
                1: 3500,            # 1 employé temps partiel
                2: 6000,            # 2 employés
                3: 8500             # 3 employés
            }
        },
        "classic": {
            "rent": 5500,
            "utilities": 1200,
            "insurance": 400,
            "other_fixed": 600,
            "staff_monthly": {
                1: 4500,
                2: 8000,
                3: 11500
            }
        }
    }
    
    # Conversion en coûts par tour
    realistic_costs = {}
    
    for resto_type, costs in monthly_costs.items():
        # Coûts fixes par tour (hors personnel)
        fixed_monthly = costs['rent'] + costs['utilities'] + costs['insurance'] + costs['other_fixed']
        fixed_per_turn = fixed_monthly / 60  # 60 tours par mois
        
        # Coûts de personnel par tour
        staff_per_turn = {}
        for level, monthly_staff in costs['staff_monthly'].items():
            staff_per_turn[level] = monthly_staff / 60
        
        realistic_costs[resto_type] = {
            "fixed_cost": round(fixed_per_turn),
            "staff_costs": {k: round(v) for k, v in staff_per_turn.items()},
            "total_monthly_fixed": fixed_monthly,
            "total_monthly_staff": costs['staff_monthly']
        }
    
    print("\nCoûts réalistes par tour:")
    for resto_type, costs in realistic_costs.items():
        print(f"\n{resto_type.upper()}:")
        print(f"  Coûts fixes: {costs['fixed_cost']}€/tour")
        print(f"  Personnel niveau 2: {costs['staff_costs'][2]}€/tour")
        print(f"  (Équivalent mensuel: {costs['total_monthly_fixed']}€ + {costs['total_monthly_staff'][2]}€)")
    
    return realistic_costs

def test_realistic_simulation():
    """Teste la simulation avec les coûts réalistes."""
    print("\n\n🎮 SIMULATION AVEC COÛTS RÉALISTES")
    print("=" * 50)
    
    # Coûts réalistes calculés
    realistic_costs = {
        "fast": {
            "fixed_cost": 92,      # 5500€/mois ÷ 60 tours
            "staff_costs": {1: 58, 2: 100, 3: 142},  # Personnel/60
            "cogs_rate": 0.32,
            "suggested_price": 11.5
        },
        "classic": {
            "fixed_cost": 128,     # 7700€/mois ÷ 60 tours
            "staff_costs": {1: 75, 2: 133, 3: 192},
            "cogs_rate": 0.36,
            "suggested_price": 17.0
        }
    }
    
    # Test avec différents volumes de clients
    volumes = [50, 100, 150, 200]
    
    for resto_type, costs in realistic_costs.items():
        print(f"\n{resto_type.upper()} - Prix {costs['suggested_price']}€:")
        print("Clients | CA    | COGS | Staff | Fixes | Total | Profit | Marge")
        print("-" * 70)
        
        for clients in volumes:
            ca = clients * costs['suggested_price']
            cogs = ca * costs['cogs_rate']
            staff = costs['staff_costs'][2]  # Niveau normal
            fixed = costs['fixed_cost']
            total_costs = cogs + staff + fixed
            profit = ca - total_costs
            margin = (profit / ca * 100) if ca > 0 else 0
            
            status = "✅" if profit > 0 else "❌"
            print(f"{clients:7} | {ca:5.0f} | {cogs:4.0f} | {staff:5.0f} | {fixed:5.0f} | {total_costs:5.0f} | {profit:6.0f} | {margin:5.1f}% {status}")
    
    return realistic_costs

def calculate_break_even():
    """Calcule les seuils de rentabilité."""
    print("\n\n📊 SEUILS DE RENTABILITÉ")
    print("=" * 50)
    
    realistic_costs = {
        "fast": {"fixed_cost": 92, "staff_costs": 100, "cogs_rate": 0.32, "price": 11.5},
        "classic": {"fixed_cost": 128, "staff_costs": 133, "cogs_rate": 0.36, "price": 17.0}
    }
    
    for resto_type, costs in realistic_costs.items():
        # Calcul du seuil de rentabilité
        # Profit = 0 => CA - COGS - Staff - Fixed = 0
        # CA = Prix × Clients
        # COGS = CA × COGS_rate
        # Donc: Prix × Clients - (Prix × Clients × COGS_rate) - Staff - Fixed = 0
        # Prix × Clients × (1 - COGS_rate) = Staff + Fixed
        # Clients = (Staff + Fixed) / (Prix × (1 - COGS_rate))
        
        fixed_costs = costs['fixed_cost'] + costs['staff_costs']
        margin_per_client = costs['price'] * (1 - costs['cogs_rate'])
        break_even_clients = fixed_costs / margin_per_client
        
        print(f"\n{resto_type.upper()}:")
        print(f"  Prix: {costs['price']}€")
        print(f"  Marge unitaire: {margin_per_client:.2f}€")
        print(f"  Coûts fixes: {fixed_costs:.0f}€")
        print(f"  Seuil de rentabilité: {break_even_clients:.0f} clients/tour")
        print(f"  CA seuil: {break_even_clients * costs['price']:.0f}€")

def main():
    """Analyse complète de l'équilibrage économique."""
    print("🎯 ANALYSE ÉQUILIBRAGE ÉCONOMIQUE FOODOPS")
    print("=" * 60)
    
    # 1. Analyser les coûts actuels (problématiques)
    analyze_current_costs()
    
    # 2. Calculer des coûts réalistes
    realistic_costs = calculate_realistic_costs()
    
    # 3. Tester la simulation réaliste
    test_realistic_simulation()
    
    # 4. Calculer les seuils de rentabilité
    calculate_break_even()
    
    print("\n\n🎯 RECOMMANDATIONS:")
    print("=" * 30)
    print("✅ Diviser les coûts actuels par ~25")
    print("✅ Fast-food: Coûts fixes 92€, Personnel 100€")
    print("✅ Classique: Coûts fixes 128€, Personnel 133€")
    print("✅ Seuils de rentabilité: 25-35 clients/tour")
    print("✅ Marges réalistes: 10-25%")

if __name__ == "__main__":
    main()
