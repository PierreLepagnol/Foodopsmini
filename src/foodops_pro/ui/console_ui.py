"""
Interface console professionnelle pour FoodOps Pro.
"""

import os
import sys
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime

from ..domain.scenario import Scenario
from ..domain.restaurant import Restaurant, RestaurantType


class ConsoleUI:
    """Interface console avec design professionnel."""
    
    def __init__(self):
        self.width = 80
        self.colors = {
            'header': '\033[1;36m',    # Cyan bold
            'success': '\033[1;32m',   # Green bold
            'warning': '\033[1;33m',   # Yellow bold
            'error': '\033[1;31m',     # Red bold
            'info': '\033[1;34m',      # Blue bold
            'reset': '\033[0m',        # Reset
            'bold': '\033[1m',         # Bold
            'dim': '\033[2m'           # Dim
        }
    
    def clear_screen(self):
        """Efface l'écran."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_box(self, content: List[str], title: str = "", style: str = "normal"):
        """Affiche un contenu dans une boîte."""
        color = self.colors.get(style, '')
        reset = self.colors['reset']
        
        # Ligne du haut
        if title:
            title_line = f"║ {title.center(self.width - 4)} ║"
            print(f"{color}╔{'═' * (self.width - 2)}╗{reset}")
            print(f"{color}{title_line}{reset}")
            print(f"{color}╠{'═' * (self.width - 2)}╣{reset}")
        else:
            print(f"{color}╔{'═' * (self.width - 2)}╗{reset}")
        
        # Contenu
        for line in content:
            padded_line = f"║ {line:<{self.width - 4}} ║"
            print(f"{color}{padded_line}{reset}")
        
        # Ligne du bas
        print(f"{color}╚{'═' * (self.width - 2)}╝{reset}")
    
    def print_separator(self, char: str = "═", style: str = "normal"):
        """Affiche une ligne de séparation."""
        color = self.colors.get(style, '')
        reset = self.colors['reset']
        print(f"{color}{char * self.width}{reset}")
    
    def show_welcome_screen(self, scenario: Scenario, admin_mode: bool = False):
        """Affiche l'écran d'accueil avec le scénario."""
        self.clear_screen()
        
        # Logo et titre
        logo = [
            "🍽️  FOODOPS PRO 2025  🍽️",
            "",
            "Simulateur de Gestion de Restaurant",
            "Version Éducative Professionnelle"
        ]
        self.print_box(logo, style="header")
        
        print()
        
        # Informations du scénario
        scenario_info = [
            f"📋 SCÉNARIO: \"{scenario.name}\"",
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
            "• Investissez dans la qualité et l'efficacité"
        ]
        
        self.print_box(scenario_info, "BRIEFING DE MISSION", "info")
        
        print()
        
        # Segments de marché
        segments_info = ["ANALYSE DU MARCHÉ:"]
        for segment in scenario.segments:
            segments_info.extend([
                f"",
                f"👥 {segment.name.upper()} ({segment.share:.0%} du marché)",
                f"   Budget moyen: {segment.budget}€",
                f"   Sensibilité prix: {segment.price_sensitivity:.1f}/2.0",
                f"   Sensibilité qualité: {segment.quality_sensitivity:.1f}/2.0"
            ])
        
        self.print_box(segments_info, style="warning")
        
        print()
        
        # Mode administrateur
        if admin_mode:
            admin_info = [
                "👨‍🏫 MODE ADMINISTRATEUR ACTIVÉ",
                "",
                "Vous pouvez configurer tous les paramètres de la partie",
                "avant de la lancer pour vos étudiants."
            ]
            self.print_box(admin_info, style="success")
            print()
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Découpe un texte en lignes de largeur donnée."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= width:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def show_menu(self, title: str, options: List[str], allow_back: bool = True) -> int:
        """Affiche un menu et retourne le choix."""
        self.print_separator()
        print(f"\n{self.colors['bold']}{title}{self.colors['reset']}\n")
        
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        if allow_back:
            print(f"  0. Retour")
        
        print()
        
        while True:
            try:
                print("Votre choix : ", end="", flush=True)
                choice = input().strip()
                if choice == "0" and allow_back:
                    return 0
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return choice_num
                
                print(f"{self.colors['error']}Choix invalide. Veuillez entrer un nombre entre 1 et {len(options)}.{self.colors['reset']}")
                
            except ValueError:
                print(f"{self.colors['error']}Veuillez entrer un nombre valide.{self.colors['reset']}")
            except KeyboardInterrupt:
                print(f"\n{self.colors['warning']}Opération annulée.{self.colors['reset']}")
                return 0
    
    def get_input(self, prompt: str, input_type: type = str,
                  min_val: Any = None, max_val: Any = None,
                  default: Any = None) -> Any:
        """Récupère une entrée utilisateur avec validation."""
        while True:
            try:
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
                if input_type == int:
                    value = int(user_input)
                elif input_type == float or input_type == Decimal:
                    value = Decimal(user_input.replace(',', '.'))
                else:
                    value = user_input
                
                # Validation des limites
                if min_val is not None and value < min_val:
                    print(f"{self.colors['error']}Valeur trop petite. Minimum: {min_val}{self.colors['reset']}")
                    continue
                
                if max_val is not None and value > max_val:
                    print(f"{self.colors['error']}Valeur trop grande. Maximum: {max_val}{self.colors['reset']}")
                    continue
                
                return value
                
            except ValueError:
                print(f"{self.colors['error']}Format invalide. Attendu: {input_type.__name__}{self.colors['reset']}")
            except KeyboardInterrupt:
                print(f"\n{self.colors['warning']}Opération annulée.{self.colors['reset']}")
                return None
    
    def show_progress_bar(self, current: int, total: int, description: str = ""):
        """Affiche une barre de progression."""
        percentage = (current / total) * 100
        filled = int(percentage / 2)  # Barre sur 50 caractères
        bar = "█" * filled + "░" * (50 - filled)
        
        print(f"\r{description} [{bar}] {percentage:.1f}% ({current}/{total})", end="", flush=True)
        
        if current == total:
            print()  # Nouvelle ligne à la fin
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Demande une confirmation oui/non."""
        suffix = " (O/n)" if default else " (o/N)"
        
        while True:
            try:
                print(f"{message}{suffix} : ", end="", flush=True)
                response = input().strip().lower()
                
                if not response:
                    return default
                
                if response in ['o', 'oui', 'y', 'yes']:
                    return True
                elif response in ['n', 'non', 'no']:
                    return False
                else:
                    print(f"{self.colors['error']}Répondez par 'oui' ou 'non'.{self.colors['reset']}")
                    
            except KeyboardInterrupt:
                print(f"\n{self.colors['warning']}Opération annulée.{self.colors['reset']}")
                return False
    
    def pause(self, message: str = "Appuyez sur Entrée pour continuer..."):
        """Pause avec message."""
        try:
            input(f"\n{self.colors['dim']}{message}{self.colors['reset']}")
        except KeyboardInterrupt:
            pass
    
    def show_error(self, message: str):
        """Affiche un message d'erreur."""
        error_box = [
            "❌ ERREUR",
            "",
            message
        ]
        self.print_box(error_box, style="error")
    
    def show_success(self, message: str):
        """Affiche un message de succès."""
        success_box = [
            "✅ SUCCÈS",
            "",
            message
        ]
        self.print_box(success_box, style="success")
    
    def show_info(self, message: str):
        """Affiche un message d'information."""
        info_box = [
            "ℹ️ INFORMATION",
            "",
            message
        ]
        self.print_box(info_box, style="info")
