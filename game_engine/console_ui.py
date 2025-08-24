"""
Interface console professionnelle
"""

import os
from decimal import Decimal
from typing import Any

from game_engine.scenario import Scenario

COLORS = {
    "header": "\033[1;36m",  # Cyan bold
    "success": "\033[1;32m",  # Green bold
    "warning": "\033[1;33m",  # Yellow bold
    "error": "\033[1;31m",  # Red bold
    "info": "\033[1;34m",  # Blue bold
    "reset": "\033[0m",  # Reset
    "bold": "\033[1m",  # Bold
    "dim": "\033[2m",  # Dim
}

WIDTH = 80


def print_box(content: list[str], title: str = "", style: str = "normal"):
    """Affiche un contenu dans une boîte."""
    color = COLORS.get(style, "")
    reset = COLORS["reset"]

    # Ligne du haut
    if title:
        title_line = f"║ {title.center(WIDTH - 4)} ║"
        print(f"{color}╔{'═' * (WIDTH - 2)}╗{reset}")
        print(f"{color}{title_line}{reset}")
        print(f"{color}╠{'═' * (WIDTH - 2)}╣{reset}")
    else:
        print(f"{color}╔{'═' * (WIDTH - 2)}╗{reset}")

    # Contenu
    for line in content:
        padded_line = f"║ {line:<{WIDTH - 4}} ║"
        print(f"{color}{padded_line}{reset}")

    # Ligne du bas
    print(f"{color}╚{'═' * (WIDTH - 2)}╝{reset}")


def clear_screen():
    """Efface l'écran."""
    os.system("cls" if os.name == "nt" else "clear")


def print_separator(char: str = "═", style: str = "normal"):
    """Affiche une ligne de séparation."""
    color = COLORS.get(style, "")
    reset = COLORS["reset"]
    print(f"{color}{char * WIDTH}{reset}")


def pause(self, message: str = "Appuyez sur Entrée pour continuer..."):
    """Pause avec message."""
    input(f"\n{self.colors['dim']}{message}{self.colors['reset']}")


def show_error(self, message: str):
    """Affiche un message d'erreur."""
    error_box = ["❌ ERREUR", "", message]
    print_box(error_box, style="error")


def show_success(self, message: str):
    """Affiche un message de succès."""
    success_box = ["✅ SUCCÈS", "", message]
    print_box(success_box, style="success")


def show_info(self, message: str):
    """Affiche un message d'information."""
    info_box = ["ℹ️ INFORMATION", "", message]
    print_box(info_box, style="info")


def show_admin(self):
    # Mode administrateur
    admin_info = [
        "👨‍🏫 MODE ADMINISTRATEUR ACTIVÉ",
        "",
        "Vous pouvez configurer tous les paramètres de la partie",
        "avant de la lancer pour vos étudiants.",
    ]
    self.print_box(admin_info, style="success")


def show_welcome_screen(self, scenario: Scenario):
    """Affiche l'écran d'accueil avec le scénario."""
    self.clear_screen()

    # Logo et titre
    logo = [
        "🍽️  FOODOPS PRO 2025  🍽️",
        "",
        "Simulateur de Gestion de Restaurant",
        "Version Éducative Professionnelle",
    ]
    self.print_box(logo, style="header")

    # Informations du scénario
    scenario_info = [
        f'📋 SCÉNARIO: "{scenario.name}"',
        "",
        "🎯 CONTEXTE:",
        *self._wrap_text(scenario.description, self.width - 8),
        "",
        "📊 PARAMÈTRES DE JEU:",
        f"• Durée: {scenario.turns} tours",
        f"• Demande de base: {scenario.base_demand} clients/tour",
        f"• Segments de marché: {len(scenario.segments)}",
        f"• Concurrents IA: {scenario.ai_competitors}",
        f"• Variabilité demande: ±{scenario.demand_noise:.0%}",
        "",
        "🏆 OBJECTIFS:",
        "• Maximiser votre trésorerie finale",
        "• Maintenir une marge bénéficiaire positive",
        "• Conquérir des parts de marché",
        "• Gérer efficacement vos ressources",
        "",
        "💡 CONSEILS:",
        "• Analysez vos segments de clientèle",
        "• Maîtrisez vos coûts matière et personnel",
        "• Adaptez votre stratégie à la concurrence",
        "• Investissez dans la qualité et l'efficacité",
    ]

    self.print_box(scenario_info, "BRIEFING DE MISSION", "info")

    # Segments de marché
    segments_info = ["ANALYSE DU MARCHÉ:"]
    for segment in scenario.segments:
        segments_info.extend(
            [
                f"👥 {segment.name.upper()} ({segment.share:.0%} du marché)",
                f"   Budget moyen: {segment.budget}€",
                f"   Sensibilité prix: {segment.price_sensitivity:.1f}/2.0",
                f"   Sensibilité qualité: {segment.quality_sensitivity:.1f}/2.0",
            ]
        )

    self.print_box(segments_info, style="warning")


