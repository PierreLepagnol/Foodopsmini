#!/usr/bin/env python3
"""
Version simplifiée de FoodOps Pro pour jouer sans dépendances.
"""

import random
from decimal import Decimal

class Restaurant:
    """Restaurant simplifié pour le jeu."""
    
    def __init__(self, name="Mon Restaurant"):
        self.name = name
        self.budget = Decimal("10000")
        self.price = Decimal("12.50")
        self.quality_level = 2  # 1-5
        self.staff_level = 2    # 1-3
        self.reputation = Decimal("5.0")  # 1-10
        
        # Historique
        self.turn_history = []
        self.total_revenue = Decimal("0")
        self.total_profit = Decimal("0")
    
    def get_capacity(self):
        """Capacité selon le niveau de personnel."""
        capacities = {1: 120, 2: 150, 3: 180}
        return capacities[self.staff_level]
    
    def get_staff_cost(self):
        """Coût du personnel."""
        costs = {1: Decimal("2200"), 2: Decimal("2800"), 3: Decimal("3600")}
        return costs[self.staff_level]
    
    def get_ingredient_cost(self):
        """Coût des ingrédients selon la qualité."""
        base_cost = Decimal("4.20")
        quality_multipliers = {1: 0.7, 2: 1.0, 3: 1.25, 4: 1.5, 5: 2.0}
        return base_cost * Decimal(str(quality_multipliers[self.quality_level]))

