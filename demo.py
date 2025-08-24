#!/usr/bin/env python3
"""
Démonstration complète FoodOps Pro - Suite de démonstrations unifiée.
Combine les fonctionnalités de demo.py, demo_admin.py, demo_pro.py
"""

from decimal import Decimal

from creation_scenario import AdminSettings
from game_engine.domain.recipe.costing import RecipeCostCalculator
from game_engine.domain.market.market import MarketEngine
from game_engine.domain.commerce import CommerceManager
from game_engine.domain.restaurant import Restaurant, RestaurantType
from game_engine.io.data_loader import DataLoader
from game_engine.ui.console_ui import ConsoleUI


def demo_data_loading():
    """Démonstration du chargement des données."""
    print("=== DÉMONSTRATION CHARGEMENT DES DONNÉES ===")

    loader = DataLoader()
    data = loader.load_all_data()

    print(f"✓ {len(data['ingredients'])} ingrédients chargés")
    print(f"✓ {len(data['recipes'])} recettes chargées")
    print(f"✓ {len(data['suppliers'])} fournisseurs chargés")
    print(f"✓ Scénario '{data['scenario'].name}' chargé")

    # Affichage de quelques ingrédients
    print("\nQuelques ingrédients :")
    for i, (id, ingredient) in enumerate(data["ingredients"].items()):
        if i >= 5:
            break
        print(f"  - {ingredient.name}: {ingredient.cost_ht}€ HT/{ingredient.unit}")

    # Affichage de quelques recettes
    print("\nQuelques recettes :")
    for i, (id, recipe) in enumerate(data["recipes"].items()):
        if i >= 5:
            break
        print(
            f"  - {recipe.name}: {len(recipe.items)} ingrédients, {recipe.temps_total_min}min"
        )

    return data


def demo_recipe_costing(data):
    """Démonstration du calcul de coûts de recettes."""
    print("\n=== DÉMONSTRATION CALCUL DE COÛTS ===")

    calculator = RecipeCostCalculator(data["ingredients"])

    # Test sur le burger classique
    burger_recipe = data["recipes"]["burger_classic"]
    breakdown = calculator.calculate_recipe_cost(burger_recipe)

    print(f"\nCoût de la recette '{burger_recipe.name}' :")
    print(f"  Coût total HT: {breakdown.total_cost_ht:.2f}€")
    print(f"  Coût par portion: {breakdown.cost_per_portion:.2f}€")
    print(f"  Coût main d'œuvre: {breakdown.preparation_time_cost:.2f}€")
    print(f"  Coût total avec MO: {breakdown.total_cost_with_labor:.2f}€")

    print("\nDétail par ingrédient :")
    for ingredient_cost in breakdown.ingredient_costs:
        print(
            f"  - {ingredient_cost.ingredient_name}: "
            f"{ingredient_cost.quantity_used} × {ingredient_cost.unit_cost_ht:.2f}€ = "
            f"{ingredient_cost.total_cost_ht:.2f}€"
        )

    # Analyse de marge
    selling_price = Decimal("12.50")
    margin_analysis = calculator.calculate_margin_analysis(
        burger_recipe, selling_price, Decimal("0.10")
    )

    print(f"\nAnalyse de marge (prix de vente: {selling_price}€ TTC) :")
    print(f"  Prix HT: {margin_analysis['selling_price_ht']:.2f}€")
    print(f"  Marge HT: {margin_analysis['margin_ht']:.2f}€")
    print(f"  Marge %: {margin_analysis['margin_percentage']:.1f}%")
    print(f"  Food cost %: {margin_analysis['food_cost_percentage']:.1f}%")


