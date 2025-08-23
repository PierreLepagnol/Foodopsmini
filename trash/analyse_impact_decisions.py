#!/usr/bin/env python3
"""
Analyse complète de l'impact des décisions sur les KPIs dans FoodOps.
"""


def analyser_impact_decisions():
    """Analyse l'impact de chaque décision sur les KPIs."""
    print("📊 ANALYSE IMPACT DES DÉCISIONS SUR LES KPIs")
    print("=" * 80)

    decisions_impact = {
        "PRIX": {
            "description": "Prix de vente des plats",
            "impact_direct": {
                "Chiffre d'affaires": "DIRECT (+100%)",
                "Volume clients": "INVERSE (-50% si trop cher)",
                "Marge unitaire": "DIRECT (+100%)",
                "Part de marché": "INVERSE (-30% si prix élevé)",
            },
            "impact_indirect": {
                "Satisfaction client": "Dépend du rapport qualité/prix",
                "Réputation": "Long terme selon satisfaction",
                "Positionnement": "Définit le segment cible",
            },
            "optimisation": "Équilibrer volume vs marge selon stratégie",
        },
        "QUALITÉ INGRÉDIENTS": {
            "description": "Niveau qualité 1⭐ à 5⭐",
            "impact_direct": {
                "Coût matières": "DIRECT (+100% pour luxe vs économique)",
                "Satisfaction client": "DIRECT (+50% pour luxe)",
                "Attractivité": "VARIABLE selon segment (+60% foodies)",
                "Temps préparation": "DIRECT (+30% pour luxe)",
            },
            "impact_indirect": {
                "Réputation": "Évolution progressive (+3 points sur 10 tours)",
                "Fidélisation": "Clients premium plus fidèles",
                "Prix justifiés": "Qualité permet prix élevés",
                "Différenciation": "Avantage concurrentiel durable",
            },
            "optimisation": "Adapter au segment cible et budget",
        },
        "PERSONNEL": {
            "description": "Niveau staffing 0-3",
            "impact_direct": {
                "Capacité service": "DIRECT (+30% en renforcé)",
                "Coût personnel": "DIRECT (+50% en renforcé)",
                "Qualité service": "DIRECT (+20% satisfaction)",
                "Vitesse service": "DIRECT (-20% temps d'attente)",
            },
            "impact_indirect": {
                "Réputation": "Service impacte satisfaction",
                "Gestion pics": "Personnel renforcé gère mieux",
                "Flexibilité": "Adaptation aux variations",
                "Formation": "Personnel expérimenté = qualité",
            },
            "optimisation": "Équilibrer coût vs capacité vs qualité",
        },
        "SAISONNALITÉ": {
            "description": "Adaptation aux saisons",
            "impact_direct": {
                "Coût ingrédients": "VARIABLE (-30% à +40%)",
                "Qualité produits": "VARIABLE (±1⭐ selon saison)",
                "Demande segments": "VARIABLE (+30% familles été)",
                "Disponibilité": "VARIABLE (ruptures hors saison)",
            },
            "impact_indirect": {
                "Opportunités": "Menus saisonniers attractifs",
                "Communication": "Produits de saison = marketing",
                "Fidélisation": "Clients apprécient fraîcheur",
                "Différenciation": "Avantage vs concurrents",
            },
            "optimisation": "Anticiper et adapter l'offre",
        },
        "GESTION STOCKS": {
            "description": "Rotation FEFO et pertes",
            "impact_direct": {
                "Pertes matières": "DIRECT (2-5% selon gestion)",
                "Coût stockage": "DIRECT (frais conservation)",
                "Disponibilité": "DIRECT (ruptures = perte ventes)",
                "Fraîcheur": "DIRECT (impact qualité perçue)",
            },
            "impact_indirect": {
                "Réputation": "Ruptures = clients mécontents",
                "Flexibilité": "Stocks permettent adaptation",
                "Négociation": "Volumes = meilleurs prix",
                "Trésorerie": "Stocks immobilisent capital",
            },
            "optimisation": "Minimiser pertes et ruptures",
        },
    }

    # Affichage détaillé
    for decision, data in decisions_impact.items():
        print(f"\n🎯 {decision}")
        print("=" * 60)
        print(f"📝 {data['description']}")

        print("\n📈 IMPACTS DIRECTS:")
        for kpi, impact in data["impact_direct"].items():
            print(f"   • {kpi}: {impact}")

        print("\n🔄 IMPACTS INDIRECTS:")
        for kpi, impact in data["impact_indirect"].items():
            print(f"   • {kpi}: {impact}")

        print("\n💡 OPTIMISATION: {data['optimisation']}")


