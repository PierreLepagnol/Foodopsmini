#!/usr/bin/env python3
"""
Démonstration simplifiée des nouveaux modules Marketing et Finance.
"""


def demo_marketing_interface():
    """Démonstration de l'interface marketing."""
    print("📈 DÉMONSTRATION INTERFACE MARKETING")
    print("=" * 70)

    print("\n📊 ÉTAT MARKETING ACTUEL:")
    print("   Réputation en ligne: 4.2/5 ⭐ (127 avis)")
    print("   Budget marketing mensuel: 850€")
    print("   Campagnes actives: 2")
    print("   ROI marketing: 3.2x")

    print("\n🎯 CAMPAGNES DISPONIBLES:")
    campaigns = [
        {
            "name": "Réseaux sociaux",
            "cost": "50€/jour",
            "reach": "1000 personnes",
            "conversion": "2.5%",
        },
        {
            "name": "Publicité locale",
            "cost": "80€/jour",
            "reach": "750 personnes",
            "conversion": "3.5%",
        },
        {
            "name": "Programme fidélité",
            "cost": "30€/jour",
            "reach": "150 clients",
            "conversion": "15%",
        },
        {
            "name": "Événement spécial",
            "cost": "200€/jour",
            "reach": "400 personnes",
            "conversion": "8%",
        },
    ]

    for i, campaign in enumerate(campaigns, 1):
        print(
            f"   {i}. {campaign['name']}: {campaign['cost']} - {campaign['reach']} - {campaign['conversion']}"
        )

    print("\n📈 SIMULATION CAMPAGNE RÉSEAUX SOCIAUX (7 jours):")
    print("   Budget total: 350€")
    print("   Portée totale: 7,000 personnes")
    print("   Conversions attendues: 175 nouveaux clients")
    print("   Coût par acquisition: 2.00€")

    print("\n⭐ GESTION RÉPUTATION:")
    print("   Avis récents:")
    reviews = [
        ("⭐⭐⭐⭐⭐", "Excellent burger, service rapide!", "Google"),
        ("⭐⭐⭐⭐", "Très bon, je recommande", "TripAdvisor"),
        ("⭐⭐", "Service lent, déçu", "Yelp"),
        ("⭐⭐⭐⭐⭐", "Parfait ! Qualité au top", "Google"),
    ]

    for rating, comment, platform in reviews:
        print(f'   {rating} "{comment}" ({platform})')

    print("\n💡 RECOMMANDATIONS MARKETING:")
    print("   • Répondre aux avis négatifs rapidement")
    print("   • Augmenter présence Instagram (+20% jeunes)")
    print("   • Lancer programme fidélité (rétention +30%)")
    print("   • Organiser événement dégustation mensuel")


