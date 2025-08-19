#!/usr/bin/env python3
"""
Script de nettoyage automatique du projet FoodOps.
Supprime les fichiers redondants et obsolètes identifiés dans l'audit.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def create_backup():
    """Crée une sauvegarde avant nettoyage."""
    backup_name = f"backup_foodops_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"🔄 Création de la sauvegarde : {backup_name}")
    
    # Créer le dossier de sauvegarde
    backup_path = Path(backup_name)
    backup_path.mkdir(exist_ok=True)
    
    # Lister les fichiers à sauvegarder
    files_to_backup = [
        # Fichiers de lancement redondants
        "🎮_Jouer_Pro.bat", "MENU_SIMPLE.bat", "🚀_LAUNCHER.bat",
        "launcher_console.py", "JOUER_MAINTENANT.bat",
        
        # Démos redondantes
        "demo_modules_simple.py", "demo_modules_avances.py",
        "demo_concurrence_dynamique.py", "demo_qualite_simple.py",
        "demo_interface_qualite.py", "demo_systeme_ingredients_avance.py",
        "demo_jeu_direct.py", "foodops_demo_direct.py",
        
        # Tests obsolètes
        "test_cli_pro.py", "test_cli_simple.py", "test_ameliorations_finales.py",
        "test_evenements_aleatoires.py", "test_concurrence_simple.py",
        "test_corrections.py", "test_gameplay_reel.py", "test_modes_pratique.py",
        "test_realisme_gameplay.py", "jeu_test.py", "jeu_test_simple.py",
        
        # Analyses redondantes
        "analyse_concurrence.py", "analyse_equilibrage.py",
        "analyse_equilibrage_economique.py", "analyse_leviers_decision.py",
        "analyse_systeme_ingredients.py", "audit_modules_manquants.py",
        
        # Documentation redondante
        "DOCUMENTATION_COMPLETE.md", "GUIDE_DEMARRAGE_RAPIDE.md",
        "RAPPORT_FINAL_COMPLET.md", "SYNTHESE_FINALE.md"
    ]
    
    backed_up = 0
    for file_name in files_to_backup:
        if Path(file_name).exists():
            shutil.copy2(file_name, backup_path / file_name)
            backed_up += 1
    
    print(f"✅ {backed_up} fichiers sauvegardés dans {backup_name}/")
    return backup_path

def phase1_lancement():
    """Phase 1 : Suppression des fichiers de lancement redondants."""
    print("\n📁 PHASE 1 : Nettoyage fichiers de lancement")
    print("-" * 50)
    
    files_to_remove = [
        "🎮_Jouer_Pro.bat",
        "MENU_SIMPLE.bat", 
        "🚀_LAUNCHER.bat",
        "launcher_console.py",
        "JOUER_MAINTENANT.bat"
    ]
    
    removed = 0
    for file_name in files_to_remove:
        if Path(file_name).exists():
            os.remove(file_name)
            print(f"  ❌ Supprimé : {file_name}")
            removed += 1
        else:
            print(f"  ⚠️  Introuvable : {file_name}")
    
    print(f"✅ Phase 1 terminée : {removed} fichiers supprimés")

def phase2_tests():
    """Phase 2 : Nettoyage des fichiers de test."""
    print("\n🔬 PHASE 2 : Nettoyage fichiers de test")
    print("-" * 50)
    
    files_to_remove = [
        "test_cli_pro.py", "test_cli_simple.py",
        "test_ameliorations_finales.py", "test_evenements_aleatoires.py",
        "test_concurrence_simple.py", "test_corrections.py",
        "test_gameplay_reel.py", "test_modes_pratique.py",
        "test_realisme_gameplay.py", "jeu_test.py", "jeu_test_simple.py"
    ]
    
    removed = 0
    for file_name in files_to_remove:
        if Path(file_name).exists():
            os.remove(file_name)
            print(f"  ❌ Supprimé : {file_name}")
            removed += 1
        else:
            print(f"  ⚠️  Introuvable : {file_name}")
    
    # Déplacer test_foodops_pro_complete.py vers tests/
    if Path("test_foodops_pro_complete.py").exists():
        Path("tests").mkdir(exist_ok=True)
        shutil.move("test_foodops_pro_complete.py", "tests/test_complete.py")
        print(f"  📁 Déplacé : test_foodops_pro_complete.py → tests/test_complete.py")
    
    print(f"✅ Phase 2 terminée : {removed} fichiers supprimés")

def phase3_demos():
    """Phase 3 : Nettoyage des fichiers de démonstration."""
    print("\n🧪 PHASE 3 : Nettoyage fichiers de démonstration")
    print("-" * 50)
    
    files_to_remove = [
        "demo_modules_simple.py", "demo_modules_avances.py",
        "demo_concurrence_dynamique.py", "demo_qualite_simple.py",
        "demo_interface_qualite.py", "demo_systeme_ingredients_avance.py",
        "demo_jeu_direct.py", "foodops_demo_direct.py"
    ]
    
    removed = 0
    for file_name in files_to_remove:
        if Path(file_name).exists():
            os.remove(file_name)
            print(f"  ❌ Supprimé : {file_name}")
            removed += 1
        else:
            print(f"  ⚠️  Introuvable : {file_name}")
    
    print(f"✅ Phase 3 terminée : {removed} fichiers supprimés")

def phase4_analyses():
    """Phase 4 : Nettoyage des fichiers d'analyse."""
    print("\n📊 PHASE 4 : Nettoyage fichiers d'analyse")
    print("-" * 50)
    
    files_to_remove = [
        "analyse_concurrence.py", "analyse_equilibrage.py",
        "analyse_equilibrage_economique.py", "analyse_leviers_decision.py",
        "analyse_systeme_ingredients.py", "audit_modules_manquants.py"
    ]
    
    removed = 0
    for file_name in files_to_remove:
        if Path(file_name).exists():
            os.remove(file_name)
            print(f"  ❌ Supprimé : {file_name}")
            removed += 1
        else:
            print(f"  ⚠️  Introuvable : {file_name}")
    
    print(f"✅ Phase 4 terminée : {removed} fichiers supprimés")

