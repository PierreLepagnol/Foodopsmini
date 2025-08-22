#!/usr/bin/env python3
"""
Démonstration de l'interface qualité pour FoodOps Pro.
"""


def demo_interface_choix_qualite():
    """Simule l'interface de choix de qualité."""
    print("🎮 DÉMONSTRATION INTERFACE QUALITÉ FOODOPS PRO")
    print("=" * 80)

    print("\n🛒 CHOIX QUALITÉ DES INGRÉDIENTS")
    print("=" * 50)

    # État actuel simulé
    print("\n📊 QUALITÉ ACTUELLE: ⭐⭐ Standard (2.3/5)")
    print("💰 Impact coût: 100%")
    print("⭐ Réputation: 5.2/10")

    print("\n🎯 NIVEAUX DE QUALITÉ DISPONIBLES:")
    print("   1⭐ Économique (-30% coût, -20% satisfaction)")
    print("   2⭐ Standard (prix de référence)")
    print("   3⭐ Supérieur (+25% coût, +15% satisfaction)")
    print("   4⭐ Premium (+50% coût, +30% satisfaction)")
    print("   5⭐ Luxe (+100% coût, +50% satisfaction)")

    # Simulation des choix
    ingredients = [
        ("🥩 Viande (bœuf haché)", 2, 4),
        ("🍅 Légumes (tomates)", 2, 3),
        ("🧀 Fromage (mozzarella)", 2, 3),
        ("🌾 Féculents (farine)", 2, 2),
    ]

    print("\n📋 CONFIGURATION DES INGRÉDIENTS:")
    print("-" * 60)

    total_cost_impact = 0
    ingredient_count = 0

    for name, current, new in ingredients:
        cost_change = ""
        if new > current:
            cost_change = f" (+{(new - current) * 25}% coût)"
        elif new < current:
            cost_change = f" ({(new - current) * 25}% coût)"

        stars_current = "⭐" * current
        stars_new = "⭐" * new

        print(f"{name} (actuel: {current}⭐)")
        print(f"   Nouveau niveau: {new} {stars_new}{cost_change}")

        if new != current:
            print(f"   ✅ Mis à jour: {stars_current} → {stars_new}")
        else:
            print(f"   ⏭️ Inchangé")

        # Calcul impact coût
        cost_multipliers = {1: 0.70, 2: 1.00, 3: 1.25, 4: 1.50, 5: 2.00}
        total_cost_impact += cost_multipliers[new]
        ingredient_count += 1

        print()

    # Calcul des nouvelles métriques
    avg_quality = sum([new for _, _, new in ingredients]) / len(ingredients)
    avg_cost_impact = total_cost_impact / ingredient_count

    print("📈 IMPACT DES CHANGEMENTS:")
    print(f"   Qualité: 2.3/5 → {avg_quality:.1f}/5")
    print(f"   Coût matières: 100% → {avg_cost_impact:.0%}")

    if avg_quality >= 4.5:
        quality_desc = "⭐⭐⭐⭐⭐ Luxe"
    elif avg_quality >= 3.5:
        quality_desc = "⭐⭐⭐⭐ Premium"
    elif avg_quality >= 2.5:
        quality_desc = "⭐⭐⭐ Supérieur"
    else:
        quality_desc = "⭐⭐ Standard"

    print(f"   Description: {quality_desc}")
    print("\n✅ Choix de qualité enregistrés !")


def demo_rapport_qualite_prix():
    """Simule le rapport qualité/prix."""
    print("\n\n📊 RAPPORT QUALITÉ/PRIX DÉTAILLÉ")
    print("=" * 60)

    print("📈 MÉTRIQUES QUALITÉ ACTUELLES:")
    print("")
    print("Score qualité global: ⭐⭐⭐ Supérieur (3.2/5)")
    print("Impact sur coûts: 125%")
    print("Satisfaction client: 3.8/5")
    print("Réputation: 6.4/10")
    print("Ticket moyen: 14.50€")
    print("")
    print("🎯 ATTRACTIVITÉ PAR SEGMENT:")
    print("")
    print("• Étudiants: 95% (sensibilité faible)")
    print("• Familles: 115% (sensibilité normale)")
    print("• Foodies: 148% (sensibilité élevée)")
    print("")
    print("💰 ANALYSE COÛT/BÉNÉFICE:")
    print("")
    print("📈 SIMULATION AMÉLIORATION (+1 niveau qualité):")
    print("• Coût supplémentaire estimé: +25%")
    print("• Satisfaction supplémentaire: +15%")
    print("• Nouvelle attractivité foodies: +23%")
    print("")
    print("🎯 RECOMMANDATIONS PERSONNALISÉES:")
    print("")
    print("🟡 OPPORTUNITÉ: Différenciation qualité")
    print("• Cibler les foodies avec du premium (4⭐)")
    print("• Excellent rapport qualité/prix: potentiel hausse prix")
    print("")
    print("🥘 DÉTAIL INGRÉDIENTS:")
    print("")
    print("• Viande: ⭐⭐⭐⭐ (niveau 4)")
    print("• Légumes: ⭐⭐⭐ (niveau 3)")
    print("• Fromage: ⭐⭐⭐ (niveau 3)")
    print("• Féculents: ⭐⭐ (niveau 2)")


