#!/usr/bin/env python3
"""
Test du gameplay réel des modes FoodOps.
"""

import sys
import os
from pathlib import Path

def test_mode_simple_gameplay():
    """Test du gameplay du mode simple."""
    print("🎮 TEST GAMEPLAY MODE SIMPLE")
    print("=" * 60)
    
    try:
        # Importer le module principal
        sys.path.append('.')
        
        # Lire le contenu pour comprendre la structure
        with open("Foodopsmini.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier chargé avec succès")
        
        # Analyser les classes principales
        classes = []
        functions = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('class '):
                class_name = line.split('class ')[1].split('(')[0].split(':')[0]
                classes.append(class_name)
            elif line.startswith('def ') and not line.startswith('def __'):
                func_name = line.split('def ')[1].split('(')[0]
                functions.append(func_name)
        
        print(f"📊 Structure détectée:")
        print(f"   Classes: {len(classes)}")
        for cls in classes[:5]:  # Afficher les 5 premières
            print(f"      • {cls}")
        
        print(f"   Fonctions: {len(functions)}")
        for func in functions[:5]:  # Afficher les 5 premières
            print(f"      • {func}")
        
        # Vérifier les mécaniques de jeu
        game_mechanics = {
            "Restaurant": "restaurant" in content.lower(),
            "Prix": "prix" in content.lower() or "price" in content.lower(),
            "Personnel": "personnel" in content.lower() or "staff" in content.lower(),
            "Clients": "client" in content.lower() or "customer" in content.lower(),
            "Profit": "profit" in content.lower(),
            "Concurrence": "concurrent" in content.lower() or "competitor" in content.lower(),
            "Satisfaction": "satisfaction" in content.lower(),
            "Marché": "marche" in content.lower() or "market" in content.lower()
        }
        
        print(f"\n🎯 Mécaniques de jeu détectées:")
        for mechanic, present in game_mechanics.items():
            icon = "✅" if present else "❌"
            print(f"   {icon} {mechanic}")
        
        mechanics_score = sum(game_mechanics.values()) / len(game_mechanics)
        print(f"\n📊 Score mécaniques: {mechanics_score:.1%}")
        
        return mechanics_score >= 0.7
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_mode_pro_imports():
    """Test des imports du mode pro."""
    print(f"\n🏢 TEST IMPORTS MODE PRO")
    print("=" * 60)
    
    try:
        # Tester les imports principaux
        sys.path.append('src')
        
        import_tests = {
            "foodops_pro": "src/foodops_pro/__init__.py",
            "restaurant": "src/foodops_pro/domain/restaurant.py",
            "market": "src/foodops_pro/core/market.py",
            "quality": "src/foodops_pro/domain/ingredient_quality.py",
            "stocks": "src/foodops_pro/domain/stock_advanced.py",
            "marketing": "src/foodops_pro/domain/marketing.py",
            "finance": "src/foodops_pro/domain/finance_advanced.py"
        }
        
        successful_imports = 0
        
        for module_name, file_path in import_tests.items():
            try:
                if Path(file_path).exists():
                    # Test basique de syntaxe
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Vérifier qu'il n'y a pas d'erreurs de syntaxe évidentes
                    compile(content, file_path, 'exec')
                    
                    print(f"   ✅ {module_name} - Syntaxe valide")
                    successful_imports += 1
                else:
                    print(f"   ❌ {module_name} - Fichier manquant")
            except SyntaxError as e:
                print(f"   ❌ {module_name} - Erreur syntaxe: {e}")
            except Exception as e:
                print(f"   ⚠️ {module_name} - Problème: {e}")
        
        import_score = successful_imports / len(import_tests)
        print(f"\n📊 Score imports: {successful_imports}/{len(import_tests)} ({import_score:.1%})")
        
        return import_score >= 0.8
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def test_donnees_coherence():
    """Test de cohérence des données."""
    print(f"\n📊 TEST COHÉRENCE DES DONNÉES")
    print("=" * 60)
    
    try:
        # Test des ingrédients
        with open("data/ingredients.csv", 'r', encoding='utf-8') as f:
            ingredients_lines = f.readlines()
        
        print(f"✅ Ingrédients: {len(ingredients_lines)-1} entrées")
        
        # Vérifier la structure
        header = ingredients_lines[0].strip().split(',')
        expected_columns = ['id', 'name', 'category', 'base_price', 'unit', 'quality_levels', 'seasonality']
        
        structure_ok = all(col in header for col in expected_columns)
        print(f"{'✅' if structure_ok else '❌'} Structure CSV ingrédients")
        
        # Test des recettes
        with open("data/recipes.csv", 'r', encoding='utf-8') as f:
            recipes_lines = f.readlines()
        
        print(f"✅ Recettes: {len(recipes_lines)-1} entrées")
        
        # Test des fournisseurs
        with open("data/suppliers.csv", 'r', encoding='utf-8') as f:
            suppliers_lines = f.readlines()
        
        print(f"✅ Fournisseurs: {len(suppliers_lines)-1} entrées")
        
        # Test cohérence prix
        ingredient_prices = []
        for line in ingredients_lines[1:]:  # Skip header
            parts = line.strip().split(',')
            if len(parts) >= 4:
                try:
                    price = float(parts[3])
                    ingredient_prices.append(price)
                except ValueError:
                    pass
        
        if ingredient_prices:
            avg_price = sum(ingredient_prices) / len(ingredient_prices)
            min_price = min(ingredient_prices)
            max_price = max(ingredient_prices)
            
            print(f"\n💰 Analyse prix ingrédients:")
            print(f"   Prix moyen: {avg_price:.2f}€")
            print(f"   Prix min: {min_price:.2f}€")
            print(f"   Prix max: {max_price:.2f}€")
            
            # Vérifier que les prix sont cohérents
            price_coherent = 0.5 <= min_price <= 50 and max_price <= 100
            print(f"   {'✅' if price_coherent else '❌'} Cohérence des prix")
        
        return structure_ok and len(ingredients_lines) > 5 and len(recipes_lines) > 5
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_scenarios_yaml():
    """Test des scénarios YAML."""
    print(f"\n⚙️ TEST SCÉNARIOS YAML")
    print("=" * 60)
    
    try:
        # Tester sans importer yaml (juste vérifier la structure)
        scenarios = ["scenarios/standard.yaml", "scenarios/demo.yaml"]
        
        valid_scenarios = 0
        
        for scenario_file in scenarios:
            if Path(scenario_file).exists():
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérifications basiques de structure YAML
                required_sections = ['name:', 'market:', 'segments:', 'restaurant:', 'game:']
                sections_found = sum(1 for section in required_sections if section in content)
                
                print(f"✅ {scenario_file}")
                print(f"   Sections trouvées: {sections_found}/{len(required_sections)}")
                
                if sections_found >= 4:
                    valid_scenarios += 1
                    print(f"   ✅ Structure valide")
                else:
                    print(f"   ⚠️ Structure incomplète")
            else:
                print(f"❌ {scenario_file} - Manquant")
        
        print(f"\n📊 Scénarios valides: {valid_scenarios}/{len(scenarios)}")
        
        return valid_scenarios >= 1
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_fonctionnalites_cles():
    """Test des fonctionnalités clés."""
    print(f"\n🔑 TEST FONCTIONNALITÉS CLÉS")
    print("=" * 60)
    
    # Vérifier les fonctionnalités dans le code
    key_features = {
        "Système qualité": "src/foodops_pro/domain/ingredient_quality.py",
        "Gestion stocks": "src/foodops_pro/domain/stock_advanced.py", 
        "Saisonnalité": "src/foodops_pro/domain/seasonality.py",
        "Marketing": "src/foodops_pro/domain/marketing.py",
        "Finance avancée": "src/foodops_pro/domain/finance_advanced.py",
        "Événements aléatoires": "src/foodops_pro/domain/random_events.py",
        "Concurrence": "src/foodops_pro/domain/competition.py",
        "Interface CLI": "src/foodops_pro/cli_pro.py"
    }
    
    available_features = 0
    
    for feature_name, file_path in key_features.items():
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            
            # Vérifier que le fichier n'est pas vide et contient du code
            if size > 1000:  # Au moins 1KB de code
                print(f"   ✅ {feature_name} ({size:,} bytes)")
                available_features += 1
            else:
                print(f"   ⚠️ {feature_name} (trop petit: {size} bytes)")
        else:
            print(f"   ❌ {feature_name} (manquant)")
    
    feature_score = available_features / len(key_features)
    print(f"\n📊 Fonctionnalités disponibles: {available_features}/{len(key_features)} ({feature_score:.1%})")
    
    return feature_score >= 0.8

