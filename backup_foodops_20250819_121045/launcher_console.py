#!/usr/bin/env python3
"""
Launcher console interactif pour FoodOps Pro.
Ouvre vraiment les jeux dans de nouvelles consoles !
"""

import subprocess
import sys
import os
from pathlib import Path


def clear_screen():
    """Efface l'écran."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    """Affiche l'en-tête du launcher."""
    print("🍽️" + "=" * 50 + "🍽️")
    print("           FOODOPS PRO - LAUNCHER CONSOLE")
    print("🍽️" + "=" * 50 + "🍽️")
    print()


def print_menu():
    """Affiche le menu principal."""
    print("🎮 CHOISISSEZ VOTRE MODE DE JEU :")
    print()
    print("  1. 🍽️  Jouer Pro (Version complète)")
    print("      → Fonds de commerce, décisions avancées, rapports")
    print()
    print("  2. 👨‍🏫  Mode Administrateur (Professeurs)")
    print("      → Configuration de partie, presets, paramètres")
    print()
    print("  3. 🧪  Démonstration Rapide")
    print("      → Aperçu des fonctionnalités en 2 minutes")
    print()
    print("  4. 🎮  Version Classique")
    print("      → Jeu simple et rapide")
    print()
    print("  5. 📊  Voir les démos techniques")
    print("      → Chargement données, calculs, marché")
    print()
    print("  0. ❌  Quitter")
    print()


def launch_in_new_console(command, title="FoodOps Pro"):
    """Lance une commande dans une nouvelle console."""
    try:
        if sys.platform == "win32":
            # Windows - Nouvelle fenêtre cmd
            full_command = f'start "{title}" cmd /k "cd /d {Path.cwd()} && {command}"'
            subprocess.run(full_command, shell=True)
            print(f"✅ {title} lancé dans une nouvelle console !")
        else:
            # Linux/Mac - Nouveau terminal
            subprocess.Popen(
                [
                    "gnome-terminal",
                    "--",
                    "bash",
                    "-c",
                    f"cd {Path.cwd()} && {command}; read",
                ]
            )
            print(f"✅ {title} lancé dans un nouveau terminal !")
    except Exception as e:
        print(f"❌ Erreur lors du lancement : {e}")
        print(f"💡 Lancez manuellement : {command}")


def main():
    """Boucle principale du launcher."""
    while True:
        clear_screen()
        print_header()
        print_menu()

        try:
            choice = input("👉 Votre choix (0-5) : ").strip()

            if choice == "0":
                print("\n👋 Au revoir ! Merci d'avoir utilisé FoodOps Pro !")
                break

            elif choice == "1":
                print("\n🍽️ Lancement de FoodOps Pro...")
                launch_in_new_console(
                    "python start_pro.py", "FoodOps Pro - Version Complète"
                )

            elif choice == "2":
                print("\n👨‍🏫 Lancement du Mode Administrateur...")
                launch_in_new_console(
                    "python start_admin.py", "FoodOps Pro - Mode Admin"
                )

            elif choice == "3":
                print("\n🧪 Lancement de la Démonstration...")
                launch_in_new_console("python demo_pro.py", "FoodOps Pro - Démo")

            elif choice == "4":
                print("\n🎮 Lancement de la Version Classique...")
                launch_in_new_console(
                    "python -m src.foodops_pro.cli", "FoodOps Pro - Classique"
                )

            elif choice == "5":
                print("\n📊 Lancement des Démos Techniques...")
                print("  a. Démo classique (chargement, coûts)")
                print("  b. Démo Pro (UI, commerce, KPIs)")
                demo_choice = input("👉 Votre choix (a/b) : ").strip().lower()

                if demo_choice == "a":
                    launch_in_new_console(
                        "python demo.py", "FoodOps Pro - Démo Classique"
                    )
                elif demo_choice == "b":
                    launch_in_new_console(
                        "python demo_pro.py", "FoodOps Pro - Démo Pro"
                    )
                else:
                    print("❌ Choix invalide")

            else:
                print("❌ Choix invalide. Utilisez 0-5.")

            if choice != "0":
                input("\n📱 Appuyez sur Entrée pour revenir au menu...")

        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {e}")
            input("📱 Appuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    # Vérifier qu'on est dans le bon dossier
    if not Path("src/foodops_pro").exists():
        print("❌ Erreur : Lancez ce script depuis le dossier racine de FoodOps Pro")
        print("📁 Dossier actuel :", Path.cwd())
        input("📱 Appuyez sur Entrée pour quitter...")
        sys.exit(1)

    main()