def analyser_kpis_cles():
    """Analyse les KPIs clés et leurs interdépendances."""
    print("\n\n📊 ANALYSE DES KPIs CLÉS")
    print("=" * 60)

    kpis = {
        "CHIFFRE D'AFFAIRES": {
            "formule": "Prix × Clients servis",
            "facteurs": ["Prix", "Attractivité", "Capacité", "Réputation"],
            "optimisation": "Équilibrer prix et volume",
            "benchmark": "Croissance 5-15% par tour",
        },
        "MARGE BRUTE": {
            "formule": "CA - Coût matières",
            "facteurs": ["Prix", "Qualité ingrédients", "Saisonnalité", "Pertes"],
            "optimisation": "Optimiser coût matières vs qualité",
            "benchmark": "40-70% selon positionnement",
        },
        "PROFIT NET": {
            "formule": "Marge brute - Personnel - Charges fixes",
            "facteurs": ["Marge", "Staffing", "Efficacité", "Volumes"],
            "optimisation": "Maximiser efficacité opérationnelle",
            "benchmark": "10-25% du CA",
        },
        "SATISFACTION CLIENT": {
            "formule": "f(Qualité, Prix, Service, Attente)",
            "facteurs": [
                "Qualité ingrédients",
                "Rapport qualité/prix",
                "Personnel",
                "Capacité",
            ],
            "optimisation": "Cohérence offre vs attentes segment",
            "benchmark": "3.5-4.5/5 selon positionnement",
        },
        "RÉPUTATION": {
            "formule": "Évolution lente basée sur satisfaction",
            "facteurs": ["Satisfaction", "Constance", "Temps", "Communication"],
            "optimisation": "Constance dans la qualité",
            "benchmark": "6-8/10 pour restaurant établi",
        },
        "PART DE MARCHÉ": {
            "formule": "Clients servis / Total marché",
            "facteurs": ["Attractivité", "Capacité", "Différenciation", "Prix"],
            "optimisation": "Cibler segments spécifiques",
            "benchmark": "15-35% selon nombre concurrents",
        },
    }

    for kpi, data in kpis.items():
        print("\n📊 {kpi}")
        print("-" * 40)
        print(f"📐 Formule: {data['formule']}")
        print(f"🎯 Facteurs clés: {', '.join(data['facteurs'])}")
        print(f"💡 Optimisation: {data['optimisation']}")
        print(f"📈 Benchmark: {data['benchmark']}")


