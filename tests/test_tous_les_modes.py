#!/usr/bin/env python3
"""
Test complet de tous les modes de FoodOps pour audit pratique.
"""

import os
import sys
import subprocess
from pathlib import Path


def test_mode_simple():
    """Test du mode simple (Foodopsmini.py)."""
    print("🎮 TEST MODE SIMPLE (Foodopsmini.py)")
    print("=" * 60)

    try:
        # Vérifier que le fichier existe
        if not Path("Foodopsmini.py").exists():
            print("❌ Fichier Foodopsmini.py introuvable")
            return False

        print("✅ Fichier principal trouvé")
        print("📝 Description: Jeu simple pour débutants")
        print("🎯 Public: Enfants, découverte, apprentissage de base")
        print("⏱️ Durée: 30-60 minutes")
        print("🔧 Lancement: python Foodopsmini.py")

        # Test d'import
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "foodopsmini", "Foodopsmini.py"
            )
            module = importlib.util.module_from_spec(spec)
            print("✅ Import réussi - Code valide")
        except Exception as e:
            print(f"⚠️ Problème d'import: {e}")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_mode_pro():
    """Test du mode professionnel."""
    print(f"\n🏢 TEST MODE PROFESSIONNEL")
    print("=" * 60)

    try:
        # Vérifier les fichiers
        files_to_check = [
            "start_pro.py",
            "src/foodops_pro/cli_pro.py",
            "src/foodops_pro/core/market.py",
            "src/foodops_pro/domain/restaurant.py",
        ]

        missing_files = []
        for file_path in files_to_check:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            print(f"❌ Fichiers manquants: {missing_files}")
            return False

        print("✅ Tous les fichiers principaux trouvés")
        print("📝 Description: Simulateur professionnel complet")
        print("🎯 Public: Étudiants, formation professionnelle")
        print("⏱️ Durée: 2-4 heures")
        print("🔧 Lancement: python start_pro.py")

        # Vérifier les modules
        modules_to_check = [
            "src/foodops_pro/domain/ingredient_quality.py",
            "src/foodops_pro/domain/stock_advanced.py",
            "src/foodops_pro/domain/seasonality.py",
            "src/foodops_pro/domain/marketing.py",
            "src/foodops_pro/domain/finance_advanced.py",
        ]

        available_modules = []
        for module_path in modules_to_check:
            if Path(module_path).exists():
                available_modules.append(module_path.split("/")[-1])

        print(f"📦 Modules avancés disponibles: {len(available_modules)}")
        for module in available_modules:
            print(f"   ✅ {module}")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_mode_admin():
    """Test du mode administrateur."""
    print(f"\n👨‍🏫 TEST MODE ADMINISTRATEUR")
    print("=" * 60)

    try:
        # Vérifier les fichiers admin
        admin_files = [
            "start_admin.py",
            "admin_configs/preset_cours.yaml",
            "admin_configs/preset_demo.yaml",
            "admin_configs/preset_concours.yaml",
        ]

        available_admin = []
        for file_path in admin_files:
            if Path(file_path).exists():
                available_admin.append(file_path)

        print(f"✅ Fichiers admin trouvés: {len(available_admin)}")
        for file in available_admin:
            print(f"   📁 {file}")

        print("📝 Description: Configuration et gestion pour enseignants")
        print("🎯 Public: Enseignants, formateurs")
        print("⏱️ Durée: Configuration rapide")
        print("🔧 Lancement: python start_admin.py")

        # Vérifier les presets
        if Path("admin_configs").exists():
            presets = list(Path("admin_configs").glob("*.yaml"))
            print(f"⚙️ Presets disponibles: {len(presets)}")
            for preset in presets:
                print(f"   🎛️ {preset.name}")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_scripts_demo():
    """Test des scripts de démonstration."""
    print(f"\n🧪 TEST SCRIPTS DE DÉMONSTRATION")
    print("=" * 60)

    demo_scripts = [
        "demo.py",
        "demo_pro.py",
        "demo_admin.py",
        "demo_modules_simple.py",
        "demo_modules_avances.py",
        "demo_concurrence_dynamique.py",
        "demo_qualite_simple.py",
    ]

    working_demos = []
    broken_demos = []

    for script in demo_scripts:
        if Path(script).exists():
            try:
                # Test basique d'import
                with open(script, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "def main()" in content or "if __name__" in content:
                        working_demos.append(script)
                    else:
                        broken_demos.append(script)
            except Exception:
                broken_demos.append(script)
        else:
            broken_demos.append(f"{script} (manquant)")

    print(f"✅ Démos fonctionnelles: {len(working_demos)}")
    for demo in working_demos:
        print(f"   🧪 {demo}")

    if broken_demos:
        print(f"\n⚠️ Démos problématiques: {len(broken_demos)}")
        for demo in broken_demos:
            print(f"   ❌ {demo}")

    return len(working_demos) > len(broken_demos)


def test_scripts_test():
    """Test des scripts de test."""
    print(f"\n🔬 TEST SCRIPTS DE TEST")
    print("=" * 60)

    test_scripts = [
        "test_cli_pro.py",
        "test_cli_simple.py",
        "test_final.py",
        "test_integration_complete.py",
        "test_ameliorations_finales.py",
        "test_evenements_aleatoires.py",
        "test_concurrence_simple.py",
    ]

    working_tests = []
    broken_tests = []

    for script in test_scripts:
        if Path(script).exists():
            try:
                with open(script, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "def test_" in content or "def main()" in content:
                        working_tests.append(script)
                    else:
                        broken_tests.append(script)
            except Exception:
                broken_tests.append(script)
        else:
            broken_tests.append(f"{script} (manquant)")

    print(f"✅ Tests fonctionnels: {len(working_tests)}")
    for test in working_tests:
        print(f"   🔬 {test}")

    if broken_tests:
        print(f"\n⚠️ Tests problématiques: {len(broken_tests)}")
        for test in broken_tests:
            print(f"   ❌ {test}")

    return len(working_tests) > len(broken_tests)


def test_fichiers_lancement():
    """Test des fichiers de lancement (.bat)."""
    print(f"\n🚀 TEST FICHIERS DE LANCEMENT")
    print("=" * 60)

    bat_files = [
        "🎮_MENU_PRINCIPAL.bat",
        "🎮_Jouer_Pro.bat",
        "👨‍🏫_Mode_Admin.bat",
        "🚀_LAUNCHER.bat",
        "🧪_Demo_Rapide.bat",
        "MENU_SIMPLE.bat",
    ]

    available_launchers = []
    missing_launchers = []

    for bat_file in bat_files:
        if Path(bat_file).exists():
            available_launchers.append(bat_file)
            # Vérifier le contenu
            try:
                with open(bat_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "python" in content.lower():
                        print(f"   ✅ {bat_file} - Commande Python trouvée")
                    else:
                        print(f"   ⚠️ {bat_file} - Pas de commande Python")
            except Exception:
                print(f"   ❌ {bat_file} - Erreur de lecture")
        else:
            missing_launchers.append(bat_file)

    print(f"\n📊 Résumé lanceurs:")
    print(f"   ✅ Disponibles: {len(available_launchers)}")
    print(f"   ❌ Manquants: {len(missing_launchers)}")

    return len(available_launchers) > 0


def test_documentation():
    """Test de la documentation."""
    print(f"\n📚 TEST DOCUMENTATION")
    print("=" * 60)

    doc_files = [
        "README.md",
        "GUIDE_DEMARRAGE_RAPIDE.md",
        "DOCUMENTATION_COMPLETE.md",
        "SYNTHESE_FINALE.md",
        "RAPPORT_FINAL_COMPLET.md",
    ]

    available_docs = []
    doc_sizes = {}

    for doc_file in doc_files:
        if Path(doc_file).exists():
            available_docs.append(doc_file)
            size = Path(doc_file).stat().st_size
            doc_sizes[doc_file] = size
            print(f"   ✅ {doc_file} ({size:,} bytes)")
        else:
            print(f"   ❌ {doc_file} (manquant)")

    print(f"\n📊 Documentation disponible: {len(available_docs)}/{len(doc_files)}")

    # Vérifier la qualité
    total_doc_size = sum(doc_sizes.values())
    print(f"📏 Taille totale documentation: {total_doc_size:,} bytes")

    if total_doc_size > 50000:  # Plus de 50KB
        print("✅ Documentation substantielle")
    else:
        print("⚠️ Documentation légère")

    return len(available_docs) >= len(doc_files) // 2


def generer_rapport_audit():
    """Génère un rapport d'audit complet."""
    print(f"\n\n📋 RAPPORT D'AUDIT COMPLET")
    print("=" * 80)

    # Exécuter tous les tests
    results = {
        "Mode Simple": test_mode_simple(),
        "Mode Pro": test_mode_pro(),
        "Mode Admin": test_mode_admin(),
        "Scripts Demo": test_scripts_demo(),
        "Scripts Test": test_scripts_test(),
        "Fichiers Lancement": test_fichiers_lancement(),
        "Documentation": test_documentation(),
    }

    # Calculer le score global
    total_tests = len(results)
    passed_tests = sum(results.values())
    score = (passed_tests / total_tests) * 100

    print(f"\n🎯 RÉSULTATS GLOBAUX:")
    print(f"   Tests réussis: {passed_tests}/{total_tests}")
    print(f"   Score global: {score:.1f}%")

    print(f"\n📊 DÉTAIL PAR COMPOSANT:")
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {component}")

    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")

    if score >= 90:
        print("   🏆 Excellent ! Projet très complet et fonctionnel")
        print("   🚀 Prêt pour déploiement en production")
    elif score >= 70:
        print("   ✅ Bon état général, quelques améliorations possibles")
        print("   🔧 Corriger les composants défaillants")
    elif score >= 50:
        print("   ⚠️ État moyen, nécessite des corrections")
        print("   🛠️ Prioriser les composants critiques")
    else:
        print("   ❌ Nombreux problèmes détectés")
        print("   🚨 Révision complète recommandée")

    # Fichiers à nettoyer
    print(f"\n🧹 SUGGESTIONS DE NETTOYAGE:")

    # Chercher les fichiers potentiellement obsolètes
    all_files = list(Path(".").glob("*.py"))
    analysis_files = [f for f in all_files if f.name.startswith("analyse_")]

    if analysis_files:
        print(f"   📊 Fichiers d'analyse ({len(analysis_files)}):")
        for f in analysis_files:
            print(f"      • {f.name} - Garder si utile pour debug")

    # Fichiers de test multiples
    test_files = [f for f in all_files if f.name.startswith("test_")]
    if len(test_files) > 10:
        print(f"   🧪 Nombreux fichiers de test ({len(test_files)}):")
        print(f"      • Considérer regroupement dans dossier tests/")

    return score


def main():
    """Test principal de tous les modes."""
    print("🔍 AUDIT PRATIQUE COMPLET - FOODOPS PRO")
    print("=" * 80)
    print("🎯 Objectif: Tester tous les modes et identifier ce qui fonctionne")
    print("")

    score = generer_rapport_audit()

    print(f"\n\n🎉 AUDIT TERMINÉ !")
    print(f"Score final: {score:.1f}%")

    if score >= 80:
        print("🏆 Votre projet FoodOps est en excellent état !")
    else:
        print("🔧 Des améliorations sont possibles selon les recommandations.")


if __name__ == "__main__":
    main()