def phase5_documentation():
    """Phase 5 : Nettoyage de la documentation."""
    print("\n📚 PHASE 5 : Nettoyage documentation")
    print("-" * 50)
    
    files_to_remove = [
        "DOCUMENTATION_COMPLETE.md", "GUIDE_DEMARRAGE_RAPIDE.md",
        "RAPPORT_FINAL_COMPLET.md", "SYNTHESE_FINALE.md"
    ]
    
    removed = 0
    for file_name in files_to_remove:
        if Path(file_name).exists():
            os.remove(file_name)
            print(f"  ❌ Supprimé : {file_name}")
            removed += 1
        else:
            print(f"  ⚠️  Introuvable : {file_name}")
    
    print(f"✅ Phase 5 terminée : {removed} fichiers supprimés")

def rename_files():
    """Renomme les fichiers selon les conventions."""
    print("\n🔧 RENOMMAGE DES FICHIERS")
    print("-" * 50)
    
    if Path("Foodopsmini.py").exists():
        shutil.move("Foodopsmini.py", "foodops_mini.py")
        print("  📝 Renommé : Foodopsmini.py → foodops_mini.py")
    
    print("✅ Renommage terminé")

def show_final_structure():
    """Affiche la structure finale."""
    print("\n📁 STRUCTURE FINALE")
    print("-" * 50)
    
    important_files = [
        "🎮_MENU_PRINCIPAL.bat",
        "👨‍🏫_Mode_Admin.bat", 
        "🧪_Demo_Rapide.bat",
        "start_pro.py",
        "start_admin.py", 
        "start_demo.py",
        "foodops_mini.py",
        "FOODOPS_PRO_COMPLET.py",
        "demo.py",
        "demo_pro.py",
        "demo_admin.py",
        "README.md",
        "pyproject.toml"
    ]
    
    print("Fichiers principaux conservés :")
    for file_name in important_files:
        if Path(file_name).exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} (manquant)")

def main():
    """Fonction principale de nettoyage."""
    print("🧹 SCRIPT DE NETTOYAGE FOODOPS")
    print("=" * 50)
    print("Ce script va supprimer les fichiers redondants identifiés dans l'audit.")
    print("Une sauvegarde sera créée avant toute suppression.")
    print()
    
    # Demander confirmation
    response = input("Voulez-vous continuer ? (oui/non) : ").lower().strip()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Nettoyage annulé.")
        return
    
    try:
        # Créer sauvegarde
        backup_path = create_backup()
        
        # Exécuter les phases de nettoyage
        phase1_lancement()
        phase2_tests()
        phase3_demos()
        phase4_analyses()
        phase5_documentation()
        rename_files()
        
        # Afficher résultat
        show_final_structure()
        
        print("\n🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS !")
        print("=" * 50)
        print(f"📁 Sauvegarde disponible dans : {backup_path}")
        print("🎮 Vous pouvez maintenant utiliser : 🎮_MENU_PRINCIPAL.bat")
        print("📚 Consultez AUDIT_PROJET_FOODOPS.md pour plus de détails")
        
    except Exception as e:
        print(f"\n❌ ERREUR PENDANT LE NETTOYAGE : {e}")
        print("🔄 Restaurez depuis la sauvegarde si nécessaire")

if __name__ == "__main__":
    main()
