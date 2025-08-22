#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FoodOps - Jeu de gestion de restaurant simplifié
Version de test qui fonctionne à coup sûr
"""

import random
import os


def clear_screen():
    """Efface l'écran."""
    os.system("cls" if os.name == "nt" else "clear")


def main():
    """Jeu principal."""
    # Initialisation
    restaurant = {
        "budget": 10000,
        "prix": 12.50,
        "qualite": 2,
        "personnel": 2,
        "reputation": 5.0,
        "tour": 1,
    }

    historique = []

    try:
        clear_screen()
        print("🍽️ FOODOPS - GESTION DE RESTAURANT")
        print("=" * 50)
        print("🎯 Gérez votre restaurant et battez la concurrence !")
        print("")
        print("🏪 Bienvenue dans votre nouveau restaurant !")
        print(f"💰 Budget de départ: {restaurant['budget']:,}€")
        print("")
        input("Appuyez sur Entrée pour commencer...")

        # Boucle de jeu
        while restaurant["tour"] <= 10 and restaurant["budget"] > -5000:
            clear_screen()

            # Affichage statut
            print("🍽️ FOODOPS - GESTION DE RESTAURANT")
            print("=" * 50)
            print(f"📊 STATUT - TOUR {restaurant['tour']}")
            print("-" * 30)
            print(f"💰 Budget: {restaurant['budget']:,}€")
            print(f"💵 Prix menu: {restaurant['prix']:.2f}€")
            print(f"⭐ Qualité: {restaurant['qualite']}/5")
            print(f"👥 Personnel: {restaurant['personnel']}/3")
            print(f"🌟 Réputation: {restaurant['reputation']:.1f}/10")
            print("")

            # Concurrents
            print("🏪 CONCURRENCE:")
            print("• Resto Rapide: 9.50€, Qualité 1⭐")
            print("• Bistrot Central: 13.20€, Qualité 3⭐")
            print("• Table Gourmande: 18.80€, Qualité 4⭐")
            print("")

            # Menu
            print("📋 MENU:")
            print("1. Prendre décisions et jouer le tour")
            print("2. Voir l'aide stratégique")
            print("3. Quitter")
            print("")

            choix = input("Votre choix (1-3): ").strip()

            if choix == "1":
                # Décisions
                print("")
                print("🎯 VOS DÉCISIONS:")
                print("-" * 20)

                try:
                    # Prix
                    nouveau_prix = input(
                        f"💵 Prix menu (actuel: {restaurant['prix']:.2f}€, Entrée=garder): "
                    )
                    if nouveau_prix.strip():
                        restaurant["prix"] = max(5.0, min(30.0, float(nouveau_prix)))

                    # Qualité
                    nouvelle_qualite = input(
                        f"⭐ Qualité 1-5 (actuel: {restaurant['qualite']}, Entrée=garder): "
                    )
                    if nouvelle_qualite.strip():
                        restaurant["qualite"] = max(1, min(5, int(nouvelle_qualite)))

                    # Personnel
                    nouveau_personnel = input(
                        f"👥 Personnel 1-3 (actuel: {restaurant['personnel']}, Entrée=garder): "
                    )
                    if nouveau_personnel.strip():
                        restaurant["personnel"] = max(1, min(3, int(nouveau_personnel)))

                except ValueError:
                    print("❌ Valeur invalide, paramètres conservés")

                # Simulation
                print("")

                # Calcul clients
                segments = {
                    "etudiants": {"taille": 150, "budget": 11.0},
                    "familles": {"taille": 180, "budget": 17.0},
                    "foodies": {"taille": 90, "budget": 25.0},
                }

                total_clients = 0
                for nom_segment, segment in segments.items():
                    ratio_prix = restaurant["prix"] / segment["budget"]
                    if ratio_prix > 1.5:
                        attractivite_prix = 0.1
                    elif ratio_prix > 1.2:
                        attractivite_prix = 0.4
                    elif ratio_prix > 0.8:
                        attractivite_prix = 1.0
                    else:
                        attractivite_prix = 0.8

                    attractivite_qualite = restaurant["qualite"] / 5.0
                    attractivite_reputation = restaurant["reputation"] / 10.0

                    attractivite_globale = (
                        attractivite_prix * 0.4
                        + attractivite_qualite * 0.3
                        + attractivite_reputation * 0.3
                    )

                    bruit = random.uniform(0.8, 1.2)
                    clients_segment = int(
                        segment["taille"] * attractivite_globale * bruit
                    )
                    total_clients += max(0, clients_segment)

                # Capacité
                capacites = {1: 120, 2: 150, 3: 180}
                capacite = capacites.get(restaurant["personnel"], 150)
                clients_servis = min(total_clients, capacite)
                clients_perdus = max(0, total_clients - capacite)

                # Finances
                chiffre_affaires = clients_servis * restaurant["prix"]

                modificateur_qualite = {1: 0.7, 2: 1.0, 3: 1.25, 4: 1.5, 5: 2.0}
                cout_ingredients = (
                    clients_servis
                    * 4.50
                    * modificateur_qualite.get(restaurant["qualite"], 1.0)
                )

                couts_personnel = {1: 2200, 2: 2800, 3: 3600}
                cout_personnel = couts_personnel.get(restaurant["personnel"], 2800)
                cout_charges = 1200
                cout_total = cout_ingredients + cout_personnel + cout_charges

                profit = chiffre_affaires - cout_total

                # Satisfaction
                satisfaction_base = 3.0
                facteur_prix = max(0.5, min(2.0, 15.0 / restaurant["prix"]))
                bonus_qualite = {1: -0.5, 2: 0.0, 3: 0.3, 4: 0.6, 5: 1.0}
                satisfaction = (
                    satisfaction_base
                    + (facteur_prix - 1) * 0.5
                    + bonus_qualite.get(restaurant["qualite"], 0.0)
                )
                satisfaction = max(1.0, min(5.0, satisfaction))

                # Réputation
                changement_reputation = (satisfaction - 3.0) * 0.1
                restaurant["reputation"] = max(
                    1.0, min(10.0, restaurant["reputation"] + changement_reputation)
                )

                # Part de marché
                marche_total = 420
                part_marche = (clients_servis / marche_total) * 100

                # Affichage résultats
                print("📈 RÉSULTATS DU TOUR")
                print("-" * 25)
                print(f"👥 Clients servis: {clients_servis}")
                if clients_perdus > 0:
                    print(
                        f"😞 Clients perdus: {clients_perdus} (capacité insuffisante)"
                    )

                print(f"💰 Chiffre d'affaires: {chiffre_affaires:,.0f}€")
                print(f"💸 Coûts totaux: {cout_total:,.0f}€")
                print(f"   • Ingrédients: {cout_ingredients:,.0f}€")
                print(f"   • Personnel: {cout_personnel:,.0f}€")
                print(f"   • Charges: {cout_charges:,.0f}€")

                couleur_profit = "💚" if profit > 0 else "❤️"
                print(f"{couleur_profit} Profit: {profit:+,.0f}€")

                print(f"😊 Satisfaction: {satisfaction:.1f}/5")
                print(f"📊 Part de marché: {part_marche:.1f}%")
                print("")

                # Mettre à jour
                restaurant["budget"] += profit
                restaurant["tour"] += 1

                # Messages
                if profit < -2000:
                    print("⚠️ Attention ! Grosses pertes ce tour !")
                elif profit > 1000:
                    print("🎉 Excellent tour ! Très bon profit !")

                if restaurant["tour"] <= 10:
                    input("\nAppuyez sur Entrée pour continuer...")

            elif choix == "2":
                # Aide
                clear_screen()
                print("🍽️ FOODOPS - AIDE STRATÉGIQUE")
                print("=" * 50)
                print("💡 AIDE STRATÉGIQUE")
                print("-" * 25)
                print("🎯 SEGMENTS CLIENTÈLE:")
                print("   • Étudiants (150): Budget 11€, sensibles au prix")
                print("   • Familles (180): Budget 17€, équilibre prix/qualité")
                print("   • Foodies (90): Budget 25€, privilégient la qualité")
                print("")
                print("⭐ NIVEAUX QUALITÉ:")
                print("   • 1⭐ Économique: -30% coût, -0.5 satisfaction")
                print("   • 2⭐ Standard: Prix de référence")
                print("   • 3⭐ Supérieur: +25% coût, +0.3 satisfaction")
                print("   • 4⭐ Premium: +50% coût, +0.6 satisfaction")
                print("   • 5⭐ Luxe: +100% coût, +1.0 satisfaction")
                print("")
                print("👥 PERSONNEL:")
                print("   • Niveau 1: 120 clients max, 2200€/mois")
                print("   • Niveau 2: 150 clients max, 2800€/mois")
                print("   • Niveau 3: 180 clients max, 3600€/mois")
                print("")
                input("Appuyez sur Entrée pour continuer...")

            elif choix == "3":
                break

            else:
                print("❌ Choix invalide")
                input("Appuyez sur Entrée pour continuer...")

        # Fin de partie
        clear_screen()
        print("🍽️ FOODOPS - FIN DE PARTIE")
        print("=" * 50)
        print("🏁 FIN DE PARTIE")
        print("=" * 30)
        print(f"🏪 Votre restaurant")
        print(f"📅 Tours joués: {restaurant['tour'] - 1}")
        print(f"💰 Budget final: {restaurant['budget']:,.0f}€")
        print(f"🌟 Réputation finale: {restaurant['reputation']:.1f}/10")
        print("")

        if restaurant["budget"] > 10000:
            print("🏆 EXCELLENT ! Vous avez fait du profit !")
        elif restaurant["budget"] > 5000:
            print("✅ BIEN JOUÉ ! Votre restaurant survit !")
        else:
            print("💪 COURAGE ! L'entrepreneuriat demande de la persévérance !")

        print("\n🎯 Merci d'avoir joué à FoodOps !")
        input("\nAppuyez sur Entrée pour quitter...")

    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 Au revoir ! Merci d'avoir joué à FoodOps !")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        input("Appuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()
