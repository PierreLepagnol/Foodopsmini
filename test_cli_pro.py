#!/usr/bin/env python3
"""
Test du nouveau CLI professionnel FoodOps Pro.
"""

def test_imports():
    """Test des imports des nouveaux modules."""
    print("=== TEST DES IMPORTS ===")
    
    try:
        from src.foodops_pro.ui.console_ui import ConsoleUI
        print("✅ ConsoleUI importé")
        
        from src.foodops_pro.admin.admin_config import AdminConfigManager
        print("✅ AdminConfigManager importé")
        
        from src.foodops_pro.domain.commerce import CommerceManager
        print("✅ CommerceManager importé")
        
        from src.foodops_pro.ui.financial_reports import FinancialReports
        print("✅ FinancialReports importé")
        
        from src.foodops_pro.ui.decision_menu import DecisionMenu
        print("✅ DecisionMenu importé")
        
        from src.foodops_pro.cli_pro import FoodOpsProGame
        print("✅ FoodOpsProGame importé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_console_ui():
    """Test de l'interface console."""
    print("\n=== TEST CONSOLE UI ===")
    
    try:
        from src.foodops_pro.ui.console_ui import ConsoleUI
        
        ui = ConsoleUI()
        print("✅ ConsoleUI créé")
        
        # Test d'affichage de boîte
        test_content = [
            "Ceci est un test",
            "de l'affichage en boîte",
            "avec du contenu multiligne"
        ]
        
        print("\nTest d'affichage:")
        ui.print_box(test_content, "TEST", "info")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur ConsoleUI: {e}")
        return False

def test_commerce_manager():
    """Test du gestionnaire de commerce."""
    print("\n=== TEST COMMERCE MANAGER ===")
    
    try:
        from src.foodops_pro.domain.commerce import CommerceManager
        from decimal import Decimal
        
        manager = CommerceManager()
        print("✅ CommerceManager créé")
        
        # Test de récupération des emplacements
        all_locations = manager.get_available_locations(Decimal("100000"))
        print(f"✅ {len(all_locations)} emplacements disponibles")
        
        # Test avec budget limité
        budget_locations = manager.get_available_locations(Decimal("50000"))
        print(f"✅ {len(budget_locations)} emplacements avec budget 50k€")
        
        # Affichage d'un exemple
        if all_locations:
            location = all_locations[0]
            print(f"\nExemple d'emplacement:")
            print(f"  - Nom: {location.name}")
            print(f"  - Prix: {location.price}€")
            print(f"  - Taille: {location.size} couverts")
            print(f"  - Loyer: {location.rent_monthly}€/mois")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur CommerceManager: {e}")
        return False

def test_financial_reports():
    """Test des rapports financiers."""
    print("\n=== TEST RAPPORTS FINANCIERS ===")
    
    try:
        from src.foodops_pro.ui.financial_reports import FinancialReports
        from src.foodops_pro.ui.console_ui import ConsoleUI
        from src.foodops_pro.domain.restaurant import Restaurant, RestaurantType
        from src.foodops_pro.core.ledger import Ledger
        from decimal import Decimal
        
        ui = ConsoleUI()
        reports = FinancialReports(ui)
        print("✅ FinancialReports créé")
        
        # Création d'un restaurant de test
        restaurant = Restaurant(
            id="test",
            name="Restaurant Test",
            type=RestaurantType.CLASSIC,
            capacity_base=50,
            speed_service=Decimal("1.0"),
            cash=Decimal("25000"),
            rent_monthly=Decimal("3000"),
            fixed_costs_monthly=Decimal("1500")
        )
        
        ledger = Ledger()
        print("✅ Restaurant et Ledger de test créés")
        
        # Test de calcul de métriques (sans affichage complet)
        metrics = reports._calculate_detailed_metrics(restaurant, {}, {})
        print(f"✅ Métriques calculées: {len(metrics)} indicateurs")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur FinancialReports: {e}")
        return False

def test_game_initialization():
    """Test d'initialisation du jeu."""
    print("\n=== TEST INITIALISATION JEU ===")
    
    try:
        from src.foodops_pro.cli_pro import FoodOpsProGame
        
        print("Initialisation du jeu (peut prendre quelques secondes)...")
        game = FoodOpsProGame(admin_mode=False)
        print("✅ Jeu initialisé avec succès")
        
        print(f"✅ Scénario chargé: {game.scenario.name}")
        print(f"✅ {len(game.ingredients)} ingrédients disponibles")
        print(f"✅ {len(game.recipes)} recettes disponibles")
        print(f"✅ {len(game.commerce_manager.available_locations)} emplacements de commerce")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test principal."""
    print("🎮 TEST DU NOUVEAU FOODOPS PRO")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_console_ui,
        test_commerce_manager,
        test_financial_reports,
        test_game_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS PASSENT !")
        print("\n🚀 Le nouveau FoodOps Pro est prêt !")
        print("\nPour jouer:")
        print("  python -m src.foodops_pro.cli_pro")
        print("\nPour le mode administrateur:")
        print("  python -m src.foodops_pro.cli_pro --admin")
    else:
        print(f"❌ {total - passed} test(s) échoué(s)")
        print("Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main()
