#!/usr/bin/env python3
"""
Lancement rapide - FoodOps Pro (version complète).
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Lance la version Pro complète."""
    print("🍽️ LANCEMENT FOODOPS PRO")
    print("=" * 40)
    print("Version Pro avec interface enrichie")
    print("Achat de fonds de commerce, décisions avancées")
    print("=" * 40)
    
    # Vérifier que nous sommes dans le bon dossier
    if not Path("src/foodops_pro").exists():
        print("❌ Erreur: Lancez ce script depuis le dossier racine du projet")
        sys.exit(1)
    
    # Lancer la version Pro
    try:
        cmd = [sys.executable, "-m", "src.foodops_pro.cli_pro"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Partie interrompue")

if __name__ == "__main__":
    main()
