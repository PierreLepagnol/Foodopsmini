#!/usr/bin/env python3
"""
Version de test simple du jeu FoodOps Pro.
"""

import sys
from decimal import Decimal


def afficher_titre():
    """Affiche le titre du jeu."""
    print("=" * 60)
    print("🍽️  FOODOPS PRO 2024 - VERSION TEST  🍽️")
    print("=" * 60)
    print("Simulateur de Gestion de Restaurant")
    print("Version Éducative Professionnelle")
    print("=" * 60)


def afficher_scenario():
    """Affiche le scénario."""
    print("\n📋 SCÉNARIO: Challenge Entrepreneuriat")
    print("\n🎯 CONTEXTE:")
    print("Vous êtes un jeune entrepreneur qui souhaite ouvrir")
    print("son premier restaurant. Vous devez choisir un emplacement,")
    print("gérer vos finances et conquérir votre marché !")

    print("\n👥 SEGMENTS DE MARCHÉ:")
    print("• Étudiants (35%): Budget 11€ - Sensibles au prix")
    print("• Familles (40%): Budget 17€ - Équilibrés")
    print("• Foodies (25%): Budget 25€ - Exigent sur la qualité")


def choisir_commerce():
    """Choix du fonds de commerce."""
    print("\n" + "=" * 60)
    print("🏪 CHOIX DU FONDS DE COMMERCE")
    print("=" * 60)

    commerces = [
        {
            "nom": "Quick Campus",
            "type": "Quartier étudiant",
            "prix": 42000,
            "renovation": 8000,
            "couverts": 45,
            "loyer": 2800,
            "passage": "Élevé",
            "concurrence": 2,
        },
        {
            "nom": "La Table Familiale",
            "type": "Banlieue résidentielle",
            "prix": 58000,
            "renovation": 0,
            "couverts": 55,
            "loyer": 3200,
            "passage": "Moyen",
            "concurrence": 1,
        },
        {
            "nom": "Bistrot du Centre",
            "type": "Centre-ville",
            "prix": 95000,
            "renovation": 0,
            "couverts": 70,
            "loyer": 5200,
            "passage": "Très élevé",
            "concurrence": 3,
        },
    ]

    budget = 60000
    print(f"💰 Votre budget: {budget:,}€")
    print()

    for i, commerce in enumerate(commerces, 1):
        total = commerce["prix"] + commerce["renovation"]
        restant = budget - total

        print(f"{i}. {commerce['nom']}")
        print(f"   📍 {commerce['type']}")
        print(
            f"   💰 {commerce['prix']:,}€ + {commerce['renovation']:,}€ rénovation = {total:,}€"
        )
        print(
            f"   🏠 {commerce['couverts']} couverts - Loyer: {commerce['loyer']:,}€/mois"
        )
        print(
            f"   📈 Passage: {commerce['passage']} - Concurrence: {commerce['concurrence']}"
        )
        print(f"   💵 Budget restant: {restant:,}€")
        print()

    while True:
        try:
            print("Votre choix (1-3): ", end="", flush=True)
            choix = int(input())
            if 1 <= choix <= 3:
                return commerces[choix - 1], budget - (
                    commerces[choix - 1]["prix"] + commerces[choix - 1]["renovation"]
                )
            print("❌ Choix invalide. Veuillez choisir 1, 2 ou 3.")
        except ValueError:
            print("❌ Veuillez entrer un nombre.")
        except KeyboardInterrupt:
            print("\n👋 Partie annulée.")
            sys.exit(0)


def configurer_restaurant(commerce, budget_restant):
    """Configuration du restaurant."""
    print("\n" + "=" * 60)
    print("🍽️ CONFIGURATION DE VOTRE RESTAURANT")
    print("=" * 60)

    print("Nom de votre restaurant: ", end="", flush=True)
    nom = input().strip()
    if not nom:
        nom = "Mon Restaurant"

    print(f"\n✅ Restaurant '{nom}' créé !")
    print(f"📍 Emplacement: {commerce['nom']}")
    print(f"🏠 Capacité: {commerce['couverts']} couverts")
    print(f"💰 Trésorerie: {budget_restant:,}€")
    print(f"🏢 Loyer mensuel: {commerce['loyer']:,}€")

    # Menu de base
    print(f"\n📋 MENU DE BASE:")
    menu = [
        ("Burger Classique", 12.50),
        ("Pâtes Bolognaise", 16.00),
        ("Salade César", 14.00),
    ]

    for plat, prix in menu:
        print(f"• {plat}: {prix:.2f}€")

    return {
        "nom": nom,
        "commerce": commerce,
        "budget": budget_restant,
        "menu": menu,
        "capacite": commerce["couverts"],
    }