def demo_market_simulation(data):
    """Démonstration de la simulation de marché."""
    print("\n=== DÉMONSTRATION SIMULATION DE MARCHÉ ===")

    # Création de deux restaurants
    fast_food = Restaurant(
        id="demo_fast",
        name="Demo Fast Food",
        type=RestaurantType.FAST,
        capacity_base=80,
        speed_service=Decimal("1.4"),
        staffing_level=2,
    )

    classic = Restaurant(
        id="demo_classic",
        name="Demo Restaurant Classique",
        type=RestaurantType.CLASSIC,
        capacity_base=50,
        speed_service=Decimal("1.0"),
        staffing_level=2,
    )

    # Configuration des menus
    fast_food.set_recipe_price("burger_classic", Decimal("10.50"))
    fast_food.set_recipe_price("burger_chicken", Decimal("11.00"))
    fast_food.activate_recipe("burger_classic")
    fast_food.activate_recipe("burger_chicken")

    classic.set_recipe_price("pasta_bolognese", Decimal("16.00"))
    classic.set_recipe_price("steak_frites", Decimal("22.00"))
    classic.activate_recipe("pasta_bolognese")
    classic.activate_recipe("steak_frites")

    restaurants = [fast_food, classic]

    # Simulation de marché
    scenario = data["scenario"]
    market_engine = MarketEngine(scenario, random_seed=42)

    print(f"\nSimulation sur {scenario.base_demand} clients potentiels")
    print("Segments de marché :")
    for segment in scenario.segments:
        print(f"  - {segment.name}: {segment.share:.1%} (budget: {segment.budget}€)")

    # Simulation de 3 tours
    for turn in range(1, 4):
        print(f"\n--- TOUR {turn} ---")
        results = market_engine.allocate_demand(restaurants, turn=turn)

        for restaurant in restaurants:
            result = results[restaurant.id]
            print(f"{restaurant.name}:")
            print(f"  Capacité: {result.capacity} couverts")
            print(f"  Demande allouée: {result.allocated_demand}")
            print(f"  Clients servis: {result.served_customers}")

            # Calcul manuel des métriques pour l'affichage
            utilization = (
                (result.served_customers / result.capacity * 100)
                if result.capacity > 0
                else 0
            )
            print(f"  Taux d'utilisation: {utilization:.1f}%")
            print(f"  Chiffre d'affaires: {result.revenue:.0f}€")

            if result.served_customers > 0:
                avg_ticket = result.revenue / result.served_customers
                print(f"  Ticket moyen: {avg_ticket:.2f}€")

    # Analyse finale
    analysis = market_engine.get_market_analysis()
    print("\nAnalyse du marché (dernier tour) :")
    print(f"  Total clients servis: {analysis['total_served']}")
    print(f"  CA total: {analysis['total_revenue']:.0f}€")
    print(f"  Taux d'utilisation marché: {analysis['market_utilization']:.1%}")
    print(f"  Satisfaction demande: {analysis['demand_satisfaction']:.1%}")


# FONCTIONS DE DÉMONSTRATION ADMIN (issues de demo_admin.py)
def demo_admin_interface():
    """Démonstration de l'interface administrateur."""
    print("=== DÉMONSTRATION INTERFACE ADMINISTRATEUR ===")

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
        "• Adapter la difficulté à vos étudiants",
    ]

    ui.print_box(welcome, "MODE PROFESSEUR", "header")


def demo_configuration_actuelle():
    """Affiche la configuration par défaut."""
    ui = ConsoleUI()
    settings = AdminSettings()

    config_summary = [
        f"📋 Session: {settings.session_name}",
        f"👥 Joueurs max: {settings.max_players}",
        f"💰 Budget initial: {settings.starting_budget_min:,.0f}€ - {settings.starting_budget_max:,.0f}€",
        f"⏱️ Durée: {settings.total_turns} tours",
        f"🤖 IA: {settings.ai_count} concurrent(s) - {settings.ai_difficulty}",
        "",
        f"🎲 Événements aléatoires: {'✅' if settings.enable_random_events else '❌'}",
        f"📈 Effets saisonniers: {'✅' if settings.enable_seasonal_effects else '❌'}",
        f"📊 Notation: {'✅' if settings.enable_scoring else '❌'}",
    ]

    ui.print_box(config_summary, "CONFIGURATION ACTUELLE", "info")


def demo_menu_configuration():
    """Affiche le menu de configuration."""
    ConsoleUI()

    menu_options = [
        "📋 Informations de session",
        "🎮 Paramètres de jeu",
        "🏪 Fonds de commerce disponibles",
        "📊 Marché et concurrence",
        "🎯 Événements et réalisme",
        "📝 Évaluation et notation",
        "🔒 Restrictions et limites",
        "💾 Sauvegarder configuration",
        "▶️ Lancer la partie",
    ]

    print("MENU DE CONFIGURATION DISPONIBLE:")
    for i, option in enumerate(menu_options, 1):
        print(f"  {i}. {option}")


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
        "✅ Analyse comparative des performances",
    ]

    ui.print_box(notation_info, "ÉVALUATION PÉDAGOGIQUE", "success")


