#!/usr/bin/env python3
"""
Démonstration des nouveaux modules avancés : Marketing et Finance.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from decimal import Decimal
from datetime import date, timedelta
from src.foodops_pro.domain.marketing import MarketingManager, CampaignType
from src.foodops_pro.domain.finance_advanced import FinanceManager, TransactionType


def demo_marketing_system():
    """Démonstration du système marketing."""
    print("📈 DÉMONSTRATION SYSTÈME MARKETING")
    print("=" * 70)

    marketing = MarketingManager()

    # Création de campagnes
    print("\n🎯 CRÉATION DE CAMPAGNES MARKETING:")

    # Campagne réseaux sociaux
    social_campaign = marketing.create_campaign(
        name="Promotion Été 2024",
        campaign_type=CampaignType.SOCIAL_MEDIA,
        budget=Decimal("350"),
        duration_days=7,
        target_segments=["étudiants", "jeunes_actifs"],
    )

    # Campagne événement
    event_campaign = marketing.create_campaign(
        name="Soirée Dégustation",
        campaign_type=CampaignType.EVENTS,
        budget=Decimal("600"),
        duration_days=1,
        target_segments=["foodies", "familles"],
    )

    # Programme fidélité
    loyalty_campaign = marketing.create_campaign(
        name="Carte Fidélité",
        campaign_type=CampaignType.LOYALTY_PROGRAM,
        budget=Decimal("900"),
        duration_days=30,
        target_segments=["tous"],
    )

    campaigns = [social_campaign, event_campaign, loyalty_campaign]

    for campaign in campaigns:
        print(f"\n📋 {campaign.name}:")
        print(f"   Type: {campaign.type.value}")
        print(f"   Budget: {campaign.budget}€")
        print(f"   Durée: {campaign.duration_days} jours")
        print(f"   Portée attendue: {campaign.expected_reach:,} personnes")
        print(f"   Conversions attendues: {campaign.expected_new_customers}")
        print(f"   Coût par acquisition: {campaign.cost_per_acquisition:.2f}€")
        print(f"   Coût quotidien: {campaign.daily_cost:.2f}€")

    # Lancement des campagnes
    print(f"\n🚀 LANCEMENT DES CAMPAGNES:")
    start_date = date.today()

    for campaign in campaigns:
        success = marketing.launch_campaign(campaign.id, start_date)
        status = "✅ Lancée" if success else "❌ Échec"
        print(f"   {campaign.name}: {status}")

    # Impact quotidien
    print(f"\n📊 IMPACT MARKETING QUOTIDIEN:")
    for day in range(1, 8):  # 7 jours
        current_date = start_date + timedelta(days=day - 1)
        impact = marketing.calculate_daily_marketing_impact(current_date)

        print(f"\n   Jour {day} ({current_date.strftime('%d/%m')}):")
        print(f"     Portée: {impact['total_reach']:,} personnes")
        print(f"     Conversions: {impact['total_conversions']} nouveaux clients")
        print(f"     Coût: {impact['total_cost']:.2f}€")
        print(f"     Campagnes actives: {impact['active_campaigns']}")

        if impact["segment_impact"]:
            print(f"     Impact par segment:")
            for segment, conv in impact["segment_impact"].items():
                print(f"       • {segment}: {conv:.1f} conversions")

    # Avis clients
    print(f"\n⭐ SIMULATION AVIS CLIENTS:")
    reviews_data = [
        ("client_001", 5, "Excellent burger, service rapide!", "google"),
        ("client_002", 4, "Très bon, je recommande", "tripadvisor"),
        ("client_003", 3, "Correct sans plus", "facebook"),
        ("client_004", 5, "Parfait ! Qualité au top", "google"),
        ("client_005", 2, "Service lent, déçu", "yelp"),
        ("client_006", 4, "Bon rapport qualité/prix", "google"),
    ]

    for customer_id, rating, comment, platform in reviews_data:
        marketing.add_customer_review(
            customer_id, "resto_001", Decimal(str(rating)), comment, platform
        )

    # Résumé réputation
    reputation = marketing.get_reputation_summary()
    print(f"\n📊 RÉSUMÉ RÉPUTATION:")
    print(f"   Note moyenne: {reputation['average_rating']:.1f}/5")
    print(f"   Nombre d'avis: {reputation['total_reviews']}")
    print(f"   Tendance récente: {reputation['recent_trend']}")
    print(f"   Distribution des notes:")
    for note, count in reputation["rating_distribution"].items():
        stars = "⭐" * note
        print(f"     {stars}: {count} avis")

    # ROI Marketing
    roi = marketing.get_marketing_roi()
    print(f"\n💰 ROI MARKETING:")
    print(f"   Investissement total: {roi['total_spend']:.2f}€")
    print(f"   Revenus estimés: {roi['estimated_revenue']:.2f}€")
    print(f"   Ratio ROI: {roi['roi_ratio']:.1f}x")
    print(f"   Campagnes terminées: {roi['campaigns_completed']}")


def demo_finance_system():
    """Démonstration du système finance avancé."""
    print(f"\n\n💰 DÉMONSTRATION SYSTÈME FINANCE AVANCÉ")
    print("=" * 70)

    finance = FinanceManager()

    # Transactions d'exemple
    print(f"\n📝 ENREGISTREMENT DE TRANSACTIONS:")

    transactions_data = [
        ("Vente déjeuner", "sale", Decimal("450.00")),
        ("Achat viande", "purchase", Decimal("180.00")),
        ("Salaire chef", "salary", Decimal("2200.00")),
        ("Campagne marketing", "marketing", Decimal("350.00")),
        ("Vente dîner", "sale", Decimal("680.00")),
        ("Achat légumes", "purchase", Decimal("120.00")),
    ]

    for desc, t_type, amount in transactions_data:
        if t_type == "sale":
            transaction = finance.record_sale(amount)
        elif t_type == "purchase":
            transaction = finance.record_purchase(amount, "Fournisseur XYZ")
        elif t_type == "salary":
            transaction = finance.record_salary_payment(amount, "Chef Dupont")
        elif t_type == "marketing":
            transaction = finance.record_marketing_expense(amount, "Promotion Été")

        print(f"   ✅ {desc}: {amount}€ (ID: {transaction.id})")

    # Bilan comptable
    print(f"\n📊 BILAN COMPTABLE:")
    balance_sheet = finance.get_balance_sheet()

    print(f"\n   ACTIFS:")
    for account, balance in balance_sheet["assets"].items():
        if balance != 0:
            print(f"     • {account}: {balance:,.2f}€")
    print(f"   TOTAL ACTIFS: {balance_sheet['totals']['assets']:,.2f}€")

    print(f"\n   PASSIFS:")
    for account, balance in balance_sheet["liabilities"].items():
        if balance != 0:
            print(f"     • {account}: {balance:,.2f}€")
    print(f"   TOTAL PASSIFS: {balance_sheet['totals']['liabilities']:,.2f}€")

    print(f"\n   CAPITAUX PROPRES:")
    for account, balance in balance_sheet["equity"].items():
        if balance != 0:
            print(f"     • {account}: {balance:,.2f}€")
    print(f"   TOTAL CAPITAUX: {balance_sheet['totals']['equity']:,.2f}€")

    # Compte de résultat
    print(f"\n📈 COMPTE DE RÉSULTAT:")
    income_statement = finance.get_income_statement()

    print(f"\n   PRODUITS:")
    for account, amount in income_statement["revenues"].items():
        if amount != 0:
            print(f"     • {account}: {amount:,.2f}€")
    print(f"   TOTAL PRODUITS: {income_statement['totals']['revenues']:,.2f}€")

    print(f"\n   CHARGES:")
    for account, amount in income_statement["expenses"].items():
        if amount != 0:
            print(f"     • {account}: {amount:,.2f}€")
    print(f"   TOTAL CHARGES: {income_statement['totals']['expenses']:,.2f}€")

    print(f"\n   RÉSULTAT NET: {income_statement['totals']['net_profit']:,.2f}€")
    print(f"   MARGE NETTE: {income_statement['margins']['net_margin_rate']:.1%}")

    # Analyse de rentabilité par recette
    print(f"\n🍽️ ANALYSE RENTABILITÉ PAR RECETTE:")

    recipes_data = [
        (
            "burger_001",
            "Burger Classic",
            Decimal("12.50"),
            Decimal("4.20"),
            Decimal("2.80"),
            Decimal("1.50"),
        ),
        (
            "pizza_001",
            "Pizza Margherita",
            Decimal("11.00"),
            Decimal("3.80"),
            Decimal("2.20"),
            Decimal("1.40"),
        ),
        (
            "salad_001",
            "Salade César",
            Decimal("9.80"),
            Decimal("3.10"),
            Decimal("1.90"),
            Decimal("1.20"),
        ),
        (
            "pasta_001",
            "Pâtes Carbonara",
            Decimal("10.50"),
            Decimal("2.90"),
            Decimal("2.10"),
            Decimal("1.30"),
        ),
    ]

    for (
        recipe_id,
        name,
        price,
        ingredient_cost,
        labor_cost,
        overhead_cost,
    ) in recipes_data:
        finance.update_recipe_profitability(
            recipe_id, name, price, ingredient_cost, labor_cost, overhead_cost
        )

        # Simuler des ventes
        import random

        quantity_sold = random.randint(50, 150)
        for _ in range(quantity_sold):
            finance.record_recipe_sale(recipe_id)

    profitability_report = finance.get_recipe_profitability_report()

    print(
        f"\n   {'Recette':<20} | {'Prix':<8} | {'Coût':<8} | {'Marge':<8} | {'Taux':<8} | {'Volume':<8} | {'Profit':<10}"
    )
    print(
        f"   {'-' * 20} | {'-' * 8} | {'-' * 8} | {'-' * 8} | {'-' * 8} | {'-' * 8} | {'-' * 10}"
    )

    for recipe in profitability_report:
        print(
            f"   {recipe['recipe_name']:<20} | {recipe['selling_price']:>6.2f}€ | {recipe['total_cost']:>6.2f}€ | {recipe['unit_margin']:>6.2f}€ | {recipe['margin_rate']:>6.1%} | {recipe['quantity_sold']:>8} | {recipe['total_profit']:>8.2f}€"
        )

    # Prévision de trésorerie
    print(f"\n💰 PRÉVISION DE TRÉSORERIE (7 jours):")
    cash_flow = finance.get_cash_flow_forecast(7)

    print(f"   Trésorerie actuelle: {cash_flow['current_cash']:,.2f}€")
    print(f"   Flux quotidien moyen: {cash_flow['daily_net_flow']:+,.2f}€")

    print(f"\n   {'Jour':<6} | {'Date':<12} | {'Position':<12} | {'Flux':<10}")
    print(f"   {'-' * 6} | {'-' * 12} | {'-' * 12} | {'-' * 10}")

    for forecast in cash_flow["forecast"]:
        print(
            f"   J+{forecast['day']:<4} | {forecast['date'].strftime('%d/%m/%Y'):<12} | {forecast['cash_position']:>10.2f}€ | {forecast['daily_flow']:>+8.2f}€"
        )

    print(f"\n   Position minimale: {cash_flow['min_cash_position']:,.2f}€")
    print(f"   Position maximale: {cash_flow['max_cash_position']:,.2f}€")

    # Ratios financiers
    print(f"\n📊 RATIOS FINANCIERS:")
    ratios = finance.get_financial_ratios()

    print(f"   Liquidité: {ratios['current_ratio']:.2f}")
    print(f"   Marge nette: {ratios['net_margin']:.1%}")
    print(f"   ROE (Rentabilité capitaux): {ratios['roe']:.1%}")
    print(f"   ROA (Rentabilité actifs): {ratios['roa']:.1%}")
    print(f"   Taux d'endettement: {ratios['debt_ratio']:.1%}")


def demo_integration_complete():
    """Démonstration de l'intégration complète."""
    print(f"\n\n🎮 INTÉGRATION MARKETING + FINANCE")
    print("=" * 60)

    print(f"\n💡 SCÉNARIO: Restaurant 'Chez Mario' - Stratégie de croissance")
    print(f"   Objectif: Augmenter CA de 20% en 3 mois")
    print(f"   Budget marketing: 2,000€")
    print(f"   Investissement équipement: 5,000€")

    print(f"\n📈 PLAN D'ACTION INTÉGRÉ:")
    print(f"   1. MARKETING:")
    print(f"      • Campagne réseaux sociaux: 700€ (14 jours)")
    print(f"      • Programme fidélité: 900€ (30 jours)")
    print(f"      • Événement dégustation: 400€ (1 jour)")
    print(f"      → Impact attendu: +150 nouveaux clients/mois")

    print(f"\n   2. FINANCE:")
    print(f"      • Investissement four professionnel: 5,000€")
    print(f"      • Financement: Prêt bancaire 4.5%")
    print(f"      • ROI attendu: 18 mois")
    print(f"      → Impact: +20% capacité production")

    print(f"\n   3. RÉSULTATS ATTENDUS:")
    print(f"      • CA mensuel: 28,750€ → 34,500€ (+20%)")
    print(f"      • Nouveaux clients: +150/mois")
    print(f"      • Marge nette: 15.0% → 17.2%")
    print(f"      • Réputation: 4.2/5 → 4.6/5")

    print(f"\n📊 SUIVI KPIs:")
    print(f"   • ROI marketing: Suivi hebdomadaire")
    print(f"   • Trésorerie: Prévision quotidienne")
    print(f"   • Rentabilité plats: Analyse mensuelle")
    print(f"   • Satisfaction client: Monitoring continu")


def main():
    """Démonstration complète des modules avancés."""
    print("🎮 DÉMONSTRATION MODULES AVANCÉS FOODOPS PRO")
    print("=" * 80)

    try:
        demo_marketing_system()
        demo_finance_system()
        demo_integration_complete()

        print(f"\n\n🎉 MODULES AVANCÉS OPÉRATIONNELS !")
        print("=" * 60)
        print("✅ Marketing & Communication complet")
        print("✅ Finance avancée avec comptabilité")
        print("✅ Analyse rentabilité par recette")
        print("✅ Prévisions de trésorerie")
        print("✅ Gestion réputation en ligne")
        print("✅ ROI marketing mesurable")
        print("✅ Ratios financiers professionnels")
        print("")
        print("🎯 FoodOps Pro offre maintenant un niveau")
        print("   de réalisme professionnel complet !")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