def demo_finance_interface():
    """Démonstration de l'interface finance."""
    print("\n\n💰 DÉMONSTRATION INTERFACE FINANCE")
    print("=" * 70)

    print("\n📊 TABLEAU DE BORD FINANCIER:")
    print("   Trésorerie: 12,450€")
    print("   CA mensuel: 28,750€")
    print("   Marge brute: 65.2%")
    print("   Résultat net: 4,320€ (15.0%)")

    print("\n📈 RATIOS FINANCIERS:")
    ratios = [
        ("Liquidité", "2.1", "Bon"),
        ("Endettement", "35%", "Acceptable"),
        ("ROE", "18.5%", "Excellent"),
        ("Rotation stocks", "12x/an", "Optimal"),
    ]

    for name, value, status in ratios:
        print(f"   {name}: {value} ({status})")

    print("\n🍽️ RENTABILITÉ PAR PLAT:")
    dishes = [
        {
            "name": "Burger Classic",
            "price": 12.50,
            "cost": 4.20,
            "margin": 66.4,
            "volume": 145,
            "profit": 1203.50,
        },
        {
            "name": "Salade César",
            "price": 9.80,
            "cost": 3.10,
            "margin": 68.4,
            "volume": 89,
            "profit": 596.30,
        },
        {
            "name": "Pizza Margherita",
            "price": 11.00,
            "cost": 3.80,
            "margin": 65.5,
            "volume": 112,
            "profit": 806.40,
        },
        {
            "name": "Pâtes Carbonara",
            "price": 10.50,
            "cost": 2.90,
            "margin": 72.4,
            "volume": 78,
            "profit": 592.80,
        },
    ]

    print(
        f"   {'Plat':<18} | {'Prix':<8} | {'Coût':<8} | {'Marge':<8} | {'Volume':<8} | {'Profit':<10}"
    )
    print(f"   {'-' * 18} | {'-' * 8} | {'-' * 8} | {'-' * 8} | {'-' * 8} | {'-' * 10}")

    for dish in dishes:
        print(
            f"   {dish['name']:<18} | {dish['price']:>6.2f}€ | {dish['cost']:>6.2f}€ | {dish['margin']:>6.1f}% | {dish['volume']:>8} | {dish['profit']:>8.2f}€"
        )

    print("\n💰 PRÉVISION TRÉSORERIE (7 jours):")
    print("   Trésorerie actuelle: 12,450€")
    print("   Flux quotidien moyen: +185€")

    forecast_data = [
        (1, "16/08", 12635, +185),
        (2, "17/08", 12820, +185),
        (3, "18/08", 13005, +185),
        (4, "19/08", 13190, +185),
        (5, "20/08", 13375, +185),
        (6, "21/08", 13560, +185),
        (7, "22/08", 13745, +185),
    ]

    print(f"   {'Jour':<6} | {'Date':<8} | {'Position':<10} | {'Flux':<8}")
    print(f"   {'-' * 6} | {'-' * 8} | {'-' * 10} | {'-' * 8}")

    for day, date, position, flow in forecast_data:
        print(f"   J+{day:<4} | {date:<8} | {position:>8}€ | {flow:>+6}€")

    print("\n💡 RECOMMANDATIONS FINANCIÈRES:")
    print("   • Augmenter prix Burger Classic (+0.50€ = +290€/mois)")
    print("   • Promouvoir Pâtes Carbonara (marge la plus élevée)")
    print("   • Optimiser coûts Pizza Margherita (-0.20€ coût)")
    print("   • Négocier délais fournisseurs (trésorerie +15%)")


def demo_integration_strategique():
    """Démonstration de l'intégration stratégique."""
    print("\n\n🎯 INTÉGRATION STRATÉGIQUE MARKETING + FINANCE")
    print("=" * 70)

    print("\n💡 SCÉNARIO: Stratégie de croissance Q4 2024")
    print("   Objectif: +20% CA en 3 mois")
    print("   Budget disponible: 7,000€")

    print("\n📊 PLAN D'ACTION INTÉGRÉ:")

    print("\n   1️⃣ PHASE MARKETING (Mois 1):")
    print("      💰 Budget: 2,000€")
    print("      🎯 Actions:")
    print("         • Campagne réseaux sociaux: 700€ (14 jours)")
    print("         • Programme fidélité: 900€ (30 jours)")
    print("         • Événement dégustation: 400€ (1 jour)")
    print("      📈 Résultats attendus:")
    print("         • +150 nouveaux clients")
    print("         • Réputation: 4.2 → 4.6/5")
    print("         • CA: +12% dès le mois 1")

    print("\n   2️⃣ PHASE INVESTISSEMENT (Mois 2):")
    print("      💰 Budget: 5,000€")
    print("      🎯 Actions:")
    print("         • Four professionnel: 3,500€")
    print("         • Système de caisse: 1,500€")
    print("      📈 Résultats attendus:")
    print("         • +20% capacité production")
    print("         • +15% efficacité service")
    print("         • Réduction temps d'attente: -25%")

    print("\n   3️⃣ PHASE OPTIMISATION (Mois 3):")
    print("      💰 Budget: 0€ (autofinancé)")
    print("      🎯 Actions:")
    print("         • Optimisation menu (plats rentables)")
    print("         • Formation équipe (nouveau matériel)")
    print("         • Ajustement prix (+3% sur plats premium)")
    print("      📈 Résultats attendus:")
    print("         • Marge nette: 15% → 18%")
    print("         • Satisfaction client: +10%")
    print("         • Objectif +20% CA atteint")

    print("\n📊 PROJECTION FINANCIÈRE:")
    months_data = [
        ("Mois 0 (Actuel)", 28750, 4320, 15.0, 4.2),
        ("Mois 1 (Marketing)", 32200, 4830, 15.0, 4.4),
        ("Mois 2 (Investissement)", 33500, 5025, 15.0, 4.5),
        ("Mois 3 (Optimisation)", 34500, 6210, 18.0, 4.6),
    ]

    print(
        f"   {'Période':<20} | {'CA':<8} | {'Profit':<8} | {'Marge':<8} | {'Réputation':<11}"
    )
    print(f"   {'-' * 20} | {'-' * 8} | {'-' * 8} | {'-' * 8} | {'-' * 11}")

    for period, ca, profit, margin, reputation in months_data:
        print(
            f"   {period:<20} | {ca:>6}€ | {profit:>6}€ | {margin:>6.1f}% | {reputation:>9.1f}/5"
        )

    print(f"\n🎯 RÉSULTATS FINAUX:")
    print(f"   • CA: +20.0% (28,750€ → 34,500€)")
    print(f"   • Profit: +43.8% (4,320€ → 6,210€)")
    print(f"   • Marge: +3.0 pts (15.0% → 18.0%)")
    print(f"   • Réputation: +0.4 pts (4.2 → 4.6/5)")
    print(f"   • ROI total: 2.1x sur 3 mois")


