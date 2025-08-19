#!/usr/bin/env python3
"""
FoodOps Demo Direct - Version de test sans dépendances.
"""

import random
from decimal import Decimal

class Restaurant:
    """Restaurant simplifié pour démonstration."""
    
    def __init__(self, name="Mon Restaurant"):
        self.name = name
        self.budget = 10000
        self.price = 12.50
        self.quality_level = 2  # 1-5
        self.staff_level = 2    # 1-3
        self.reputation = 5.0   # 1-10
        self.turn = 1
        
        # Historique
        self.history = []
        
    def get_capacity(self):
        """Calcule la capacité selon le personnel."""
        capacities = {1: 120, 2: 150, 3: 180}
        return capacities.get(self.staff_level, 150)
    
    def get_staff_cost(self):
        """Calcule le coût du personnel."""
        costs = {1: 2200, 2: 2800, 3: 3600}
        return costs.get(self.staff_level, 2800)
    
    def get_quality_cost_modifier(self):
        """Modificateur de coût selon la qualité."""
        modifiers = {1: 0.7, 2: 1.0, 3: 1.25, 4: 1.5, 5: 2.0}
        return modifiers.get(self.quality_level, 1.0)
    
    def get_quality_satisfaction_bonus(self):
        """Bonus de satisfaction selon la qualité."""
        bonuses = {1: -0.5, 2: 0.0, 3: 0.3, 4: 0.6, 5: 1.0}
        return bonuses.get(self.quality_level, 0.0)

class MarketSimulator:
    """Simulateur de marché simplifié."""
    
    def __init__(self):
        self.segments = {
            "étudiants": {"size": 150, "budget": 11.0, "price_sensitivity": 1.8},
            "familles": {"size": 180, "budget": 17.0, "price_sensitivity": 1.2},
            "foodies": {"size": 90, "budget": 25.0, "price_sensitivity": 0.6}
        }
        
        self.competitors = [
            {"name": "Resto Rapide", "price": 9.50, "quality": 1},
            {"name": "Bistrot Central", "price": 13.20, "quality": 3},
            {"name": "Table Gourmande", "price": 18.80, "quality": 4}
        ]
    
    def simulate_turn(self, restaurant):
        """Simule un tour de marché."""
        total_customers = 0
        total_revenue = 0
        
        # Calculer l'attractivité pour chaque segment
        for segment_name, segment in self.segments.items():
            customers = self._calculate_segment_customers(restaurant, segment_name, segment)
            total_customers += customers
            total_revenue += customers * restaurant.price
        
        # Limiter par la capacité
        capacity = restaurant.get_capacity()
        if total_customers > capacity:
            lost_customers = total_customers - capacity
            total_customers = capacity
            total_revenue = capacity * restaurant.price
        else:
            lost_customers = 0
        
        # Calculer les coûts
        ingredient_cost_per_meal = 4.50 * restaurant.get_quality_cost_modifier()
        total_ingredient_cost = total_customers * ingredient_cost_per_meal
        staff_cost = restaurant.get_staff_cost()
        overhead_cost = 1200
        total_costs = total_ingredient_cost + staff_cost + overhead_cost
        
        # Profit
        profit = total_revenue - total_costs
        
        # Satisfaction client
        base_satisfaction = 3.0
        price_factor = max(0.5, min(2.0, 15.0 / restaurant.price))
        quality_bonus = restaurant.get_quality_satisfaction_bonus()
        satisfaction = base_satisfaction + (price_factor - 1) * 0.5 + quality_bonus
        satisfaction = max(1.0, min(5.0, satisfaction))
        
        # Mettre à jour la réputation
        reputation_change = (satisfaction - 3.0) * 0.1
        restaurant.reputation = max(1.0, min(10.0, restaurant.reputation + reputation_change))
        
        # Calculer la part de marché
        total_market = sum(segment["size"] for segment in self.segments.values())
        market_share = (total_customers / total_market) * 100
        
        return {
            "customers": total_customers,
            "lost_customers": lost_customers,
            "revenue": total_revenue,
            "costs": total_costs,
            "profit": profit,
            "satisfaction": satisfaction,
            "market_share": market_share,
            "ingredient_cost": total_ingredient_cost,
            "staff_cost": staff_cost,
            "overhead_cost": overhead_cost
        }
    
    def _calculate_segment_customers(self, restaurant, segment_name, segment):
        """Calcule les clients d'un segment."""
        # Attractivité basée sur le prix
        price_ratio = restaurant.price / segment["budget"]
        if price_ratio > 1.5:
            price_attractiveness = 0.1
        elif price_ratio > 1.2:
            price_attractiveness = 0.4
        elif price_ratio > 0.8:
            price_attractiveness = 1.0
        else:
            price_attractiveness = 0.8
        
        # Attractivité basée sur la qualité
        quality_attractiveness = restaurant.quality_level / 5.0
        
        # Attractivité basée sur la réputation
        reputation_attractiveness = restaurant.reputation / 10.0
        
        # Attractivité globale
        overall_attractiveness = (
            price_attractiveness * 0.4 +
            quality_attractiveness * 0.3 +
            reputation_attractiveness * 0.3
        )
        
        # Ajouter du bruit
        noise = random.uniform(0.8, 1.2)
        
        # Calculer les clients
        base_customers = segment["size"] * overall_attractiveness * noise
        return max(0, int(base_customers))