def tour_de_jeu(restaurant, tour):
    """Simulation d'un tour de jeu."""
    print(f"\n" + "=" * 60)
    print(f"🎯 TOUR {tour}/12")
    print("=" * 60)

    print(f"🏪 {restaurant['nom']}")
    print(f"💰 Trésorerie: {restaurant['budget']:,}€")
    print(f"🍽️ Capacité: {restaurant['capacite']} couverts")

    print(f"\n📋 DÉCISIONS DISPONIBLES:")
    print("1. 💰 Modifier les prix")
    print("2. 👥 Recruter du personnel")
    print("3. 📢 Campagne marketing")
    print("4. 📊 Voir les rapports")
    print("5. ▶️ Passer au tour suivant")

    while True:
        try:
            print("\nVotre choix (1-5): ", end="", flush=True)
            choix = int(input())

            if choix == 1:
                modifier_prix(restaurant)
            elif choix == 2:
                recruter_personnel(restaurant)
            elif choix == 3:
                campagne_marketing(restaurant)
            elif choix == 4:
                afficher_rapports(restaurant)
            elif choix == 5:
                break
            else:
                print("❌ Choix invalide.")

        except ValueError:
            print("❌ Veuillez entrer un nombre.")
        except KeyboardInterrupt:
            print("\n👋 Partie annulée.")
            sys.exit(0)

    # Simulation des résultats
    return simuler_resultats(restaurant, tour)


def modifier_prix(restaurant):
    """Modification des prix."""
    print(f"\n💰 MODIFICATION DES PRIX")
    print("Menu actuel:")

    for i, (plat, prix) in enumerate(restaurant["menu"], 1):
        print(f"{i}. {plat}: {prix:.2f}€")

    try:
        print("Quel plat modifier (1-3): ", end="", flush=True)
        choix = int(input())
        if 1 <= choix <= 3:
            plat, ancien_prix = restaurant["menu"][choix - 1]
            print(
                f"Nouveau prix pour {plat} (actuel: {ancien_prix:.2f}€): ",
                end="",
                flush=True,
            )
            nouveau_prix = float(input())

            restaurant["menu"][choix - 1] = (plat, nouveau_prix)
            changement = ((nouveau_prix - ancien_prix) / ancien_prix) * 100
            print(
                f"✅ Prix modifié: {ancien_prix:.2f}€ → {nouveau_prix:.2f}€ ({changement:+.1f}%)"
            )
        else:
            print("❌ Choix invalide.")
    except ValueError:
        print("❌ Prix invalide.")


def recruter_personnel(restaurant):
    """Recrutement de personnel."""
    print(f"\n👥 RECRUTEMENT")
    print("Postes disponibles:")
    print("1. Serveur - 1900€/mois")
    print("2. Cuisinier - 2300€/mois")
    print("3. Manager - 2800€/mois")

    try:
        print("Quel poste recruter (1-3): ", end="", flush=True)
        choix = int(input())

        postes = [("Serveur", 1900), ("Cuisinier", 2300), ("Manager", 2800)]

        if 1 <= choix <= 3:
            poste, salaire = postes[choix - 1]
            cout_total = salaire * 1.42  # Avec charges

            if restaurant["budget"] >= cout_total * 3:  # 3 mois de salaire
                restaurant["budget"] -= cout_total
                restaurant["capacite"] += 10  # Bonus de capacité
                print(f"✅ {poste} recruté ! Coût: {cout_total:.0f}€/mois")
                print(f"📈 Capacité augmentée de 10 couverts")
            else:
                print(f"❌ Budget insuffisant (besoin: {cout_total * 3:.0f}€)")
        else:
            print("❌ Choix invalide.")
    except ValueError:
        print("❌ Choix invalide.")


def campagne_marketing(restaurant):
    """Campagne marketing."""
    print(f"\n📢 CAMPAGNE MARKETING")
    print("Campagnes disponibles:")
    print("1. Flyers quartier - 200€")
    print("2. Radio locale - 800€")
    print("3. Réseaux sociaux - 300€")

    try:
        print("Quelle campagne (1-3): ", end="", flush=True)
        choix = int(input())

        campagnes = [
            ("Flyers quartier", 200, 10),
            ("Radio locale", 800, 25),
            ("Réseaux sociaux", 300, 15),
        ]

        if 1 <= choix <= 3:
            nom, cout, bonus = campagnes[choix - 1]

            if restaurant["budget"] >= cout:
                restaurant["budget"] -= cout
                print(f"✅ {nom} lancée ! Coût: {cout}€")
                print(f"📈 Bonus clientèle: +{bonus}% pour 2 tours")
            else:
                print(f"❌ Budget insuffisant (besoin: {cout}€)")
        else:
            print("❌ Choix invalide.")
    except ValueError:
        print("❌ Choix invalide.")