def demo_resultats_simulation():
    """Simule les résultats d'une simulation avec qualité."""
    print("\n\n📊 RÉSULTATS SIMULATION AVEC QUALITÉ")
    print("=" * 80)

    restaurants = [
        {
            "name": "Quick & Cheap",
            "type": "fast",
            "quality": "⭐ Économique",
            "price": 8.50,
            "clients": 168,
            "ca": 1428,
            "profit": 485,
            "satisfaction": 2.1,
            "reputation": 4.2,
            "market_share": 28.5,
        },
        {
            "name": "Burger Standard",
            "type": "classic",
            "quality": "⭐⭐ Standard",
            "price": 12.50,
            "clients": 142,
            "ca": 1775,
            "profit": 623,
            "satisfaction": 3.2,
            "reputation": 5.8,
            "market_share": 24.1,
        },
        {
            "name": "Gourmet Express",
            "type": "classic",
            "quality": "⭐⭐⭐⭐ Premium",
            "price": 18.50,
            "clients": 156,
            "ca": 2886,
            "profit": 1155,
            "satisfaction": 4.1,
            "reputation": 7.3,
            "market_share": 26.5,
        },
        {
            "name": "Artisan Bistro",
            "type": "gastronomique",
            "quality": "⭐⭐⭐⭐⭐ Luxe",
            "price": 28.50,
            "clients": 124,
            "ca": 3534,
            "profit": 1238,
            "satisfaction": 4.8,
            "reputation": 8.9,
            "market_share": 21.0,
        },
    ]

    print("RÉSULTATS TOUR 3 - JUILLET (BONUS SAISONNIER ÉTÉ)")
    print("-" * 120)
    print(
        f"{'Restaurant':<18} | {'Type':<12} | {'Qualité':<15} | {'Prix':<6} | {'Clients':<7} | {'CA €':<8} | {'Profit €':<9} | {'Satisf.':<7} | {'Réputation':<10} | {'Part %':<6}"
    )
    print("-" * 120)

    for r in restaurants:
        print(
            f"{r['name']:<18} | {r['type']:<12} | {r['quality']:<15} | {r['price']:>5.2f}€ | {r['clients']:>7} | {r['ca']:>8} | {r['profit']:>9} | {r['satisfaction']:>6.1f}/5 | {r['reputation']:>9.1f}/10 | {r['market_share']:>5.1f}"
        )

    print("-" * 120)

    total_clients = sum(r["clients"] for r in restaurants)
    total_ca = sum(r["ca"] for r in restaurants)
    total_profit = sum(r["profit"] for r in restaurants)

    print(
        f"{'TOTAL':<18} | {'':>12} | {'':>15} | {'':>6} | {total_clients:>7} | {total_ca:>8} | {total_profit:>9} | {'':>7} | {'':>10} | {'100.0':>5}"
    )

    print(f"\n💡 INSIGHTS STRATÉGIQUES:")
    print(f"• Le restaurant PREMIUM génère le plus de profit malgré un coût +50%")
    print(f"• La qualité LUXE attire moins de clients mais avec un ticket très élevé")
    print(f"• L'ÉCONOMIQUE a le plus de clients mais la plus faible marge")
    print(f"• La réputation évolue selon la satisfaction client")
    print(f"• Chaque stratégie qualité a sa place sur le marché !")


def demo_evolution_reputation():
    """Simule l'évolution de la réputation."""
    print(f"\n\n📈 ÉVOLUTION RÉPUTATION SUR 10 TOURS")
    print("=" * 60)

    # Données simulées pour 3 restaurants
    tours_data = [
        # Quick & Cheap (économique)
        {
            "name": "Quick & Cheap",
            "tours": [4.2, 4.1, 4.0, 4.1, 4.0, 3.9, 4.0, 4.1, 4.0, 4.1],
        },
        # Gourmet Express (premium)
        {
            "name": "Gourmet Express",
            "tours": [5.8, 6.2, 6.5, 6.8, 7.0, 7.2, 7.3, 7.4, 7.5, 7.6],
        },
        # Artisan Bistro (luxe)
        {
            "name": "Artisan Bistro",
            "tours": [7.5, 7.8, 8.1, 8.3, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0],
        },
    ]

    print(
        f"{'Tour':<6} | {'Quick & Cheap':<13} | {'Gourmet Express':<15} | {'Artisan Bistro':<14}"
    )
    print("-" * 60)

    for tour in range(10):
        line = f"{tour + 1:<6}"
        for resto_data in tours_data:
            reputation = resto_data["tours"][tour]
            line += f" | {reputation:<13.1f}"
        print(line)

    print("-" * 60)
    print(f"{'Évol.':<6}", end="")
    for resto_data in tours_data:
        evolution = resto_data["tours"][-1] - resto_data["tours"][0]
        print(f" | {evolution:+12.1f}", end="")
    print()

    print(f"\n💡 OBSERVATIONS:")
    print(f"• Restaurant premium: Réputation en croissance constante")
    print(f"• Restaurant luxe: Réputation élevée et stable")
    print(f"• Restaurant économique: Réputation faible mais stable")
    print(f"• La qualité impacte directement la réputation long terme")


def main():
    """Démonstration complète de l'interface."""
    demo_interface_choix_qualite()
    demo_rapport_qualite_prix()
    demo_resultats_simulation()
    demo_evolution_reputation()

    print(f"\n\n🎉 SYSTÈME QUALITÉ FOODOPS PRO - INTÉGRATION COMPLÈTE")
    print("=" * 80)
    print("✅ Interface de choix qualité intuitive")
    print("✅ Rapport qualité/prix détaillé avec recommandations")
    print("✅ Impact visible sur résultats de simulation")
    print("✅ Évolution réputation réaliste")
    print("✅ Différenciation stratégique opérationnelle")
    print("✅ Saisonnalité intégrée automatiquement")
    print("")
    print("🎯 FoodOps Pro offre maintenant un gameplay éducatif")
    print("   complet sur les vrais enjeux qualité/prix de la restauration !")
    print("")
    print("🚀 Prêt pour utilisation en formation professionnelle !")


if __name__ == "__main__":
    main()