def show_menu(self, title: str, options: list[str], allow_back: bool = True) -> int:
    """Affiche un menu et retourne le choix."""
    self.print_separator()
    print(f"\n{self.colors['bold']}{title}{self.colors['reset']}\n")

    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    if allow_back:
        print("  0. Retour")

    while True:
        print("Votre choix : ", end="", flush=True)
        choice = input().strip()
        if choice == "0" and allow_back:
            return 0

        choice_num = int(choice)
        if 1 <= choice_num <= len(options):
            return choice_num

        print(
            f"{self.colors['error']}Choix invalide. Veuillez entrer un nombre entre 1 et {len(options)}.{self.colors['reset']}"
        )


def get_input(
    self,
    prompt: str,
    input_type: type = str,
    min_val: Any = None,
    max_val: Any = None,
    default: Any = None,
) -> Any:
    """Récupère une entrée utilisateur avec validation."""
    while True:
        display_prompt = prompt
        if default is not None:
            display_prompt += f" (défaut: {default})"
        display_prompt += " : "

        print(display_prompt, end="", flush=True)
        user_input = input().strip()

        if not user_input and default is not None:
            return default

        if not user_input:
            print(f"{self.colors['error']}Entrée requise.{self.colors['reset']}")
            continue

        # Conversion de type
        if isinstance(input_type, int):
            value = int(user_input)
        elif isinstance(input_type, float) or isinstance(input_type, Decimal):
            value = Decimal(user_input.replace(",", "."))
        else:
            value = user_input

        # Validation des limites
        if min_val is not None and value < min_val:
            print(
                f"{self.colors['error']}Valeur trop petite. Minimum: {min_val}{self.colors['reset']}"
            )
            continue

        if max_val is not None and value > max_val:
            print(
                f"{self.colors['error']}Valeur trop grande. Maximum: {max_val}{self.colors['reset']}"
            )
            continue

        return value


# Utilitaires numériques simples (compat maintenue)
def ask_int(
    self,
    prompt: str,
    min_val: int = 0,
    max_val: int = 10**9,
    default: int | None = None,
) -> int:
    """Demande un entier avec bornes et défaut."""
    while True:
        display_prompt = prompt
        if default is not None:
            display_prompt += f" (défaut: {default})"
        display_prompt += ""
        print(display_prompt, end="", flush=True)
        text = input().strip()
        if not text and default is not None:
            return default
        value = int(text)
        if value < min_val or value > max_val:
            print(
                f"{self.colors['error']}Valeur hors bornes ({min_val}-{max_val}).{self.colors['reset']}"
            )
            continue
        return value


def ask_float(
    self,
    prompt: str,
    min_val: float = 0.0,
    max_val: float = 1e9,
    default: float | None = None,
) -> float:
    """Demande un flottant avec bornes et défaut."""
    while True:
        display_prompt = prompt
        if default is not None:
            display_prompt += f" (défaut: {default})"
        display_prompt += ""
        print(display_prompt, end="", flush=True)
        text = input().strip().replace(",", ".")
        if not text and default is not None:
            return default
        value = float(text)
        if value < min_val or value > max_val:
            print(
                f"{self.colors['error']}Valeur hors bornes ({min_val}-{max_val}).{self.colors['reset']}"
            )
            continue
        return value


def show_progress_bar(current: int, total: int, description: str = ""):
    """Affiche une barre de progression."""
    percentage = (current / total) * 100
    filled = int(percentage / 2)  # Barre sur 50 caractères
    bar = "█" * filled + "░" * (50 - filled)

    print(
        f"\r{description} [{bar}] {percentage:.1f}% ({current}/{total})",
        end="",
        flush=True,
    )

    if current == total:
        print()


def confirm(message: str, default: bool = False) -> bool:
    """Demande une confirmation oui/non."""
    suffix = " (O/n)" if default else " (o/N)"

    while True:
        print(f"{message}{suffix} : ", end="", flush=True)
        response = input().strip().lower()

        if not response:
            return default

        if response in ["o", "oui", "y", "yes"]:
            return True
        elif response in ["n", "non", "no"]:
            return False
        else:
            print(f"{COLORS['error']}Répondez par 'oui' ou 'non'.{COLORS['reset']}")
