#!/usr/bin/env python3
"""
Version simplifiée du jeu FoodOps Pro pour test.
"""

import sys
from decimal import Decimal
from src.foodops_pro.io.data_loader import DataLoader
from src.foodops_pro.core.market import MarketEngine
from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType

def main():
    print("🎮 FOODOPS PRO - VERSION SIMPLIFIÉE", flush=True)
    print("=" * 50, flush=True)
    
    try:
        # Chargement des données
        print("Chargement des données...", flush=True)
        loader = DataLoader()
        data = loader.load_all_data()
        print(f"✓ {len(data['ingredients'])} ingrédients, {len(data['recipes'])} recettes chargés", flush=True)
        
        # Configuration simple
        print("\n--- Configuration ---", flush=True)
        nom = input("Nom de votre restaurant : ").strip()
        if not nom:
            nom = "Mon Restaurant"
        
        print("Types de restaurant :", flush=True)
        print("1. Fast-food", flush=True)
        print("2. Classique", flush=True)
        print("3. Gastronomique", flush=True)
        print("4. Brasserie", flush=True)
        
        while True:
            try:
                choix = int(input("Votre choix (1-4) : "))
                if 1 <= choix <= 4:
                    types = [RestaurantType.FAST, RestaurantType.CLASSIC, 
                            RestaurantType.GASTRONOMIQUE, RestaurantType.BRASSERIE]
                    restaurant_type = types[choix - 1]
                    break
                print("Choix invalide.", flush=True)
            except ValueError:
                print("Veuillez entrer un nombre.", flush=True)
        
        # Création du restaurant
        restaurant = Restaurant(
            id="player",
            name=nom,
            type=restaurant_type,
            capacity_base=60,
            speed_service=Decimal("1.0"),
            staffing_level=2,
            cash=Decimal("20000")
        )
        
        # Menu simple
        restaurant.set_recipe_price("burger_classic", Decimal("12.50"))
        restaurant.set_recipe_price("pasta_bolognese", Decimal("16.00"))
        restaurant.activate_recipe("burger_classic")
        restaurant.activate_recipe("pasta_bolognese")
        
        # Concurrent IA
        concurrent = Restaurant(
            id="ai",
            name="Concurrent IA",
            type=RestaurantType.CLASSIC,
            capacity_base=50,
            speed_service=Decimal("1.0"),
            staffing_level=2
        )
        concurrent.set_recipe_price("burger_classic", Decimal("11.00"))
        concurrent.activate_recipe("burger_classic")
        
        restaurants = [restaurant, concurrent]
        
        print(f"\n✓ Restaurant '{nom}' créé ({restaurant_type.value})", flush=True)
        print(f"✓ Trésorerie initiale : {restaurant.cash}€", flush=True)
        print(f"✓ Capacité : {restaurant.capacity_current} couverts", flush=True)
        
        # Simulation de 3 tours
        scenario = data['scenario']
        market_engine = MarketEngine(scenario, random_seed=42)
        
        for tour in range(1, 4):
            print(f"\n{'='*50}", flush=True)
            print(f"TOUR {tour}/3", flush=True)
            print(f"{'='*50}", flush=True)
            
            # Décision simple
            print(f"\nTrésorerie actuelle : {restaurant.cash:.0f}€", flush=True)
            print("Niveau de staffing actuel : 2 (Normal)", flush=True)
            print("0=Fermé, 1=Léger, 2=Normal, 3=Renforcé", flush=True)
            
            while True:
                try:
                    staffing = int(input("Nouveau niveau de staffing : "))
                    if 0 <= staffing <= 3:
                        restaurant.staffing_level = staffing
                        break
                    print("Niveau invalide (0-3).", flush=True)
                except ValueError:
                    print("Veuillez entrer un nombre valide.", flush=True)
            
            # Simulation du marché
            results = market_engine.allocate_demand(restaurants, tour)
            
            # Affichage des résultats
            print(f"\n📊 Résultats du tour {tour}", flush=True)
            print("-" * 60, flush=True)
            
            for resto in restaurants:
                result = results[resto.id]
                utilization = (result.served_customers / result.capacity * 100) if result.capacity > 0 else 0
                
                print(f"{resto.name}:", flush=True)
                print(f"  Clients servis: {result.served_customers}/{result.capacity}", flush=True)
                print(f"  Utilisation: {utilization:.1f}%", flush=True)
                print(f"  Chiffre d'affaires: {result.revenue:.0f}€", flush=True)
                
                if resto.id == "player":
                    # Mise à jour trésorerie (profit approximatif)
                    profit = result.revenue * Decimal("0.15")
                    resto.update_cash(profit)
            
            if tour < 3:
                input("\nAppuyez sur Entrée pour continuer...")
        
        # Fin de partie
        print(f"\n🏁 FIN DE PARTIE", flush=True)
        print(f"Trésorerie finale : {restaurant.cash:.0f}€", flush=True)
        
        if restaurant.cash > Decimal("20000"):
            print("🎉 Félicitations ! Vous avez fait du profit !", flush=True)
        else:
            print("💪 Pas mal ! Continuez à vous améliorer !", flush=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 Partie interrompue. À bientôt !", flush=True)
    except Exception as e:
        print(f"\n❌ Erreur : {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