def analyser_strategies_types():
    """Analyse les différents types de stratégies."""
    print("\n\n🎯 ANALYSE DES STRATÉGIES TYPES")
    print("=" * 60)

    strategies = {
        "ÉCONOMIQUE": {
            "description": "Volume maximum, prix bas",
            "decisions": {
                "Prix": "Bas (-20% vs marché)",
                "Qualité": "Économique (1-2⭐)",
                "Personnel": "Normal (2/3)",
                "Cible": "Étudiants, familles budget",
            },
            "kpis_cibles": {
                "Volume clients": "Maximum (30-40% marché)",
                "Marge unitaire": "Faible (30-40%)",
                "Satisfaction": "Correcte (2.5-3.5/5)",
                "Réputation": "Stable (4-6/10)",
            },
            "risques": ["Guerre des prix", "Marges faibles", "Vulnérabilité coûts"],
            "avantages": ["Volume élevé", "Barrière prix", "Marché large"],
        },
        "PREMIUM": {
            "description": "Équilibre qualité/prix optimisé",
            "decisions": {
                "Prix": "Élevé (+20% vs marché)",
                "Qualité": "Premium (3-4⭐)",
                "Personnel": "Renforcé (3/3)",
                "Cible": "Familles, foodies occasionnels",
            },
            "kpis_cibles": {
                "Volume clients": "Moyen (20-30% marché)",
                "Marge unitaire": "Élevée (50-65%)",
                "Satisfaction": "Bonne (3.5-4.5/5)",
                "Réputation": "Croissante (6-8/10)",
            },
            "risques": ["Concurrence intense", "Attentes élevées", "Coûts variables"],
            "avantages": ["Marge élevée", "Différenciation", "Fidélisation"],
        },
        "LUXE": {
            "description": "Excellence maximale, niche premium",
            "decisions": {
                "Prix": "Très élevé (+50% vs marché)",
                "Qualité": "Luxe (5⭐)",
                "Personnel": "Expert (3/3 + formation)",
                "Cible": "Foodies, occasions spéciales",
            },
            "kpis_cibles": {
                "Volume clients": "Faible (10-20% marché)",
                "Marge unitaire": "Très élevée (60-80%)",
                "Satisfaction": "Excellente (4.5-5/5)",
                "Réputation": "Élevée (8-10/10)",
            },
            "risques": ["Marché restreint", "Coûts élevés", "Sensibilité crise"],
            "avantages": ["Marge maximale", "Prestige", "Fidélité forte"],
        },
    }

    for strategie, data in strategies.items():
        print("\n🎯 STRATÉGIE {strategie}")
        print("=" * 50)
        print(f"📝 {data['description']}")

        print("\n🎮 DÉCISIONS CLÉS:")
        for decision, valeur in data["decisions"].items():
            print(f"   • {decision}: {valeur}")

        print("\n📊 KPIs CIBLES:")
        for kpi, valeur in data["kpis_cibles"].items():
            print(f"   • {kpi}: {valeur}")

        print("\n⚠️ RISQUES: {', '.join(data['risques'])}")
        print(f"✅ AVANTAGES: {', '.join(data['avantages'])}")


def analyser_interdependances():
    """Analyse les interdépendances entre décisions."""
    print("\n\n🔄 INTERDÉPENDANCES ENTRE DÉCISIONS")
    print("=" * 60)

    print("\n🎯 COHÉRENCE STRATÉGIQUE REQUISE:")
    print("-" * 40)

    coherences = [
        "Prix élevé → Qualité élevée (sinon satisfaction chute)",
        "Qualité luxe → Personnel expert (sinon gaspillage)",
        "Volume élevé → Capacité suffisante (sinon clients perdus)",
        "Saisonnalité → Adaptation menu (sinon coûts élevés)",
        "Réputation élevée → Constance qualité (sinon chute brutale)",
    ]

    for coherence in coherences:
        print(f"   • {coherence}")

    print("\n⚠️ PIÈGES À ÉVITER:")
    print("-" * 30)

    pieges = [
        "Prix bas + Qualité luxe = Perte assurée",
        "Personnel léger + Volume élevé = Service dégradé",
        "Stocks excessifs + Rotation lente = Pertes importantes",
        "Qualité variable = Réputation instable",
        "Ignorer saisonnalité = Coûts subis vs optimisés",
    ]

    for piege in pieges:
        print(f"   ❌ {piege}")

    print("\n✅ SYNERGIES POSITIVES:")
    print("-" * 30)

    synergies = [
        "Qualité premium + Prix justifié = Marge optimale",
        "Saisonnalité + Communication = Différenciation",
        "Personnel expert + Qualité luxe = Excellence perçue",
        "Réputation élevée + Prix premium = Acceptation client",
        "Stocks optimisés + Qualité constante = Efficacité maximale",
    ]

    for synergie in synergies:
        print(f"   ✅ {synergie}")


def main():
    """Analyse complète de l'impact des décisions."""
    analyser_impact_decisions()
    analyser_kpis_cles()
    analyser_strategies_types()
    analyser_interdependances()

    print("\n\n🎉 CONCLUSIONS CLÉS")
    print("=" * 40)
    print("✅ Chaque décision impacte plusieurs KPIs")
    print("✅ Cohérence stratégique = Clé du succès")
    print("✅ Interdépendances fortes entre décisions")
    print("✅ Plusieurs stratégies viables selon marché")
    print("✅ Optimisation continue nécessaire")
    print("")
    print("🎯 Le jeu enseigne la complexité réelle")
    print("   de la gestion d'entreprise !")


if __name__ == "__main__":
    main()
