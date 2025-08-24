#!/usr/bin/env python3
"""
Démonstration des nouvelles fonctionnalités FoodOps Pro.
"""

from decimal import Decimal
from game_engine.ui.console_ui import ConsoleUI
from game_engine.domain.commerce import CommerceManager
from game_engine.admin.admin_config import AdminSettings
from game_engine.io.data_loader import DataLoader


def demo_interface():
    """Démonstration de l'interface."""
    print("=== DÉMONSTRATION INTERFACE PROFESSIONNELLE ===")

    ui = ConsoleUI()

    # Test d'affichage de boîte
    welcome = [
        "🍽️ FOODOPS PRO 2024 🍽️",
        "",
        "Simulateur de Gestion de Restaurant",
        "Version Éducative Professionnelle",
        "",
        "Bienvenue dans la nouvelle interface !",
    ]

    ui.print_box(welcome, "BIENVENUE", "header")

    # Test de menu
    options = [
        "Voir les fonds de commerce",
        "Configuration administrateur",
        "Rapports financiers",
        "Quitter",
    ]

    print("Exemple de menu professionnel:")
    choice = ui.show_menu("MENU PRINCIPAL", options, allow_back=False)
    print(f"Choix sélectionné: {choice}")


def demo_commerce():
    """Démonstration du système de commerce."""
    print("\n=== DÉMONSTRATION FONDS DE COMMERCE ===")

    ui = ConsoleUI()
    manager = CommerceManager()

    # Affichage des commerces disponibles
    budget = Decimal("60000")
    locations = manager.get_available_locations(budget)

    commerce_info = [f"FONDS DE COMMERCE DISPONIBLES (Budget: {budget:,.0f}€)", ""]

    for i, location in enumerate(locations[:3], 1):  # Top 3
        commerce_info.extend(
            [
                f"{i}. {location.name}",
                f"   📍 {location.location_type.value.replace('_', ' ').title()}",
                f"   💰 {location.price:,.0f}€ + {location.renovation_cost:,.0f}€ rénovation",
                f"   🏠 {location.size} couverts - {location.foot_traffic} passage",
                f"   🏢 {location.rent_monthly:,.0f}€/mois",
                "",
            ]
        )

    ui.print_box(commerce_info, style="info")


def demo_admin_config():
    """Démonstration de la configuration admin."""
    print("\n=== DÉMONSTRATION CONFIGURATION ADMIN ===")

    ui = ConsoleUI()
    settings = AdminSettings()

    # Affichage de la configuration par défaut
    config_info = [
        "CONFIGURATION ADMINISTRATEUR PAR DÉFAUT:",
        "",
        f"📋 Session: {settings.session_name}",
        f"👥 Joueurs max: {settings.max_players}",
        f"💰 Budget: {settings.starting_budget_min:,.0f}€ - {settings.starting_budget_max:,.0f}€",
        f"⏱️ Durée: {settings.total_turns} tours",
        f"🤖 IA: {settings.ai_count} concurrent(s) - {settings.ai_difficulty}",
        "",
        f"🎲 Événements aléatoires: {'✅' if settings.enable_random_events else '❌'}",
        f"📈 Effets saisonniers: {'✅' if settings.enable_seasonal_effects else '❌'}",
        f"📊 Notation: {'✅' if settings.enable_scoring else '❌'}",
        "",
        "Le professeur peut modifier tous ces paramètres !",
    ]

    ui.print_box(config_info, "MODE PROFESSEUR", "success")


def demo_scenario():
    """Démonstration du scénario."""
    print("\n=== DÉMONSTRATION SCÉNARIO ===")

    ui = ConsoleUI()

    try:
        loader = DataLoader()
        data = loader.load_all_data()
        scenario = data["scenario"]

        # Affichage du scénario comme dans le jeu
        ui.show_welcome_screen(scenario, admin_mode=False)

    except Exception as e:
        print(f"Erreur lors du chargement du scénario: {e}")


def demo_financial_kpis():
    """Démonstration des KPIs financiers."""
    print("\n=== DÉMONSTRATION KPIs FINANCIERS ===")

    ui = ConsoleUI()

    # Simulation de KPIs
    kpis = [
        "KPIs MÉTIER EXEMPLE:",
        "",
        "• Food Cost: 28.5% (Objectif: <30%) ✅",
        "• Coût personnel: 32.1% (Objectif: <35%) ✅",
        "• Marge brute: 71.5%",
        "• Marge nette: 12.3%",
        "• Ticket moyen: 18.45€",
        "• Taux de rotation: 2.3 (Objectif: >2.0) ✅",
        "• Capacité utilisée: 50 couverts",
        "",
        "📊 Performance: EXCELLENTE",
    ]

    ui.print_box(kpis, "TABLEAU DE BORD", "success")


def demo_compte_resultat():
    """Démonstration du compte de résultat."""
    print("\n=== DÉMONSTRATION COMPTE DE RÉSULTAT ===")

    ui = ConsoleUI()

    # Exemple de compte de résultat
    pnl = [
        "COMPTE DE RÉSULTAT - RESTAURANT EXEMPLE",
        "Période: Janvier 2024",
        "",
        "PRODUITS D'EXPLOITATION",
        "├─ Chiffre d'affaires HT              │        28,450.00 €",
        "├─ Subventions d'exploitation          │           150.00 €",
        "└─ TOTAL PRODUITS                      │        28,600.00 €",
        "",
        "CHARGES D'EXPLOITATION",
        "├─ Achats matières premières          │         8,535.00 €",
        "├─ Charges externes",
        "│  ├─ Loyer                           │         4,500.00 €",
        "│  ├─ Électricité/Gaz                 │           890.00 €",
        "│  └─ Assurances                      │           245.00 €",
        "├─ Charges de personnel",
        "│  ├─ Salaires bruts                  │         8,200.00 €",
        "│  └─ Charges sociales                │         3,444.00 €",
        "└─ TOTAL CHARGES                       │        25,814.00 €",
        "",
        "RÉSULTAT NET                           │         2,786.00 €",
    ]

    ui.print_box(pnl, style="info")


def main():
    """Démonstration principale."""
    print("🎮 DÉMONSTRATION FOODOPS PRO - NOUVELLES FONCTIONNALITÉS")
    print("=" * 70)

    try:
        # Interface professionnelle
        demo_interface()

        # Système de commerce
        demo_commerce()

        # Configuration admin
        demo_admin_config()

        # Scénario
        demo_scenario()

        # KPIs financiers
        demo_financial_kpis()

        # Compte de résultat
        demo_compte_resultat()

        print("\n" + "=" * 70)
        print("🎉 DÉMONSTRATION TERMINÉE !")
        print("\n✨ NOUVELLES FONCTIONNALITÉS IMPLÉMENTÉES:")
        print("  ✅ Interface console professionnelle avec boîtes et couleurs")
        print("  ✅ Écran d'accueil avec présentation du scénario")
        print("  ✅ Mode administrateur pour professeurs")
        print("  ✅ Système d'achat de fonds de commerce réaliste")
        print("  ✅ Compte de résultat professionnel")
        print("  ✅ Menu de décisions enrichi")
        print("  ✅ KPIs métier détaillés")
        print("  ✅ Rapports financiers complets")

        print("\n🚀 POUR JOUER:")
        print("  python -m src.game_engine.cli_pro")
        print("  python -m src.game_engine.cli_pro --admin  (mode professeur)")

    except Exception as e:
        print(f"\n❌ Erreur durant la démonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