class GameInterface:
    """Interface de jeu simplifiée."""
    
    def __init__(self):
        self.restaurant = Restaurant()
        self.market = MarketSimulator()
    
    def show_welcome(self):
        """Affiche l'écran d'accueil."""
        print("🍽️ FOODOPS PRO - DÉMONSTRATION")
        print("=" * 50)
        print("🎯 Simulateur de gestion de restaurant")
        print("📚 Version de test simplifiée")
        print("")
        print(f"🏪 Bienvenue dans votre restaurant : {self.restaurant.name}")
        print(f"💰 Budget initial : {self.restaurant.budget:,.0f}€")
        print("")
    
    def show_status(self):
        """Affiche le statut actuel."""
        print(f"\n📊 STATUT RESTAURANT - TOUR {self.restaurant.turn}")
        print("=" * 40)
        print(f"💰 Budget: {self.restaurant.budget:,.0f}€")
        print(f"💵 Prix menu: {self.restaurant.price:.2f}€")
        print(f"⭐ Qualité: {self.restaurant.quality_level}/5")
        print(f"👥 Personnel: Niveau {self.restaurant.staff_level}/3")
        print(f"🌟 Réputation: {self.restaurant.reputation:.1f}/10")
        print(f"🏢 Capacité: {self.restaurant.get_capacity()} clients")
    
    def get_decisions(self):
        """Récupère les décisions du joueur."""
        print(f"\n🎯 DÉCISIONS TOUR {self.restaurant.turn}")
        print("=" * 30)
        
        try:
            # Prix
            new_price = input(f"💵 Prix menu (actuel: {self.restaurant.price:.2f}€): ")
            if new_price.strip():
                self.restaurant.price = max(5.0, min(30.0, float(new_price)))
            
            # Qualité
            new_quality = input(f"⭐ Niveau qualité 1-5 (actuel: {self.restaurant.quality_level}): ")
            if new_quality.strip():
                self.restaurant.quality_level = max(1, min(5, int(new_quality)))
            
            # Personnel
            new_staff = input(f"👥 Niveau personnel 1-3 (actuel: {self.restaurant.staff_level}): ")
            if new_staff.strip():
                self.restaurant.staff_level = max(1, min(3, int(new_staff)))
            
            return True
            
        except (ValueError, KeyboardInterrupt):
            print("❌ Entrée invalide, valeurs conservées")
            return True
        except EOFError:
            return False
    
    def simulate_and_show_results(self):
        """Simule le tour et affiche les résultats."""
        results = self.market.simulate_turn(self.restaurant)
        
        print(f"\n📈 RÉSULTATS TOUR {self.restaurant.turn}")
        print("=" * 35)
        print(f"👥 Clients servis: {results['customers']}")
        if results['lost_customers'] > 0:
            print(f"😞 Clients perdus: {results['lost_customers']} (capacité insuffisante)")
        
        print(f"💰 Chiffre d'affaires: {results['revenue']:,.0f}€")
        print(f"💸 Coûts totaux: {results['costs']:,.0f}€")
        print(f"   • Ingrédients: {results['ingredient_cost']:,.0f}€")
        print(f"   • Personnel: {results['staff_cost']:,.0f}€")
        print(f"   • Charges: {results['overhead_cost']:,.0f}€")
        
        profit_color = "💚" if results['profit'] > 0 else "❤️"
        print(f"{profit_color} Profit: {results['profit']:+,.0f}€")
        
        print(f"😊 Satisfaction: {results['satisfaction']:.1f}/5")
        print(f"📊 Part de marché: {results['market_share']:.1f}%")
        
        # Mettre à jour le budget
        self.restaurant.budget += results['profit']
        
        # Sauvegarder l'historique
        self.restaurant.history.append(results)
        
        return results
    
    def show_competitors(self):
        """Affiche les concurrents."""
        print(f"\n🏪 CONCURRENCE")
        print("=" * 20)
        for comp in self.market.competitors:
            print(f"• {comp['name']}: {comp['price']:.2f}€, Qualité {comp['quality']}/5")
    
    def show_help(self):
        """Affiche l'aide."""
        print(f"\n💡 AIDE STRATÉGIQUE")
        print("=" * 25)
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
    
    def play(self):
        """Boucle de jeu principale."""
        self.show_welcome()
        
        while self.restaurant.turn <= 10 and self.restaurant.budget > -5000:
            self.show_status()
            self.show_competitors()
            
            print(f"\n📋 MENU")
            print("1. Prendre décisions et jouer le tour")
            print("2. Voir l'aide stratégique")
            print("3. Quitter")
            
            try:
                choice = input("\nVotre choix (1-3): ").strip()
                
                if choice == "1":
                    if self.get_decisions():
                        results = self.simulate_and_show_results()
                        
                        if results['profit'] < -2000:
                            print("\n⚠️ Attention ! Grosses pertes ce tour !")
                        elif results['profit'] > 1000:
                            print("\n🎉 Excellent tour ! Très bon profit !")
                        
                        self.restaurant.turn += 1
                        
                        if self.restaurant.turn <= 10:
                            input("\nAppuyez sur Entrée pour continuer...")
                    else:
                        break
                        
                elif choice == "2":
                    self.show_help()
                    input("\nAppuyez sur Entrée pour continuer...")
                    
                elif choice == "3":
                    break
                    
                else:
                    print("❌ Choix invalide")
                    
            except (KeyboardInterrupt, EOFError):
                break
        
        # Fin de partie
        self.show_final_results()
    
    def show_final_results(self):
        """Affiche les résultats finaux."""
        print(f"\n🏁 FIN DE PARTIE")
        print("=" * 30)
        print(f"🏪 Restaurant: {self.restaurant.name}")
        print(f"📅 Tours joués: {self.restaurant.turn - 1}")
        print(f"💰 Budget final: {self.restaurant.budget:,.0f}€")
        print(f"🌟 Réputation finale: {self.restaurant.reputation:.1f}/10")
        
        if self.restaurant.history:
            total_profit = sum(r['profit'] for r in self.restaurant.history)
            avg_customers = sum(r['customers'] for r in self.restaurant.history) / len(self.restaurant.history)
            avg_satisfaction = sum(r['satisfaction'] for r in self.restaurant.history) / len(self.restaurant.history)
            
            print(f"💚 Profit total: {total_profit:+,.0f}€")
            print(f"👥 Clients moyens/tour: {avg_customers:.0f}")
            print(f"😊 Satisfaction moyenne: {avg_satisfaction:.1f}/5")
            
            if total_profit > 5000:
                print("\n🏆 EXCELLENT ! Vous êtes un vrai entrepreneur !")
            elif total_profit > 0:
                print("\n✅ BIEN JOUÉ ! Votre restaurant est rentable !")
            else:
                print("\n💪 COURAGE ! L'entrepreneuriat demande de la persévérance !")
        
        print(f"\n🎯 Merci d'avoir joué à FoodOps Pro !")

def main():
    """Point d'entrée principal."""
    try:
        game = GameInterface()
        game.play()
    except KeyboardInterrupt:
        print(f"\n\n👋 Au revoir ! Merci d'avoir testé FoodOps Pro !")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("💡 Veuillez signaler ce problème aux développeurs.")

if __name__ == "__main__":
    main()
