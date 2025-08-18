#!/usr/bin/env python3
"""
Démonstration du mode administrateur FoodOps Pro.
"""

from src.foodops_pro.ui.console_ui import ConsoleUI
from src.foodops_pro.admin.admin_config import AdminSettings, AdminConfigManager

def demo_admin_interface():
    """Démonstration de l'interface administrateur."""
    print("=" * 70)
    print("👨‍🏫 DÉMONSTRATION MODE ADMINISTRATEUR FOODOPS PRO")
    print("=" * 70)
    
    ui = ConsoleUI()
    
    # Écran d'accueil admin
    welcome = [
        "👨‍🏫 CONFIGURATION ADMINISTRATEUR",
        "",
        "Bienvenue dans l'interface de configuration FoodOps Pro.",
        "Vous pouvez personnaliser tous les aspects de la partie",
        "pour vos étudiants.",
        "",
        "Cette interface vous permet de :",
        "• Configurer les paramètres de jeu",
        "• Définir les critères d'évaluation",
        "• Sauvegarder vos configurations",
        "• Adapter la difficulté à vos étudiants"
    ]
    
    ui.print_box(welcome, "MODE PROFESSEUR", "header")
    print()

def demo_configuration_actuelle():
    """Affiche la configuration par défaut."""
    ui = ConsoleUI()
    settings = AdminSettings()
    
    config_summary = [
        f"📋 Session: {settings.session_name}",
        f"👨‍🏫 Professeur: {settings.instructor_name or 'Non défini'}",
        f"🎓 Cours: {settings.course_code or 'Non défini'}",
        "",
        f"👥 Joueurs max: {settings.max_players}",
        f"💰 Budget initial: {settings.starting_budget_min:,.0f}€ - {settings.starting_budget_max:,.0f}€",
        f"⏱️ Durée: {settings.total_turns} tours ({settings.turn_duration_description} chacun)",
        f"🤖 IA: {settings.ai_count} concurrent(s) - Difficulté {settings.ai_difficulty}",
        "",
        f"🎲 Événements aléatoires: {'✅' if settings.enable_random_events else '❌'}",
        f"📈 Effets saisonniers: {'✅' if settings.enable_seasonal_effects else '❌'}",
        f"📊 Notation automatique: {'✅' if settings.enable_scoring else '❌'}",
        "",
        f"💳 Emprunts autorisés: {'✅' if settings.allow_loans else '❌'}",
        f"💰 Montant max emprunt: {settings.max_loan_amount:,.0f}€",
        f"📈 Taux d'intérêt: {settings.loan_interest_rate:.1%}"
    ]
    
    ui.print_box(config_summary, "CONFIGURATION ACTUELLE", "info")
    print()

def demo_menu_configuration():
    """Affiche le menu de configuration."""
    ui = ConsoleUI()
    
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
    
    print("MENU DE CONFIGURATION DISPONIBLE:")
    for i, option in enumerate(menu_options, 1):
        print(f"  {i}. {option}")
    print()

def demo_criteres_notation():
    """Démonstration des critères de notation."""
    ui = ConsoleUI()
    settings = AdminSettings()
    
    notation_info = [
        "SYSTÈME DE NOTATION AUTOMATIQUE:",
        "",
        "Critères d'évaluation personnalisables:",
        f"• Survie (rester en vie): {settings.scoring_criteria['survival']:.0%}",
        f"• Rentabilité (marge bénéficiaire): {settings.scoring_criteria['profitability']:.0%}",
        f"• Croissance (évolution CA): {settings.scoring_criteria['growth']:.0%}",
        f"• Efficacité (ratios de gestion): {settings.scoring_criteria['efficiency']:.0%}",
        f"• Stratégie (décisions cohérentes): {settings.scoring_criteria['strategy']:.0%}",
        "",
        "Fonctionnalités:",
        "✅ Calcul automatique de la note finale",
        "✅ Feedback détaillé pour chaque étudiant",
        "✅ Export des résultats pour le LMS",
        "✅ Analyse comparative des performances"
    ]
    
    ui.print_box(notation_info, "ÉVALUATION PÉDAGOGIQUE", "success")
    print()

