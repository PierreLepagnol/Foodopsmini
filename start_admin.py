#!/usr/bin/env python3
"""
Lancement rapide - Mode Administrateur FoodOps Pro.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Lance le mode administrateur."""
    print("👨‍🏫 LANCEMENT MODE ADMINISTRATEUR")
    print("=" * 40)
    print("Interface de configuration pour professeurs")
    print("Configurez tous les paramètres de la partie")
    print("=" * 40)
    
    # Vérifier que nous sommes dans le bon dossier
    if not Path("src/foodops_pro").exists():
        print("❌ Erreur: Lancez ce script depuis le dossier racine du projet")
        sys.exit(1)
    
    # Lancer le mode admin
    try:
        cmd = [sys.executable, "-m", "src.foodops_pro.cli_pro", "--admin"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Configuration interrompue")

if __name__ == "__main__":
    main()