class MarketSimulator:
    """Simulateur de marché simplifié."""
    
    def __init__(self):
        self.segments = {
            "étudiants": {"size": 150, "budget": 11.0, "price_sensitivity": 1.8, "quality_preference": 0.7},
            "familles": {"size": 180, "budget": 17.0, "price_sensitivity": 1.2, "quality_preference": 1.1},
            "foodies": {"size": 90, "budget": 25.0, "price_sensitivity": 0.6, "quality_preference": 1.8}
        }
        
        self.competitors = [
            {"name": "Resto Rapide", "price": 9.50, "quality": 1},
            {"name": "Bistrot Central", "price": 13.20, "quality": 3},
            {"name": "Table Gourmande", "price": 18.80, "quality": 4}
        ]
    
    def simulate_demand(self, restaurant):
        """Simule la demande pour le restaurant."""
        total_clients = 0
        segment_details = {}
        
        for segment_name, segment in self.segments.items():
            # Attractivité basée sur prix et qualité
            price_factor = self._calculate_price_attractiveness(
                float(restaurant.price), segment["budget"], segment["price_sensitivity"]
            )
            
            quality_factor = self._calculate_quality_attractiveness(
                restaurant.quality_level, segment["quality_preference"]
            )
            
            # Facteur de réputation
            reputation_factor = float(restaurant.reputation) / 10.0
            
            # Attractivité totale
            attractiveness = price_factor * quality_factor * reputation_factor
            
            # Clients du segment
            base_demand = segment["size"] * 0.3  # 30% du segment potentiel
            segment_clients = int(base_demand * attractiveness * random.uniform(0.8, 1.2))
            
            # Limiter par la capacité
            segment_clients = min(segment_clients, restaurant.get_capacity() // 3)
            
            total_clients += segment_clients
            segment_details[segment_name] = segment_clients
        
        # Limiter par la capacité totale
        total_clients = min(total_clients, restaurant.get_capacity())
        
        return total_clients, segment_details
    
    def _calculate_price_attractiveness(self, price, budget, sensitivity):
        """Calcule l'attractivité basée sur le prix."""
        if price > budget * 1.5:
            return 0.1  # Trop cher
        
        price_ratio = price / budget
        if price_ratio <= 0.8:
            return 1.2  # Bon prix
        elif price_ratio <= 1.0:
            return 1.0  # Prix correct
        else:
            return max(0.3, 1.0 - (price_ratio - 1.0) * sensitivity)
    
    def _calculate_quality_attractiveness(self, quality_level, preference):
        """Calcule l'attractivité basée sur la qualité."""
        quality_factor = quality_level / 3.0  # Normaliser sur 3
        return max(0.5, min(1.5, quality_factor * preference))

class GameEngine:
    """Moteur de jeu principal."""
    
    def __init__(self):
        self.restaurant = None
        self.market = MarketSimulator()
        self.turn = 0
        self.max_turns = 10
    
    def start_game(self):
        """Démarre une nouvelle partie."""
        print("🍔 BIENVENUE DANS FOODOPS PRO !")
        print("=" * 50)
        
        # Création du restaurant
        name = input("Nom de votre restaurant (ou Entrée pour 'Mon Restaurant'): ").strip()
        if not name:
            name = "Mon Restaurant"
        
        self.restaurant = Restaurant(name)
        
        print(f"\n🏪 Restaurant '{self.restaurant.name}' créé !")
        print(f"💰 Budget initial: {self.restaurant.budget}€")
        print(f"🎯 Objectif: Survivre {self.max_turns} tours et maximiser les profits")
        
        # Boucle de jeu
        while self.turn < self.max_turns:
            self.turn += 1
            print(f"\n" + "="*60)
            print(f"🎮 TOUR {self.turn}/{self.max_turns}")
            print("="*60)
            
            if not self.play_turn():
                break
        
        self.end_game()
    
    def play_turn(self):
        """Joue un tour."""
        # Afficher l'état actuel
        self.show_status()
        
        # Prendre les décisions
        if not self.make_decisions():
            return False
        
        # Simuler le marché
        clients, segment_details = self.market.simulate_demand(self.restaurant)
        
        # Calculer les résultats
        results = self.calculate_results(clients)
        
        # Afficher les résultats
        self.show_results(results, segment_details)
        
        # Mettre à jour l'historique
        self.restaurant.turn_history.append(results)
        
        # Vérifier la faillite
        if self.restaurant.budget <= 0:
            print("\n💥 FAILLITE ! Votre budget est épuisé.")
            return False
        
        input("\nAppuyez sur Entrée pour continuer...")
        return True
    
    def show_status(self):
        """Affiche l'état actuel du restaurant."""
        print(f"\n📊 ÉTAT DE VOTRE RESTAURANT:")
        print(f"   💰 Budget: {self.restaurant.budget:.2f}€")
        print(f"   💵 Prix actuel: {self.restaurant.price}€")
        print(f"   ⭐ Qualité: {self.restaurant.quality_level}/5")
        print(f"   👥 Personnel: Niveau {self.restaurant.staff_level} (capacité: {self.restaurant.get_capacity()} clients)")
        print(f"   🌟 Réputation: {self.restaurant.reputation:.1f}/10")
        
        if self.restaurant.turn_history:
            last_turn = self.restaurant.turn_history[-1]
            print(f"   📈 Dernier profit: {last_turn['profit']:+.2f}€")
    
    def make_decisions(self):
        """Interface pour prendre les décisions."""
        print(f"\n🎯 VOS DÉCISIONS POUR CE TOUR:")
        
        try:
            # Prix
            print(f"\n💵 PRIX DU MENU (actuel: {self.restaurant.price}€)")
            print("   Segments clientèle: Étudiants (~11€), Familles (~17€), Foodies (~25€)")
            new_price = input(f"Nouveau prix (ou Entrée pour garder {self.restaurant.price}€): ").strip()
            
            if new_price:
                price = float(new_price)
                if 5.0 <= price <= 50.0:
                    self.restaurant.price = Decimal(str(price))
                else:
                    print("⚠️ Prix doit être entre 5€ et 50€")
            
            # Qualité
            print(f"\n⭐ QUALITÉ DES INGRÉDIENTS (actuel: {self.restaurant.quality_level}/5)")
            print("   1⭐ Économique (-30% coût, -20% satisfaction)")
            print("   2⭐ Standard (prix de référence)")
            print("   3⭐ Supérieur (+25% coût, +15% satisfaction)")
            print("   4⭐ Premium (+50% coût, +30% satisfaction)")
            print("   5⭐ Luxe (+100% coût, +50% satisfaction)")
            
            new_quality = input(f"Niveau qualité 1-5 (ou Entrée pour garder {self.restaurant.quality_level}): ").strip()
            
            if new_quality:
                quality = int(new_quality)
                if 1 <= quality <= 5:
                    self.restaurant.quality_level = quality
                else:
                    print("⚠️ Qualité doit être entre 1 et 5")
            
            # Personnel
            print(f"\n👥 NIVEAU DE PERSONNEL (actuel: {self.restaurant.staff_level})")
            print("   1. Équipe réduite (120 clients max, 2200€/mois)")
            print("   2. Équipe normale (150 clients max, 2800€/mois)")
            print("   3. Équipe renforcée (180 clients max, 3600€/mois)")
            
            new_staff = input(f"Niveau personnel 1-3 (ou Entrée pour garder {self.restaurant.staff_level}): ").strip()
            
            if new_staff:
                staff = int(new_staff)
                if 1 <= staff <= 3:
                    self.restaurant.staff_level = staff
                else:
                    print("⚠️ Personnel doit être entre 1 et 3")
            
            return True
            
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Décision annulée ou invalide")
            return False
    
    def calculate_results(self, clients):
        """Calcule les résultats du tour."""
        # Revenus
        revenue = self.restaurant.price * Decimal(str(clients))
        
        # Coûts
        ingredient_cost_per_client = self.restaurant.get_ingredient_cost()
        ingredient_costs = ingredient_cost_per_client * Decimal(str(clients))
        staff_costs = self.restaurant.get_staff_cost()
        overhead_costs = Decimal("1200")  # Coûts fixes
        
        total_costs = ingredient_costs + staff_costs + overhead_costs
        
        # Profit
        profit = revenue - total_costs
        
        # Satisfaction client (basée sur qualité et prix)
        base_satisfaction = 2.0 + (self.restaurant.quality_level - 1) * 0.5
        price_penalty = max(0, (float(self.restaurant.price) - 15) * 0.1)
        satisfaction = max(1.0, min(5.0, base_satisfaction - price_penalty))
        
        # Mise à jour budget et réputation
        self.restaurant.budget += profit
        self.restaurant.total_revenue += revenue
        self.restaurant.total_profit += profit
        
        # Évolution réputation
        if satisfaction >= 4.0:
            self.restaurant.reputation += Decimal("0.2")
        elif satisfaction >= 3.0:
            self.restaurant.reputation += Decimal("0.1")
        elif satisfaction < 2.5:
            self.restaurant.reputation -= Decimal("0.1")
        
        self.restaurant.reputation = max(Decimal("1.0"), min(Decimal("10.0"), self.restaurant.reputation))
        
        return {
            "clients": clients,
            "revenue": revenue,
            "ingredient_costs": ingredient_costs,
            "staff_costs": staff_costs,
            "overhead_costs": overhead_costs,
            "total_costs": total_costs,
            "profit": profit,
            "satisfaction": satisfaction,
            "capacity_used": clients / self.restaurant.get_capacity()
        }
    
    def show_results(self, results, segment_details):
        """Affiche les résultats du tour."""
        print(f"\n📊 RÉSULTATS DU TOUR {self.turn}:")
        print("="*40)
        
        print(f"👥 Clients servis: {results['clients']}")
        print(f"   📊 Répartition par segment:")
        for segment, count in segment_details.items():
            print(f"      • {segment}: {count} clients")
        
        print(f"💰 Chiffre d'affaires: {results['revenue']:.2f}€")
        
        print(f"💸 Coûts:")
        print(f"   • Ingrédients: {results['ingredient_costs']:.2f}€")
        print(f"   • Personnel: {results['staff_costs']:.2f}€")
        print(f"   • Charges fixes: {results['overhead_costs']:.2f}€")
        print(f"   • Total: {results['total_costs']:.2f}€")
        
        profit_icon = "📈" if results['profit'] >= 0 else "📉"
        print(f"{profit_icon} Profit: {results['profit']:+.2f}€")
        
        print(f"😊 Satisfaction client: {results['satisfaction']:.1f}/5")
        print(f"🏪 Taux d'occupation: {results['capacity_used']:.1%}")
        
        # Marge
        if results['revenue'] > 0:
            margin = results['profit'] / results['revenue']
            print(f"📊 Marge nette: {margin:.1%}")
    
    def end_game(self):
        """Fin de partie."""
        print(f"\n" + "="*60)
        print("🎉 FIN DE PARTIE !")
        print("="*60)
        
        print(f"🏪 Restaurant: {self.restaurant.name}")
        print(f"💰 Budget final: {self.restaurant.budget:.2f}€")
        print(f"📈 Chiffre d'affaires total: {self.restaurant.total_revenue:.2f}€")
        print(f"💵 Profit total: {self.restaurant.total_profit:+.2f}€")
        print(f"🌟 Réputation finale: {self.restaurant.reputation:.1f}/10")
        
        # Évaluation
        if self.restaurant.total_profit >= 5000:
            print("🏆 EXCELLENT ! Vous êtes un vrai entrepreneur !")
        elif self.restaurant.total_profit >= 2000:
            print("✅ BIEN JOUÉ ! Vous maîtrisez les bases.")
        elif self.restaurant.total_profit >= 0:
            print("⚠️ CORRECT. Vous pouvez mieux faire !")
        else:
            print("❌ DIFFICILE. Révisez votre stratégie !")
        
        # Statistiques
        if self.restaurant.turn_history:
            avg_clients = sum(t['clients'] for t in self.restaurant.turn_history) / len(self.restaurant.turn_history)
            avg_satisfaction = sum(t['satisfaction'] for t in self.restaurant.turn_history) / len(self.restaurant.turn_history)
            
            print(f"\n📊 STATISTIQUES:")
            print(f"   Clients moyens/tour: {avg_clients:.0f}")
            print(f"   Satisfaction moyenne: {avg_satisfaction:.1f}/5")

def main():
    """Point d'entrée principal."""
    try:
        game = GameEngine()
        game.start_game()
    except KeyboardInterrupt:
        print("\n\n👋 Merci d'avoir joué à FoodOps Pro !")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()
