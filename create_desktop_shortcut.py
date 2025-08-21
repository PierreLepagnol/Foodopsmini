#!/usr/bin/env python3
"""
Crée un raccourci sur le bureau pour FoodOps Pro.
"""

import os
import sys
from pathlib import Path


def create_desktop_shortcut():
    """Crée un raccourci sur le bureau Windows."""
    try:
        import winshell
        from win32com.client import Dispatch

        # Chemin du bureau
        desktop = winshell.desktop()

        # Chemin du projet
        project_path = Path.cwd()
        launcher_path = project_path / "🚀_LAUNCHER.bat"

        # Créer le raccourci
        shortcut_path = os.path.join(desktop, "🍽️ FoodOps Pro.lnk")

        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = str(launcher_path)
        shortcut.WorkingDirectory = str(project_path)
        shortcut.IconLocation = str(launcher_path)
        shortcut.Description = "FoodOps Pro - Simulateur de Gestion de Restaurant"
        shortcut.save()

        print("✅ Raccourci créé sur le bureau : 🍽️ FoodOps Pro")
        print("📍 Double-cliquez dessus pour lancer le jeu !")

    except ImportError:
        print("❌ Modules Windows manquants. Installation...")
        print("Exécutez : pip install pywin32 winshell")

        # Alternative : créer un fichier batch sur le bureau
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.join(os.path.expanduser("~"), "Bureau")  # Français

            if os.path.exists(desktop):
                project_path = Path.cwd()
                shortcut_content = f'''@echo off
cd /d "{project_path}"
call "🚀_LAUNCHER.bat"
'''
                shortcut_path = os.path.join(desktop, "🍽️ FoodOps Pro.bat")

                with open(shortcut_path, "w", encoding="utf-8") as f:
                    f.write(shortcut_content)

                print("✅ Raccourci alternatif créé sur le bureau")
                print("📍 Fichier : 🍽️ FoodOps Pro.bat")
            else:
                print("❌ Bureau non trouvé")

        except Exception as e:
            print(f"❌ Erreur création raccourci : {e}")

    except Exception as e:
        print(f"❌ Erreur : {e}")


def main():
    """Point d'entrée principal."""
    print("🚀 CRÉATION RACCOURCI FOODOPS PRO")
    print("=" * 40)

    if sys.platform != "win32":
        print("❌ Ce script est conçu pour Windows uniquement")
        return

    create_desktop_shortcut()

    print("\n💡 Autres façons de lancer le jeu :")
    print("  • Double-clic sur 🚀_LAUNCHER.bat")
    print("  • Double-clic sur 🎮_Jouer_Pro.bat")
    print("  • Ouvrir launcher.html dans le navigateur")

    input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()