def demo_parametres_avances():
    """Démonstration des paramètres avancés."""
    ui = ConsoleUI()
    
    avances_info = [
        "PARAMÈTRES AVANCÉS DISPONIBLES:",
        "",
        "🎯 Marché et Économie:",
        "• Taille du marché (100-2000 clients/tour)",
        "• Taux de croissance du marché (-5% à +10%/an)",
        "• Intensité concurrentielle (faible/normale/intense)",
        "",
        "🎲 Événements et Réalisme:",
        "• Événements aléatoires (pannes, contrôles, festivals...)",
        "• Effets saisonniers (variations de demande)",
        "• Cycles économiques (récession/croissance)",
        "• Fréquence des événements (5% à 50% par tour)",
        "",
        "💰 Contraintes Financières:",
        "• Autorisation d'emprunts bancaires",
        "• Montant maximum d'emprunt",
        "• Taux d'intérêt (1% à 15%)",
        "",
        "🔒 Restrictions Pédagogiques:",
        "• Types de restaurants autorisés",
        "• Limites d'employés (min/max)",
        "• Restrictions sur les changements de prix",
        "• Emplacements de commerce disponibles"
    ]
    
    ui.print_box(avances_info, "CONFIGURATION AVANCÉE", "warning")
    print()

def demo_scenarios_pedagogiques():
    """Exemples de scénarios pédagogiques."""
    ui = ConsoleUI()
    
    scenarios = [
        "EXEMPLES DE SCÉNARIOS PÉDAGOGIQUES:",
        "",
        "🎓 NIVEAU DÉBUTANT:",
        "• Budget élevé (40-60k€)",
        "• Durée courte (6-8 tours)",
        "• IA facile, peu d'événements",
        "• Focus sur les bases de gestion",
        "",
        "📚 NIVEAU INTERMÉDIAIRE:",
        "• Budget moyen (25-40k€)",
        "• Durée standard (12 tours)",
        "• IA moyenne, événements modérés",
        "• Emprunts autorisés",
        "",
        "🏆 NIVEAU AVANCÉ:",
        "• Budget serré (15-25k€)",
        "• Durée longue (18-24 tours)",
        "• IA difficile, nombreux événements",
        "• Cycles économiques activés",
        "",
        "🎯 CONCOURS/COMPÉTITION:",
        "• Conditions identiques pour tous",
        "• Notation stricte",
        "• Classement final",
        "• Export automatique des résultats"
    ]
    
    ui.print_box(scenarios, "SCÉNARIOS TYPES", "info")
    print()

def demo_export_resultats():
    """Démonstration de l'export des résultats."""
    ui = ConsoleUI()
    
    export_info = [
        "EXPORT ET SUIVI DES RÉSULTATS:",
        "",
        "📊 Données exportées:",
        "• Note finale de chaque étudiant",
        "• Détail des performances par critère",
        "• Évolution tour par tour",
        "• Décisions prises et leur impact",
        "• Classement final",
        "",
        "📁 Formats disponibles:",
        "• JSON (données brutes)",
        "• CSV (import Excel/LMS)",
        "• PDF (rapport détaillé)",
        "",
        "🎓 Intégration LMS:",
        "• Compatible Moodle, Blackboard",
        "• Import direct des notes",
        "• Feedback automatique",
        "",
        "📈 Analyses disponibles:",
        "• Performance moyenne de la classe",
        "• Identification des difficultés",
        "• Recommandations pédagogiques"
    ]
    
    ui.print_box(export_info, "SUIVI PÉDAGOGIQUE", "success")
    print()

def main():
    """Démonstration complète du mode admin."""
    demo_admin_interface()
    demo_configuration_actuelle()
    demo_menu_configuration()
    demo_criteres_notation()
    demo_parametres_avances()
    demo_scenarios_pedagogiques()
    demo_export_resultats()
    
    print("=" * 70)
    print("🎉 DÉMONSTRATION MODE ADMINISTRATEUR TERMINÉE")
    print("=" * 70)
    print()
    print("✨ FONCTIONNALITÉS CLÉS DU MODE PROFESSEUR:")
    print("  ✅ Configuration complète des paramètres de jeu")
    print("  ✅ Critères d'évaluation personnalisables")
    print("  ✅ Scénarios pédagogiques prédéfinis")
    print("  ✅ Sauvegarde et réutilisation des configurations")
    print("  ✅ Export automatique des résultats")
    print("  ✅ Intégration avec les LMS")
    print("  ✅ Analyses et recommandations pédagogiques")
    print()
    print("🚀 POUR UTILISER LE MODE ADMIN:")
    print("  python -m src.foodops_pro.cli_pro --admin")
    print()
    print("📚 IDÉAL POUR:")
    print("  • Cours de gestion d'entreprise")
    print("  • Formations en entrepreneuriat")
    print("  • Écoles de commerce")
    print("  • Modules de comptabilité/finance")

if __name__ == "__main__":
    main()