# FONCTIONS DE DÉMONSTRATION PRO (issues de demo_pro.py)
def demo_interface_pro():
    """Démonstration de l'interface professionnelle."""
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


def demo_commerce_pro():
    """Démonstration du système de commerce."""
    print("=== DÉMONSTRATION FONDS DE COMMERCE ===")

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


def demo_admin_config_pro():
    """Démonstration de la configuration admin."""
    print("=== DÉMONSTRATION CONFIGURATION ADMIN ===")

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


def demo_financial_kpis():
    """Démonstration des KPIs financiers."""
    print("=== DÉMONSTRATION KPIs FINANCIERS ===")

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
    print("=== DÉMONSTRATION COMPTE DE RÉSULTAT ===")

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


def show_demo_menu():
    """Affiche le menu de sélection de démonstration."""
    print("🎮 FOODOPS PRO - SUITE DE DÉMONSTRATIONS")
    print("=" * 60)
    print("Choisissez une démonstration:")

    print("1. 📊 Chargement des données & calculs de base")
    print("   (Original demo.py)")

    print("2. 👨‍🏫 Interface & configuration administrateur")
    print("   (Fonctionnalités professeur)")

    print("3. 🍽️ Interface professionnelle & commerce")
    print("   (Nouvelles fonctionnalités Pro)")

    print("4. 📈 KPIs financiers & compte de résultat")
    print("   (Outils de gestion avancés)")

    print("5. 🎯 Démonstration complète")
    print("   (Toutes les démos en séquence)")

    print("6. ❌ Quitter")

    return input("Votre choix (1-6) : ").strip()


def main():
    """Fonction principale de démonstration unifiée."""
    print("🎮 FOODOPS PRO - SUITE DE DÉMONSTRATIONS COMPLÈTE")
    print("=" * 60)

    while True:
        choice = show_demo_menu()

        if choice == "1":
            try:
                print("\n" + "=" * 60)
                # Chargement des données
                data = demo_data_loading()
                # Calcul de coûts
                demo_recipe_costing(data)
                # Simulation de marché
                demo_market_simulation(data)
                print("\n✅ Démonstration de base terminée !")
            except Exception as e:
                print(f"\n❌ Erreur durant la démonstration : {e}")
                import traceback

                traceback.print_exc()

        elif choice == "2":
            print("\n" + "=" * 60)
            demo_admin_interface()
            demo_configuration_actuelle()
            demo_menu_configuration()
            demo_criteres_notation()
            print("✅ Démonstration admin terminée !")

        elif choice == "3":
            print("\n" + "=" * 60)
            demo_interface_pro()
            demo_commerce_pro()
            demo_admin_config_pro()
            print("✅ Démonstration Pro terminée !")

        elif choice == "4":
            print("\n" + "=" * 60)
            demo_financial_kpis()
            demo_compte_resultat()
            print("✅ Démonstration financière terminée !")

        elif choice == "5":
            try:
                print("\n" + "=" * 80)
                print("🎯 DÉMONSTRATION COMPLÈTE - TOUTES LES FONCTIONNALITÉS")
                print("=" * 80)

                # Partie 1: Base
                data = demo_data_loading()
                demo_recipe_costing(data)
                demo_market_simulation(data)

                # Partie 2: Admin
                demo_admin_interface()
                demo_configuration_actuelle()

                # Partie 3: Pro
                demo_interface_pro()
                demo_commerce_pro()

                # Partie 4: Finance
                demo_financial_kpis()
                demo_compte_resultat()

                print("\n" + "=" * 80)
                print("🎉 DÉMONSTRATION COMPLÈTE TERMINÉE AVEC SUCCÈS !")
                print("=" * 80)
                print(
                    "\n✨ Toutes les fonctionnalités de FoodOps Pro ont été présentées:"
                )
                print("  ✅ Interface console professionnelle")
                print("  ✅ Mode administrateur pour professeurs")
                print("  ✅ Système d'achat de fonds de commerce")
                print("  ✅ Calculs de coûts et marges détaillés")
                print("  ✅ Simulation de marché réaliste")
                print("  ✅ KPIs métier et compte de résultat")
                print("  ✅ Évaluation pédagogique automatisée")

            except Exception as e:
                print(f"\n❌ Erreur durant la démonstration complète : {e}")
                import traceback

                traceback.print_exc()

        elif choice == "6":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Choix invalide. Veuillez sélectionner 1-6.")

        if choice != "6":
            input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()
