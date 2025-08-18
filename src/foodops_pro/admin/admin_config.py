"""
Configuration administrateur pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from decimal import Decimal
from pathlib import Path
import yaml

from ..domain.scenario import Scenario, MarketSegment
from ..domain.restaurant import RestaurantType


@dataclass
class AdminSettings:
    """Configuration administrateur pour une partie."""
    
    # Informations générales
    session_name: str = "Session FoodOps Pro 2025"
    instructor_name: str = ""
    course_code: str = ""
    academic_year: str = "2025-2026"
    
    # Paramètres de jeu
    max_players: int = 4
    starting_budget_min: Decimal = Decimal("20000")
    starting_budget_max: Decimal = Decimal("1000000")
    allow_loans: bool = True
    max_loan_amount: Decimal = Decimal("50000")
    loan_interest_rate: Decimal = Decimal("0.045")
    
    # Durée et difficulté
    total_turns: int = 12
    turn_duration_description: str = "1 mois"
    ai_difficulty: str = "medium"  # easy, medium, hard
    ai_count: int = 2
    
    # Événements et réalisme
    enable_random_events: bool = True
    enable_seasonal_effects: bool = True
    enable_economic_cycles: bool = False
    event_frequency: Decimal = Decimal("0.15")  # 15% de chance par tour
    
    # Marché
    total_market_size: int = 500
    market_growth_rate: Decimal = Decimal("0.02")  # 2% par an
    competition_intensity: str = "normal"  # low, normal, high
    
    # Pédagogie
    show_competitor_details: bool = False
    enable_hints: bool = True
    auto_save: bool = True
    detailed_feedback: bool = True
    
    # Évaluation
    enable_scoring: bool = True
    scoring_criteria: Dict[str, Decimal] = field(default_factory=lambda: {
        "survival": Decimal("0.3"),      # 30% - Survie
        "profitability": Decimal("0.25"), # 25% - Rentabilité
        "growth": Decimal("0.20"),       # 20% - Croissance
        "efficiency": Decimal("0.15"),   # 15% - Efficacité
        "strategy": Decimal("0.10")      # 10% - Stratégie
    })
    
    # Restrictions
    restrict_restaurant_types: List[str] = field(default_factory=list)
    min_employees: int = 1
    max_employees: int = 10
    allow_price_changes: bool = True
    price_change_limit: Decimal = Decimal("0.20")  # ±20%
    
    # Commerce disponibles
    available_locations: List[str] = field(default_factory=lambda: [
        "centre_ville", "banlieue", "zone_commerciale", "quartier_etudiant"
    ])


class AdminConfigManager:
    """Gestionnaire de configuration administrateur."""
    
    def __init__(self, ui):
        self.ui = ui
        self.settings = AdminSettings()
    
    def configure_session(self) -> AdminSettings:
        """Interface de configuration complète pour l'administrateur."""
        self.ui.clear_screen()
        
        welcome = [
            "👨‍🏫 CONFIGURATION ADMINISTRATEUR",
            "",
            "Bienvenue dans l'interface de configuration FoodOps Pro.",
            "Vous pouvez personnaliser tous les aspects de la partie",
            "pour vos étudiants."
        ]
        self.ui.print_box(welcome, "MODE PROFESSEUR", "header")
        
        # Menu principal de configuration
        while True:
            self.ui.clear_screen()
            self._show_current_config()
            
            menu_options = [
                "📋 Informations de session",
                "🎮 Paramètres de jeu",
                "🏪 Fonds de commerce disponibles",
                "📊 Marché et concurrence",
                "🎯 Événements et réalisme",
                "📝 Évaluation et notation",
                "🔒 Restrictions et limites",
                "💾 Sauvegarder configuration",
                "▶️ Lancer la partie"
            ]
            
            choice = self.ui.show_menu("CONFIGURATION ADMINISTRATEUR", menu_options, allow_back=False)
            
            if choice == 1:
                self._configure_session_info()
            elif choice == 2:
                self._configure_game_params()
            elif choice == 3:
                self._configure_commerce_locations()
            elif choice == 4:
                self._configure_market()
            elif choice == 5:
                self._configure_events()
            elif choice == 6:
                self._configure_evaluation()
            elif choice == 7:
                self._configure_restrictions()
            elif choice == 8:
                self._save_configuration()
            elif choice == 9:
                if self._validate_configuration():
                    break
        
        return self.settings
    
    def _show_current_config(self):
        """Affiche la configuration actuelle."""
        config_summary = [
            f"📋 Session: {self.settings.session_name}",
            f"👨‍🏫 Professeur: {self.settings.instructor_name or 'Non défini'}",
            f"🎓 Cours: {self.settings.course_code or 'Non défini'}",
            "",
            f"👥 Joueurs max: {self.settings.max_players}",
            f"💰 Budget initial: {self.settings.starting_budget_min}€ - {self.settings.starting_budget_max}€",
            f"⏱️ Durée: {self.settings.total_turns} tours ({self.settings.turn_duration_description} chacun)",
            f"🤖 IA: {self.settings.ai_count} concurrent(s) - Difficulté {self.settings.ai_difficulty}",
            "",
            f"🎲 Événements aléatoires: {'✅' if self.settings.enable_random_events else '❌'}",
            f"📈 Effets saisonniers: {'✅' if self.settings.enable_seasonal_effects else '❌'}",
            f"📊 Notation automatique: {'✅' if self.settings.enable_scoring else '❌'}"
        ]
        
        self.ui.print_box(config_summary, "CONFIGURATION ACTUELLE", "info")
    
    def _configure_session_info(self):
        """Configure les informations de session."""
        self.ui.clear_screen()
        
        info = [
            "📋 INFORMATIONS DE SESSION",
            "",
            "Définissez les informations générales de votre cours."
        ]
        self.ui.print_box(info, style="header")
        
        self.settings.session_name = self.ui.get_input(
            "Nom de la session",
            default=self.settings.session_name
        )
        
        self.settings.instructor_name = self.ui.get_input(
            "Nom du professeur",
            default=self.settings.instructor_name
        )
        
        self.settings.course_code = self.ui.get_input(
            "Code du cours (ex: GEST301)",
            default=self.settings.course_code
        )
        
        self.settings.academic_year = self.ui.get_input(
            "Année académique",
            default=self.settings.academic_year
        )
        
        self.ui.show_success("Informations de session mises à jour.")
        self.ui.pause()
    
    def _configure_game_params(self):
        """Configure les paramètres de jeu."""
        self.ui.clear_screen()
        
        info = [
            "🎮 PARAMÈTRES DE JEU",
            "",
            "Définissez la durée, la difficulté et les règles de base."
        ]
        self.ui.print_box(info, style="header")
        
        self.settings.max_players = self.ui.get_input(
            "Nombre maximum de joueurs",
            int, min_val=1, max_val=8,
            default=self.settings.max_players
        )
        
        self.settings.total_turns = self.ui.get_input(
            "Nombre de tours",
            int, min_val=6, max_val=48,
            default=self.settings.total_turns
        )
        
        duration_options = ["1 semaine", "2 semaines", "1 mois", "1 trimestre", "6 mois"]
        duration_choice = self.ui.show_menu(
            "Durée représentée par chaque tour",
            duration_options
        )
        if duration_choice > 0:
            self.settings.turn_duration_description = duration_options[duration_choice - 1]
        
        self.settings.starting_budget_min = self.ui.get_input(
            "Budget initial minimum (€)",
            Decimal, min_val=Decimal("5000"),
            default=self.settings.starting_budget_min
        )
        
        self.settings.starting_budget_max = self.ui.get_input(
            "Budget initial maximum (€)",
            Decimal, min_val=self.settings.starting_budget_min,
            default=self.settings.starting_budget_max
        )
        
        self.settings.allow_loans = self.ui.confirm(
            "Autoriser les emprunts",
            default=self.settings.allow_loans
        )
        
        if self.settings.allow_loans:
            self.settings.max_loan_amount = self.ui.get_input(
                "Montant maximum d'emprunt (€)",
                Decimal, min_val=Decimal("10000"),
                default=self.settings.max_loan_amount
            )
            
            self.settings.loan_interest_rate = self.ui.get_input(
                "Taux d'intérêt annuel (ex: 0.045 pour 4.5%)",
                Decimal, min_val=Decimal("0.01"), max_val=Decimal("0.15"),
                default=self.settings.loan_interest_rate
            )
        
        # Configuration IA
        difficulty_options = ["Facile", "Moyen", "Difficile"]
        difficulty_choice = self.ui.show_menu("Difficulté de l'IA", difficulty_options)
        if difficulty_choice > 0:
            difficulty_map = ["easy", "medium", "hard"]
            self.settings.ai_difficulty = difficulty_map[difficulty_choice - 1]
        
        self.settings.ai_count = self.ui.get_input(
            "Nombre de concurrents IA",
            int, min_val=0, max_val=6,
            default=self.settings.ai_count
        )
        
        self.ui.show_success("Paramètres de jeu mis à jour.")
        self.ui.pause()
    
    def _configure_market(self):
        """Configure le marché et la concurrence."""
        self.ui.clear_screen()
        
        info = [
            "📊 MARCHÉ ET CONCURRENCE",
            "",
            "Définissez la taille du marché et l'intensité concurrentielle."
        ]
        self.ui.print_box(info, style="header")
        
        self.settings.total_market_size = self.ui.get_input(
            "Taille totale du marché (clients/tour)",
            int, min_val=100, max_val=2000,
            default=self.settings.total_market_size
        )
        
        self.settings.market_growth_rate = self.ui.get_input(
            "Taux de croissance du marché par an (ex: 0.02 pour 2%)",
            Decimal, min_val=Decimal("-0.05"), max_val=Decimal("0.10"),
            default=self.settings.market_growth_rate
        )
        
        competition_options = ["Faible", "Normale", "Intense"]
        competition_choice = self.ui.show_menu("Intensité concurrentielle", competition_options)
        if competition_choice > 0:
            competition_map = ["low", "normal", "high"]
            self.settings.competition_intensity = competition_map[competition_choice - 1]
        
        self.ui.show_success("Configuration du marché mise à jour.")
        self.ui.pause()
    
    def _configure_events(self):
        """Configure les événements et le réalisme."""
        self.ui.clear_screen()
        
        info = [
            "🎯 ÉVÉNEMENTS ET RÉALISME",
            "",
            "Activez les mécaniques qui rendent le jeu plus réaliste."
        ]
        self.ui.print_box(info, style="header")
        
        self.settings.enable_random_events = self.ui.confirm(
            "Activer les événements aléatoires",
            default=self.settings.enable_random_events
        )
        
        if self.settings.enable_random_events:
            self.settings.event_frequency = self.ui.get_input(
                "Fréquence des événements (ex: 0.15 pour 15% par tour)",
                Decimal, min_val=Decimal("0.05"), max_val=Decimal("0.50"),
                default=self.settings.event_frequency
            )
        
        self.settings.enable_seasonal_effects = self.ui.confirm(
            "Activer les effets saisonniers",
            default=self.settings.enable_seasonal_effects
        )
        
        self.settings.enable_economic_cycles = self.ui.confirm(
            "Activer les cycles économiques",
            default=self.settings.enable_economic_cycles
        )
        
        self.ui.show_success("Configuration des événements mise à jour.")
        self.ui.pause()
    
    def _configure_evaluation(self):
        """Configure l'évaluation et la notation."""
        self.ui.clear_screen()
        
        info = [
            "📝 ÉVALUATION ET NOTATION",
            "",
            "Configurez le système de notation automatique."
        ]
        self.ui.print_box(info, style="header")
        
        self.settings.enable_scoring = self.ui.confirm(
            "Activer la notation automatique",
            default=self.settings.enable_scoring
        )
        
        if self.settings.enable_scoring:
            print("\nCritères de notation (total doit faire 1.0):")
            
            criteria_names = {
                "survival": "Survie (rester en vie)",
                "profitability": "Rentabilité (marge bénéficiaire)",
                "growth": "Croissance (évolution CA)",
                "efficiency": "Efficacité (ratios de gestion)",
                "strategy": "Stratégie (décisions cohérentes)"
            }
            
            total_weight = Decimal("0")
            for key, name in criteria_names.items():
                weight = self.ui.get_input(
                    f"Poids pour {name}",
                    Decimal, min_val=Decimal("0"), max_val=Decimal("1"),
                    default=self.settings.scoring_criteria[key]
                )
                self.settings.scoring_criteria[key] = weight
                total_weight += weight
            
            if abs(total_weight - Decimal("1.0")) > Decimal("0.01"):
                self.ui.show_error(f"Le total des poids ({total_weight}) doit faire 1.0")
                self.ui.pause()
                return
        
        self.settings.detailed_feedback = self.ui.confirm(
            "Fournir un feedback détaillé aux étudiants",
            default=self.settings.detailed_feedback
        )
        
        self.ui.show_success("Configuration de l'évaluation mise à jour.")
        self.ui.pause()
    
    def _configure_restrictions(self):
        """Configure les restrictions et limites."""
        # Implementation simplifiée pour l'instant
        self.ui.show_info("Configuration des restrictions - À implémenter")
        self.ui.pause()
    
    def _configure_commerce_locations(self):
        """Configure les emplacements de commerce disponibles."""
        # Implementation simplifiée pour l'instant
        self.ui.show_info("Configuration des emplacements - À implémenter")
        self.ui.pause()
    
    def _save_configuration(self):
        """Sauvegarde la configuration."""
        config_path = Path("admin_configs") / f"{self.settings.session_name.replace(' ', '_')}.yaml"
        config_path.parent.mkdir(exist_ok=True)
        
        # Conversion en dict pour YAML
        config_dict = {
            "session_info": {
                "name": self.settings.session_name,
                "instructor": self.settings.instructor_name,
                "course_code": self.settings.course_code,
                "academic_year": self.settings.academic_year
            },
            "game_params": {
                "max_players": self.settings.max_players,
                "total_turns": self.settings.total_turns,
                "starting_budget_min": float(self.settings.starting_budget_min),
                "starting_budget_max": float(self.settings.starting_budget_max),
                "ai_count": self.settings.ai_count,
                "ai_difficulty": self.settings.ai_difficulty
            },
            "features": {
                "enable_random_events": self.settings.enable_random_events,
                "enable_seasonal_effects": self.settings.enable_seasonal_effects,
                "enable_scoring": self.settings.enable_scoring
            }
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            
            self.ui.show_success(f"Configuration sauvegardée dans {config_path}")
        except Exception as e:
            self.ui.show_error(f"Erreur lors de la sauvegarde: {e}")
        
        self.ui.pause()
    
    def _validate_configuration(self) -> bool:
        """Valide la configuration avant de lancer la partie."""
        errors = []
        
        if not self.settings.session_name.strip():
            errors.append("Le nom de session est requis")
        
        if self.settings.starting_budget_min >= self.settings.starting_budget_max:
            errors.append("Le budget minimum doit être inférieur au maximum")
        
        if self.settings.enable_scoring:
            total_weight = sum(self.settings.scoring_criteria.values())
            if abs(total_weight - Decimal("1.0")) > Decimal("0.01"):
                errors.append("Les poids de notation doivent totaliser 1.0")
        
        if errors:
            error_msg = "Erreurs de configuration:\n" + "\n".join(f"• {error}" for error in errors)
            self.ui.show_error(error_msg)
            self.ui.pause()
            return False
        
        return True
