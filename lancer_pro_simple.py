#!/usr/bin/env python3
"""
Lanceur simplifié pour FoodOps Pro.
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Lance FoodOps Pro de manière simplifiée."""
    print("🍽️ FOODOPS PRO - VERSION SIMPLIFIÉE")
    print("=" * 50)
    print("🎯 Simulateur de gestion de restaurant professionnel")
    print("📚 Parfait pour formation et apprentissage")
    print("")
    
    try:
        # Import du module principal
        from foodops_pro.cli_pro import main as cli_main
        
        print("✅ Modules chargés avec succès")
        print("🚀 Lancement du jeu...")
        print("")
        
        # Lancer le jeu
        cli_main()
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("")
        print("🔧 Solutions possibles:")
        print("   1. Installer les dépendances: pip install pyyaml")
        print("   2. Vérifier que tous les fichiers sont présents")
        print("   3. Utiliser le mode simple: python Foodopsmini.py")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("")
        print("💡 Essayez le mode simple: python Foodopsmini.py")

if __name__ == "__main__":
    main()
