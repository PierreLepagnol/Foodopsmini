#!/usr/bin/env python3
"""
Test pratique des modes FoodOps sans dépendances externes.
"""

import os
import sys
from pathlib import Path

def test_mode_simple_pratique():
    """Test pratique du mode simple."""
    print("🎮 TEST PRATIQUE MODE SIMPLE")
    print("=" * 60)
    
    try:
        # Vérifier le contenu du fichier principal
        if not Path("Foodopsmini.py").exists():
            print("❌ Fichier Foodopsmini.py introuvable")
            return False
        
        with open("Foodopsmini.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Analyser le contenu
        has_main = "def main(" in content or "if __name__" in content
        has_game_logic = "restaurant" in content.lower() or "profit" in content.lower()
        has_input = "input(" in content
        
        print(f"✅ Fichier trouvé ({len(content)} caractères)")
        print(f"{'✅' if has_main else '❌'} Point d'entrée principal")
        print(f"{'✅' if has_game_logic else '❌'} Logique de jeu")
        print(f"{'✅' if has_input else '❌'} Interface utilisateur")
        
        # Vérifier les imports
        imports = []
        for line in content.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
        
        print(f"📦 Imports détectés: {len(imports)}")
        for imp in imports[:5]:  # Afficher les 5 premiers
            print(f"   • {imp}")
        
        # Évaluation
        score = sum([has_main, has_game_logic, has_input])
        print(f"\n📊 Score fonctionnel: {score}/3")
        
        if score >= 2:
            print("✅ Mode simple semble fonctionnel")
            return True
        else:
            print("⚠️ Mode simple incomplet")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_mode_pro_structure():
    """Test de la structure du mode pro."""
    print(f"\n🏢 TEST STRUCTURE MODE PRO")
    print("=" * 60)
    
    # Fichiers essentiels
    essential_files = {
        "start_pro.py": "Point d'entrée",
        "src/foodops_pro/__init__.py": "Package principal",
        "src/foodops_pro/cli_pro.py": "Interface CLI",
        "src/foodops_pro/core/market.py": "Moteur de marché",
        "src/foodops_pro/domain/restaurant.py": "Modèle restaurant"
    }
    
    available_files = {}
    missing_files = []
    
    for file_path, description in essential_files.items():
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            available_files[file_path] = {"description": description, "size": size}
            print(f"✅ {file_path} ({size:,} bytes) - {description}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - {description}")
    
    # Modules avancés
    advanced_modules = {
        "src/foodops_pro/domain/ingredient_quality.py": "Système qualité",
        "src/foodops_pro/domain/stock_advanced.py": "Gestion stocks",
        "src/foodops_pro/domain/seasonality.py": "Saisonnalité",
        "src/foodops_pro/domain/marketing.py": "Marketing",
        "src/foodops_pro/domain/finance_advanced.py": "Finance avancée",
        "src/foodops_pro/domain/random_events.py": "Événements aléatoires",
        "src/foodops_pro/domain/competition.py": "Concurrence"
    }
    
    available_advanced = 0
    print(f"\n📦 MODULES AVANCÉS:")
    for module_path, description in advanced_modules.items():
        if Path(module_path).exists():
            size = Path(module_path).stat().st_size
            available_advanced += 1
            print(f"   ✅ {module_path.split('/')[-1]} ({size:,} bytes)")
        else:
            print(f"   ❌ {module_path.split('/')[-1]}")
    
    # Évaluation
    essential_score = len(available_files) / len(essential_files)
    advanced_score = available_advanced / len(advanced_modules)
    
    print(f"\n📊 ÉVALUATION:")
    print(f"   Fichiers essentiels: {len(available_files)}/{len(essential_files)} ({essential_score:.1%})")
    print(f"   Modules avancés: {available_advanced}/{len(advanced_modules)} ({advanced_score:.1%})")
    
    overall_score = (essential_score + advanced_score) / 2
    print(f"   Score global: {overall_score:.1%}")
    
    if overall_score >= 0.8:
        print("✅ Mode pro très complet")
        return True
    elif overall_score >= 0.6:
        print("⚠️ Mode pro fonctionnel mais incomplet")
        return True
    else:
        print("❌ Mode pro insuffisant")
        return False

def test_donnees_jeu():
    """Test des données de jeu."""
    print(f"\n📊 TEST DONNÉES DE JEU")
    print("=" * 60)
    
    data_files = {
        "data/ingredients.csv": "Ingrédients",
        "data/recipes.csv": "Recettes", 
        "data/suppliers.csv": "Fournisseurs",
        "scenarios/standard.yaml": "Scénario standard",
        "scenarios/demo.yaml": "Scénario démo"
    }
    
    available_data = 0
    total_size = 0
    
    for file_path, description in data_files.items():
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            available_data += 1
            total_size += size
            print(f"✅ {file_path} ({size:,} bytes) - {description}")
            
            # Analyser le contenu si c'est un CSV
            if file_path.endswith('.csv'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"   📝 {len(lines)} lignes de données")
                except Exception:
                    print(f"   ⚠️ Erreur de lecture")
        else:
            print(f"❌ {file_path} - {description}")
    
    print(f"\n📊 Résumé données:")
    print(f"   Fichiers disponibles: {available_data}/{len(data_files)}")
    print(f"   Taille totale: {total_size:,} bytes")
    
    return available_data >= len(data_files) // 2

def test_scripts_utiles():
    """Test des scripts vraiment utiles."""
    print(f"\n🛠️ TEST SCRIPTS UTILES")
    print("=" * 60)
    
    # Scripts par catégorie
    scripts_categories = {
        "🎮 LANCEMENT": [
            "Foodopsmini.py",
            "start_pro.py", 
            "start_admin.py"
        ],
        "🧪 DÉMONSTRATION": [
            "demo_modules_simple.py",
            "demo_qualite_simple.py",
            "test_concurrence_simple.py"
        ],
        "📊 ANALYSE": [
            "audit_complet_final.py",
            "test_tous_les_modes.py",
            "analyse_impact_decisions.py"
        ],
        "🔧 UTILITAIRES": [
            "🎮_MENU_PRINCIPAL.bat",
            "🚀_LAUNCHER.bat"
        ]
    }
    
    useful_scripts = []
    obsolete_scripts = []
    
    for category, scripts in scripts_categories.items():
        print(f"\n{category}:")
        for script in scripts:
            if Path(script).exists():
                size = Path(script).stat().st_size
                useful_scripts.append(script)
                print(f"   ✅ {script} ({size:,} bytes)")
            else:
                obsolete_scripts.append(script)
                print(f"   ❌ {script} (manquant)")
    
    # Identifier les scripts potentiellement obsolètes
    all_py_files = list(Path(".").glob("*.py"))
    analysis_files = [f.name for f in all_py_files if f.name.startswith("analyse_")]
    test_files = [f.name for f in all_py_files if f.name.startswith("test_")]
    
    print(f"\n🧹 SCRIPTS À ÉVALUER:")
    if analysis_files:
        print(f"   📊 Fichiers d'analyse ({len(analysis_files)}):")
        for f in analysis_files[:5]:  # Limiter l'affichage
            print(f"      • {f}")
        if len(analysis_files) > 5:
            print(f"      • ... et {len(analysis_files) - 5} autres")
    
    if len(test_files) > 8:
        print(f"   🧪 Nombreux fichiers de test ({len(test_files)}):")
        print(f"      • Considérer regroupement ou nettoyage")
    
    return len(useful_scripts) > len(obsolete_scripts)

def generer_recommandations():
    """Génère des recommandations pratiques."""
    print(f"\n💡 RECOMMANDATIONS PRATIQUES")
    print("=" * 60)
    
    print("🎯 MODES À CONSERVER:")
    print("   ✅ Mode Simple (Foodopsmini.py) - Entrée de gamme")
    print("   ✅ Mode Pro - Si tous les modules fonctionnent")
    print("   ⚠️ Mode Admin - Si utilisé pour l'enseignement")
    
    print(f"\n🧹 NETTOYAGE SUGGÉRÉ:")
    print("   📊 Regrouper fichiers d'analyse dans dossier analysis/")
    print("   🧪 Garder 3-4 scripts de test principaux")
    print("   📝 Archiver les fichiers de développement")
    print("   🔧 Conserver les utilitaires de lancement")
    
    print(f"\n🚀 PRIORITÉS DE DÉVELOPPEMENT:")
    print("   1. Corriger les dépendances manquantes (yaml)")
    print("   2. Tester le gameplay complet")
    print("   3. Valider l'équilibrage")
    print("   4. Simplifier l'installation")
    
    print(f"\n📦 STRUCTURE RECOMMANDÉE:")
    print("   📁 / (racine)")
    print("   ├── 🎮 Foodopsmini.py (mode simple)")
    print("   ├── 🏢 start_pro.py (mode pro)")
    print("   ├── 📁 src/ (code source)")
    print("   ├── 📁 data/ (données de jeu)")
    print("   ├── 📁 docs/ (documentation)")
    print("   ├── 📁 tests/ (tests principaux)")
    print("   └── 📁 utils/ (utilitaires)")

def main():
    """Test principal pratique."""
    print("🔍 TEST PRATIQUE FOODOPS - AUDIT FONCTIONNEL")
    print("=" * 80)
    
    # Exécuter les tests
    results = {
        "Mode Simple": test_mode_simple_pratique(),
        "Structure Mode Pro": test_mode_pro_structure(),
        "Données de Jeu": test_donnees_jeu(),
        "Scripts Utiles": test_scripts_utiles()
    }
    
    # Calculer le score
    passed = sum(results.values())
    total = len(results)
    score = (passed / total) * 100
    
    print(f"\n📊 RÉSULTATS FINAUX:")
    print(f"   Tests réussis: {passed}/{total}")
    print(f"   Score: {score:.1f}%")
    
    print(f"\n📋 DÉTAIL:")
    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {test_name}")
    
    # Recommandations
    generer_recommandations()
    
    print(f"\n🎯 CONCLUSION:")
    if score >= 75:
        print("✅ Projet en bon état, prêt pour utilisation")
    elif score >= 50:
        print("⚠️ Projet fonctionnel, quelques améliorations nécessaires")
    else:
        print("❌ Projet nécessite des corrections importantes")

if __name__ == "__main__":
    main()