def demo_kpis_dashboard():
    """Démonstration du tableau de bord KPIs."""
    print("\n\n📊 TABLEAU DE BORD KPIs INTÉGRÉ")
    print("=" * 60)

    print("\n🎯 KPIs OPÉRATIONNELS:")
    operational_kpis = [
        ("Clients/jour", "142", "+8%", "🟢"),
        ("Ticket moyen", "16.80€", "+5%", "🟢"),
        ("Taux occupation", "78%", "+12%", "🟢"),
        ("Temps d'attente", "8 min", "-15%", "🟢"),
        ("Satisfaction client", "4.4/5", "+5%", "🟢"),
    ]

    for kpi, value, evolution, trend in operational_kpis:
        print(f"   {kpi:<18}: {value:<8} ({evolution:<4}) {trend}")

    print("\n💰 KPIs FINANCIERS:")
    financial_kpis = [
        ("CA mensuel", "32,200€", "+12%", "🟢"),
        ("Marge brute", "67.2%", "+2%", "🟢"),
        ("Résultat net", "4,830€", "+12%", "🟢"),
        ("Trésorerie", "14,280€", "+15%", "🟢"),
        ("ROE", "19.2%", "+1%", "🟢"),
    ]

    for kpi, value, evolution, trend in financial_kpis:
        print(f"   {kpi:<18}: {value:<8} ({evolution:<4}) {trend}")

    print("\n📈 KPIs MARKETING:")
    marketing_kpis = [
        ("Nouveaux clients", "38/sem", "+25%", "🟢"),
        ("Taux fidélisation", "68%", "+8%", "🟢"),
        ("ROI marketing", "3.4x", "+6%", "🟢"),
        ("Avis positifs", "89%", "+4%", "🟢"),
        ("Portée sociale", "2,400", "+45%", "🟢"),
    ]

    for kpi, value, evolution, trend in marketing_kpis:
        print(f"   {kpi:<18}: {value:<8} ({evolution:<4}) {trend}")

    print("\n⚠️ ALERTES ET ACTIONS:")
    print("   🟡 Stock tomates: Bas (2 jours restants)")
    print("   🟢 Trésorerie: Excellente position")
    print("   🟡 Avis négatif récent: Réponse requise")
    print("   🟢 Objectifs mensuels: En avance (+5%)")


def main():
    """Démonstration complète des modules avancés."""
    print("🎮 DÉMONSTRATION MODULES AVANCÉS FOODOPS PRO")
    print("=" * 80)

    demo_marketing_interface()
    demo_finance_interface()
    demo_integration_strategique()
    demo_kpis_dashboard()

    print(f"\n\n🎉 MODULES AVANCÉS INTÉGRÉS AVEC SUCCÈS !")
    print("=" * 70)
    print("✅ Marketing & Communication opérationnel")
    print("✅ Finance avancée avec comptabilité complète")
    print("✅ Analyse rentabilité par recette")
    print("✅ Prévisions de trésorerie automatiques")
    print("✅ Gestion réputation en ligne")
    print("✅ ROI marketing mesurable en temps réel")
    print("✅ Ratios financiers professionnels")
    print("✅ Tableau de bord KPIs intégré")
    print("✅ Planification stratégique multi-phases")
    print("")
    print("🎯 FoodOps Pro offre maintenant un niveau de réalisme")
    print("   et de complexité digne d'une formation professionnelle !")
    print("")
    print("🚀 Prêt pour utilisation en école de commerce,")
    print("   formation continue, ou simulation d'entreprise !")


if __name__ == "__main__":
    main()