def afficher_rapports(restaurant):
    """Affichage des rapports."""
    print(f"\n📊 RAPPORTS FINANCIERS")
    print("=" * 40)

    # Estimation du CA mensuel
    ticket_moyen = sum(prix for _, prix in restaurant["menu"]) / len(restaurant["menu"])
    ca_estime = restaurant["capacite"] * ticket_moyen * 25  # 25 jours/mois

    # Coûts estimés
    cout_loyer = restaurant["commerce"]["loyer"]
    cout_personnel = 3000  # Estimation
    cout_matieres = ca_estime * 0.30  # 30% du CA

    benefice = ca_estime - cout_loyer - cout_personnel - cout_matieres

    print(f"💰 COMPTE DE RÉSULTAT ESTIMÉ:")
    print(f"Chiffre d'affaires:    {ca_estime:8.0f}€")
    print(f"Coût matières:        -{cout_matieres:8.0f}€")
    print(f"Charges personnel:    -{cout_personnel:8.0f}€")
    print(f"Loyer:                -{cout_loyer:8.0f}€")
    print("-" * 30)
    print(f"BÉNÉFICE:             {benefice:8.0f}€")

    print(f"\n📈 KPIs:")
    print(f"• Ticket moyen: {ticket_moyen:.2f}€")
    print(f"• Food cost: {(cout_matieres / ca_estime * 100):.1f}%")
    print(f"• Marge: {(benefice / ca_estime * 100):.1f}%")


def simuler_resultats(restaurant, tour):
    """Simulation des résultats du tour."""
    print(f"\n📊 RÉSULTATS DU TOUR {tour}")
    print("=" * 40)

    # Simulation simple
    demande = restaurant["capacite"] + 20  # Un peu plus que la capacité
    servi = min(demande, restaurant["capacite"])
    utilisation = (servi / restaurant["capacite"]) * 100

    ticket_moyen = sum(prix for _, prix in restaurant["menu"]) / len(restaurant["menu"])
    ca = servi * ticket_moyen

    # Coûts
    cout_matieres = ca * 0.30
    cout_fixe = restaurant["commerce"]["loyer"] / 4  # Par semaine
    benefice = ca - cout_matieres - cout_fixe

    restaurant["budget"] += benefice

    print(f"Demande:           {demande} clients")
    print(f"Clients servis:    {servi} clients")
    print(f"Taux utilisation:  {utilisation:.1f}%")
    print(f"Chiffre affaires:  {ca:.0f}€")
    print(f"Bénéfice:          {benefice:.0f}€")
    print(f"Nouvelle trésorerie: {restaurant['budget']:.0f}€")

    return restaurant["budget"] > 0  # Continue si positif


def main():
    """Jeu principal."""
    try:
        afficher_titre()
        afficher_scenario()

        # Phase d'acquisition
        commerce, budget_restant = choisir_commerce()
        restaurant = configurer_restaurant(commerce, budget_restant)

        # Boucle de jeu
        for tour in range(1, 13):
            if not tour_de_jeu(restaurant, tour):
                print("\n💸 FAILLITE ! Votre trésorerie est épuisée.")
                break

            if tour < 12:
                print("\nAppuyez sur Entrée pour continuer...", end="", flush=True)
                input()
        else:
            # Fin normale
            print(f"\n🎉 PARTIE TERMINÉE !")
            print(f"Trésorerie finale: {restaurant['budget']:,.0f}€")

            if restaurant["budget"] > 50000:
                print("🏆 EXCELLENT ! Vous êtes un entrepreneur accompli !")
            elif restaurant["budget"] > 20000:
                print("👍 BIEN JOUÉ ! Votre restaurant est rentable !")
            else:
                print("💪 PAS MAL ! Continuez à vous améliorer !")

        print(f"\n👋 Merci d'avoir joué à FoodOps Pro !")

    except KeyboardInterrupt:
        print(f"\n\n👋 Partie interrompue. À bientôt !")


if __name__ == "__main__":
    main()