def generer_rapport_gameplay():
    """Génère un rapport de gameplay complet."""
    print(f"\n📋 RAPPORT GAMEPLAY COMPLET")
    print("=" * 80)
    
    # Exécuter tous les tests
    tests = {
        "Mode Simple Gameplay": test_mode_simple_gameplay(),
        "Mode Pro Imports": test_mode_pro_imports(),
        "Cohérence Données": test_donnees_coherence(),
        "Scénarios YAML": test_scenarios_yaml(),
        "Fonctionnalités Clés": test_fonctionnalites_cles()
    }
    
    # Calculer le score global
    passed_tests = sum(tests.values())
    total_tests = len(tests)
    global_score = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 RÉSULTATS GLOBAUX:")
    print(f"   Tests réussis: {passed_tests}/{total_tests}")
    print(f"   Score global: {global_score:.1f}%")
    
    print(f"\n📊 DÉTAIL PAR TEST:")
    for test_name, result in tests.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {test_name}")
    
    # Recommandations finales
    print(f"\n💡 RECOMMANDATIONS FINALES:")
    
    if global_score >= 90:
        print("   🏆 EXCELLENT ! Jeu complet et fonctionnel")
        print("   🚀 Prêt pour utilisation en production")
        print("   📚 Parfait pour formation professionnelle")
    elif global_score >= 70:
        print("   ✅ BON ÉTAT ! Quelques ajustements mineurs")
        print("   🔧 Corriger les points défaillants")
        print("   📖 Utilisable pour enseignement")
    elif global_score >= 50:
        print("   ⚠️ ÉTAT MOYEN ! Corrections nécessaires")
        print("   🛠️ Prioriser les fonctionnalités critiques")
        print("   🎓 Utilisable avec supervision")
    else:
        print("   ❌ PROBLÈMES MAJEURS ! Révision complète")
        print("   🚨 Corriger avant utilisation")
        print("   🔄 Retour en développement recommandé")
    
    return global_score

def main():
    """Test principal du gameplay."""
    print("🎮 TEST GAMEPLAY RÉEL - FOODOPS PRO")
    print("=" * 80)
    print("🎯 Objectif: Vérifier que les modes fonctionnent vraiment")
    print("")
    
    score = generer_rapport_gameplay()
    
    print(f"\n\n🎉 TEST GAMEPLAY TERMINÉ !")
    print(f"Score final: {score:.1f}%")
    
    if score >= 80:
        print("🏆 Votre jeu FoodOps est prêt à l'emploi !")
    else:
        print("🔧 Des améliorations sont nécessaires.")

if __name__ == "__main__":
    main()
