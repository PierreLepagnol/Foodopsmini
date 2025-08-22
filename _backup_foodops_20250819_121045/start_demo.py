#!/usr/bin/env python3
"""
Lancement rapide - Démo FoodOps Pro (3 tours, 1 joueur).
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Lance une démo rapide avec preset."""
    print("🎮 LANCEMENT DÉMO FOODOPS PRO")
    print("=" * 40)
    print("Configuration: 1 joueur, 3 tours, budget 40-60k€")
    print("IA: 2 concurrents moyens")
    print("=" * 40)

    # Vérifier que nous sommes dans le bon dossier
    if not Path("src/foodops_pro").exists():
        print("❌ Erreur: Lancez ce script depuis le dossier racine du projet")
        sys.exit(1)

    # Lancer le jeu Pro directement (sans preset pour l'instant)
    try:
        cmd = [sys.executable, "-m", "src.foodops_pro.cli_pro"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Démo interrompue")


if __name__ == "__main__":
    main()
