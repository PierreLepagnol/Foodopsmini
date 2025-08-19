#!/usr/bin/env python3
"""
🍔 FOODOPS PRO - SIMULATEUR COMPLET DE GESTION DE RESTAURANT 🍔
Version autonome sans dépendances externes.
"""

import random
import os
from decimal import Decimal

def clear_screen():
    """Efface l'écran."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Restaurant:
    """Restaurant du joueur avec toutes les fonctionnalités."""
    
    def __init__(self, name="Mon Restaurant"):
        self.name = name
        self.budget = Decimal("10000")
        self.price = Decimal("12.50")
        self.quality_level = 2  # 1-5
        self.staff_level = 2    # 1-3
        self.reputation = Decimal("5.0")  # 1-10
        
        # Marketing
        self.marketing_budget = Decimal("0")
        self.marketing_active = False
        
        # Historique
        self.turn_history = []
        self.total_revenue = Decimal("0")
        self.total_profit = Decimal("0")
        
        # Efficacité
        self.stock_efficiency = 0.95
    
    def get_capacity(self):
        """Capacité selon le personnel."""
        return {1: 120, 2: 150, 3: 180}[self.staff_level]
    
    def get_staff_cost(self):
        """Coût du personnel."""
        return {1: Decimal("2200"), 2: Decimal("2800"), 3: Decimal("3600")}[self.staff_level]
    
    def get_quality_cost_multiplier(self):
        """Multiplicateur de coût selon la qualité."""
        return {1: 0.7, 2: 1.0, 3: 1.25, 4: 1.5, 5: 2.0}[self.quality_level]
    
    def get_quality_name(self):
        """Nom du niveau de qualité."""
        return {1: "Économique", 2: "Standard", 3: "Supérieur", 4: "Premium", 5: "Luxe"}[self.quality_level]

class MarketEngine:
    """Moteur de marché avec segments et concurrence."""
    
    def __init__(self):
        self.segments = {
            "étudiants": {"size": 150, "budget": 11.0, "price_sens": 1.8, "quality_pref": 0.7},
            "familles": {"size": 180, "budget": 17.0, "price_sens": 1.2, "quality_pref": 1.1},
            "foodies": {"size": 90, "budget": 25.0, "price_sens": 0.6, "quality_pref": 1.8}
        }
        
        self.competitors = [
            {"name": "Resto Rapide", "price": 9.50, "quality": 1},
            {"name": "Bistrot Central", "price": 13.20, "quality": 3},
            {"name": "Table Gourmande", "price": 18.80, "quality": 4}
        ]
        
        self.events = []
        self.current_season = "printemps"
    
    def simulate_turn(self, restaurant, turn):
        """Simule un tour complet de marché."""
        # Facteurs externes
        seasonal_factor = self._get_seasonal_factor(turn)
        event_factor, event_desc = self._check_events(turn)
        
        # Simulation par segment
        total_clients = 0
        segment_breakdown = {}
        
        for segment_name, segment in self.segments.items():
            clients = self._simulate_segment(restaurant, segment, seasonal_factor, event_factor)
            total_clients += clients
            segment_breakdown[segment_name] = clients
        
        # Limiter par capacité
        total_clients = min(total_clients, restaurant.get_capacity())
        
        return total_clients, segment_breakdown, event_desc
    
    def _simulate_segment(self, restaurant, segment, seasonal_factor, event_factor):
        """Simule la demande d'un segment."""
        # Attractivité prix
        price_ratio = float(restaurant.price) / segment["budget"]
        if price_ratio <= 0.8:
            price_attract = 1.2
        elif price_ratio <= 1.0:
            price_attract = 1.0
        elif price_ratio <= 1.3:
            price_attract = max(0.3, 1.0 - (price_ratio - 1.0) * segment["price_sens"])
        else:
            price_attract = 0.1
        
        # Attractivité qualité
        quality_attract = 0.6 + (restaurant.quality_level / 5.0) * segment["quality_pref"]
        
        # Réputation
        reputation_factor = float(restaurant.reputation) / 10.0
        
        # Marketing
        marketing_factor = 1.2 if restaurant.marketing_active else 1.0
        
        # Demande finale
        base_demand = segment["size"] * 0.3
        final_demand = (base_demand * price_attract * quality_attract * 
                       reputation_factor * seasonal_factor * event_factor * marketing_factor)
        
        return max(0, int(final_demand * random.uniform(0.85, 1.15)))
    
    def _get_seasonal_factor(self, turn):
        """Facteur saisonnier."""
        seasons = ["hiver", "printemps", "été", "automne"]
        season_idx = ((turn - 1) // 3) % 4
        self.current_season = seasons[season_idx]
        
        factors = {"hiver": 0.9, "printemps": 1.0, "été": 1.2, "automne": 1.0}
        return factors[self.current_season]
    
    def _check_events(self, turn):
        """Vérifie les événements aléatoires."""
        if random.random() < 0.25:  # 25% de chance
            events = [
                (1.4, "🎪 Festival local - Affluence exceptionnelle !"),
                (0.8, "🌧️ Pluie continue - Moins de clients"),
                (1.2, "📰 Article positif dans la presse locale"),
                (0.9, "💸 Promotion chez un concurrent"),
                (0.7, "🚇 Grève des transports publics"),
                (1.3, "🎉 Événement sportif dans le quartier"),
                (0.85, "🏗️ Travaux dans la rue principale")
            ]
            
            factor, description = random.choice(events)
            self.events.append((turn, description))
            return factor, description
        
        return 1.0, None

class FinanceEngine:
    """Moteur financier avancé."""
    
    def calculate_results(self, restaurant, clients):
        """Calcule tous les résultats financiers."""
        # Revenus
        revenue = restaurant.price * Decimal(str(clients))
        
        # Coûts détaillés
        base_ingredient_cost = Decimal("4.20")
        ingredient_cost = (base_ingredient_cost * 
                          Decimal(str(restaurant.get_quality_cost_multiplier())) * 
                          Decimal(str(clients)) * 
                          Decimal(str(restaurant.stock_efficiency)))
        
        staff_cost = restaurant.get_staff_cost()
        overhead_cost = Decimal("1200")
        marketing_cost = restaurant.marketing_budget
        
        total_costs = ingredient_cost + staff_cost + overhead_cost + marketing_cost
        
        # Profits
        gross_profit = revenue - ingredient_cost
        net_profit = revenue - total_costs
        
        # Ratios
        gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
        net_margin = (net_profit / revenue * 100) if revenue > 0 else 0
        
        # Satisfaction client
        base_satisfaction = 2.5
        quality_bonus = {1: -0.3, 2: 0.0, 3: 0.2, 4: 0.4, 5: 0.6}[restaurant.quality_level]
        
        satisfaction = base_satisfaction + quality_bonus
        
        # Pénalité prix élevé
        if float(restaurant.price) > 20:
            satisfaction -= 0.5
        
        satisfaction = max(1.0, min(5.0, satisfaction))
        
        # Mise à jour restaurant
        restaurant.budget += net_profit
        restaurant.total_revenue += revenue
        restaurant.total_profit += net_profit
        restaurant.marketing_budget = Decimal("0")
        restaurant.marketing_active = False
        
        # Évolution réputation
        if satisfaction >= 4.0:
            restaurant.reputation += Decimal("0.2")
        elif satisfaction >= 3.5:
            restaurant.reputation += Decimal("0.1")
        elif satisfaction < 2.5:
            restaurant.reputation -= Decimal("0.2")
        elif satisfaction < 3.0:
            restaurant.reputation -= Decimal("0.1")
        
        restaurant.reputation = max(Decimal("1.0"), min(Decimal("10.0"), restaurant.reputation))
        
        return {
            "clients": clients,
            "revenue": revenue,
            "ingredient_cost": ingredient_cost,
            "staff_cost": staff_cost,
            "overhead_cost": overhead_cost,
            "marketing_cost": marketing_cost,
            "total_costs": total_costs,
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "gross_margin": gross_margin,
            "net_margin": net_margin,
            "satisfaction": satisfaction,
            "capacity_utilization": clients / restaurant.get_capacity()
        }

class GameEngine:
    """Moteur de jeu principal."""
    
    def __init__(self):
        self.restaurant = None
        self.market = MarketEngine()
        self.finance = FinanceEngine()
        self.turn = 0
        self.max_turns = 10
        self.game_mode = "standard"
    
    def start_game(self):
        """Lance le jeu complet."""
        self.show_welcome()
        
        if not self.setup_game():
            return
        
        # Boucle principale
        while self.turn < self.max_turns:
            self.turn += 1
            
            if not self.play_turn():
                break
        
        self.show_final_results()
    
    def show_welcome(self):
        """Écran d'accueil."""
        clear_screen()
        print("🍔" + "="*70 + "🍔")
        print("                    FOODOPS PRO - SIMULATEUR COMPLET")
        print("                     Gestion de Restaurant Avancée")
        print("🍔" + "="*70 + "🍔")
        print()
        print("🎯 OBJECTIFS:")
        print("   • Gérer un restaurant rentable et durable")
        print("   • Optimiser prix, qualité et service client")
        print("   • Développer votre réputation sur le marché")
        print("   • Battre la concurrence avec votre stratégie")
        print()
        print("⭐ FONCTIONNALITÉS PROFESSIONNELLES:")
        print("   🔹 Système qualité 5 niveaux (Économique → Luxe)")
        print("   🔹 3 segments clientèle (Étudiants, Familles, Foodies)")
        print("   🔹 Marketing et campagnes publicitaires")
        print("   🔹 Finance avancée avec ratios et marges")
        print("   🔹 Événements saisonniers et aléatoires")
        print("   🔹 Concurrence dynamique et réaliste")
        print("   🔹 Évolution de réputation")
        print()
        input("Appuyez sur Entrée pour commencer...")
    
    def setup_game(self):
        """Configuration initiale."""
        clear_screen()
        print("⚙️ CONFIGURATION DE LA PARTIE")
        print("="*50)
        
        # Mode de jeu
        print("\n🎮 CHOIX DU MODE:")
        print("   1. 📚 Démo (5 tours, plus facile)")
        print("   2. 🎯 Standard (10 tours, équilibré)")
        print("   3. 🏆 Expert (15 tours, difficile)")
        
        while True:
            try:
                choice = input("\nVotre choix (1-3): ").strip()
                if choice == "1":
                    self.game_mode = "demo"
                    self.max_turns = 5
                    initial_budget = 15000
                    break
                elif choice == "2":
                    self.game_mode = "standard"
                    self.max_turns = 10
                    initial_budget = 10000
                    break
                elif choice == "3":
                    self.game_mode = "expert"
                    self.max_turns = 15
                    initial_budget = 8000
                    break
                else:
                    print("❌ Choix invalide")
            except KeyboardInterrupt:
                print("\n👋 Au revoir !")
                return False
        
        # Nom du restaurant
        print(f"\n🏪 CRÉATION DE VOTRE RESTAURANT:")
        name = input("Nom (ou Entrée pour 'Mon Restaurant'): ").strip()
        if not name:
            name = "Mon Restaurant"
        
        self.restaurant = Restaurant(name)
        self.restaurant.budget = Decimal(str(initial_budget))
        
        print(f"\n✅ Restaurant '{self.restaurant.name}' créé !")
        print(f"💰 Budget initial: {self.restaurant.budget}€")
        print(f"🎯 Objectif: Survivre {self.max_turns} tours et maximiser les profits")
        
        input("\nAppuyez sur Entrée pour commencer le jeu...")
        return True

    def play_turn(self):
        """Joue un tour complet."""
        clear_screen()

        print("🍔" + "="*70 + "🍔")
        print(f"                         TOUR {self.turn}/{self.max_turns}")
        print("🍔" + "="*70 + "🍔")

        # État du restaurant
        self.show_restaurant_status()

        # Événements et marché
        self.show_market_info()

        # Décisions du joueur
        if not self.make_decisions():
            return False

        # Simulation
        clients, segments, event = self.market.simulate_turn(self.restaurant, self.turn)
        results = self.finance.calculate_results(self.restaurant, clients)

        # Résultats
        self.show_turn_results(results, segments, event)

        # Historique
        self.restaurant.turn_history.append(results)

        # Vérification faillite
        if self.restaurant.budget <= 0:
            print("\n💥 FAILLITE ! Votre budget est épuisé.")
            input("Appuyez sur Entrée pour voir le bilan final...")
            return False

        input("\nAppuyez sur Entrée pour continuer...")
        return True

    def show_restaurant_status(self):
        """Affiche l'état du restaurant."""
        print(f"\n📊 ÉTAT DE VOTRE RESTAURANT:")
        print(f"   🏪 {self.restaurant.name}")
        print(f"   💰 Budget: {self.restaurant.budget:.2f}€")
        print(f"   💵 Prix menu: {self.restaurant.price}€")
        print(f"   ⭐ Qualité: {self.restaurant.quality_level}/5 ({self.restaurant.get_quality_name()})")
        print(f"   👥 Personnel: Niveau {self.restaurant.staff_level} (capacité: {self.restaurant.get_capacity()} clients)")
        print(f"   🌟 Réputation: {self.restaurant.reputation:.1f}/10")

        if self.restaurant.turn_history:
            last = self.restaurant.turn_history[-1]
            print(f"   📈 Dernier profit: {last['net_profit']:+.2f}€")
            print(f"   😊 Dernière satisfaction: {last['satisfaction']:.1f}/5")

    def show_market_info(self):
        """Affiche les informations du marché."""
        print(f"\n🏪 MARCHÉ ET CONCURRENCE:")
        print(f"   🌍 Saison: {self.market.current_season.title()}")

        print(f"   🎯 Segments clientèle:")
        for name, segment in self.market.segments.items():
            print(f"      • {name.title()}: {segment['size']} clients, budget {segment['budget']}€")

        print(f"   🏢 Concurrents:")
        for comp in self.market.competitors:
            print(f"      • {comp['name']}: {comp['price']}€, qualité {comp['quality']}/5")

        # Événements récents
        if self.market.events:
            recent_events = self.market.events[-2:]
            print(f"   📰 Événements récents:")
            for turn, desc in recent_events:
                print(f"      • Tour {turn}: {desc}")

    def make_decisions(self):
        """Interface de prise de décision."""
        print(f"\n🎯 VOS DÉCISIONS POUR CE TOUR:")

        try:
            # Prix
            print(f"\n💵 PRIX DU MENU (actuel: {self.restaurant.price}€)")
            print("   Budgets clientèle: Étudiants 11€ | Familles 17€ | Foodies 25€")
            new_price = input(f"Nouveau prix 8-35€ (Entrée = garder): ").strip()

            if new_price:
                price = float(new_price)
                if 8 <= price <= 35:
                    self.restaurant.price = Decimal(str(price))
                else:
                    print("⚠️ Prix doit être entre 8€ et 35€")

            # Qualité
            print(f"\n⭐ QUALITÉ INGRÉDIENTS (actuel: {self.restaurant.quality_level}/5)")
            print("   1⭐ Économique (-30% coût, -30% satisfaction)")
            print("   2⭐ Standard (coût de référence)")
            print("   3⭐ Supérieur (+25% coût, +20% satisfaction)")
            print("   4⭐ Premium (+50% coût, +40% satisfaction)")
            print("   5⭐ Luxe (+100% coût, +60% satisfaction)")

            new_quality = input(f"Niveau 1-5 (Entrée = garder): ").strip()

            if new_quality:
                quality = int(new_quality)
                if 1 <= quality <= 5:
                    self.restaurant.quality_level = quality
                else:
                    print("⚠️ Qualité entre 1 et 5")

            # Personnel
            print(f"\n👥 PERSONNEL (actuel: niveau {self.restaurant.staff_level})")
            print("   1. Réduit (120 clients max, 2200€/mois)")
            print("   2. Normal (150 clients max, 2800€/mois)")
            print("   3. Renforcé (180 clients max, 3600€/mois)")

            new_staff = input(f"Niveau 1-3 (Entrée = garder): ").strip()

            if new_staff:
                staff = int(new_staff)
                if 1 <= staff <= 3:
                    self.restaurant.staff_level = staff
                else:
                    print("⚠️ Personnel entre 1 et 3")

            # Marketing
            print(f"\n📢 MARKETING (budget actuel: {self.restaurant.marketing_budget}€)")
            print("   Effet: +20% d'attractivité ce tour")
            marketing = input(f"Budget marketing 0-2000€ (Entrée = 0): ").strip()

            if marketing:
                budget = float(marketing)
                if 0 <= budget <= 2000 and budget <= float(self.restaurant.budget):
                    self.restaurant.marketing_budget = Decimal(str(budget))
                    self.restaurant.marketing_active = budget > 0
                    self.restaurant.budget -= Decimal(str(budget))
                else:
                    print("⚠️ Budget marketing invalide ou insuffisant")

            return True

        except (ValueError, KeyboardInterrupt):
            print("\n❌ Décision annulée")
            return False

    def show_turn_results(self, results, segments, event):
        """Affiche les résultats du tour."""
        print(f"\n📊 RÉSULTATS DU TOUR {self.turn}:")
        print("="*50)

        # Événement
        if event:
            print(f"🎲 ÉVÉNEMENT: {event}")

        # Clients
        print(f"\n👥 CLIENTS SERVIS: {results['clients']}")
        print(f"   Répartition par segment:")
        for segment, count in segments.items():
            print(f"      • {segment.title()}: {count} clients")
        print(f"   📊 Taux occupation: {results['capacity_utilization']:.1%}")

        # Finances
        print(f"\n💰 FINANCES:")
        print(f"   📈 Chiffre d'affaires: {results['revenue']:.2f}€")
        print(f"   💸 Coûts totaux: {results['total_costs']:.2f}€")
        print(f"      • Ingrédients: {results['ingredient_cost']:.2f}€")
        print(f"      • Personnel: {results['staff_cost']:.2f}€")
        print(f"      • Charges fixes: {results['overhead_cost']:.2f}€")
        if results['marketing_cost'] > 0:
            print(f"      • Marketing: {results['marketing_cost']:.2f}€")

        profit_icon = "📈" if results['net_profit'] >= 0 else "📉"
        print(f"   {profit_icon} PROFIT NET: {results['net_profit']:+.2f}€")
        print(f"   📊 Marge nette: {results['net_margin']:.1f}%")

        # Performance
        print(f"\n🎯 PERFORMANCE:")
        print(f"   😊 Satisfaction client: {results['satisfaction']:.1f}/5")
        print(f"   🌟 Réputation: {self.restaurant.reputation:.1f}/10")
        print(f"   💰 Budget restant: {self.restaurant.budget:.2f}€")

    def show_final_results(self):
        """Affiche les résultats finaux."""
        clear_screen()
        print("🏆" + "="*70 + "🏆")
        print("                           BILAN FINAL")
        print("🏆" + "="*70 + "🏆")

        print(f"\n🏪 RESTAURANT: {self.restaurant.name}")
        print(f"🎮 Mode: {self.game_mode.title()} ({self.max_turns} tours)")

        print(f"\n💰 RÉSULTATS FINANCIERS:")
        print(f"   Budget final: {self.restaurant.budget:.2f}€")
        print(f"   CA total: {self.restaurant.total_revenue:.2f}€")
        print(f"   Profit total: {self.restaurant.total_profit:+.2f}€")
        print(f"   Réputation finale: {self.restaurant.reputation:.1f}/10")

        # Évaluation
        profit = float(self.restaurant.total_profit)
        if profit >= 8000:
            grade = "🏆 EXCELLENT ! Entrepreneur exceptionnel !"
        elif profit >= 5000:
            grade = "🥇 TRÈS BIEN ! Vous maîtrisez la gestion !"
        elif profit >= 2000:
            grade = "🥈 BIEN ! Bonne compréhension du business"
        elif profit >= 0:
            grade = "🥉 CORRECT. Vous pouvez mieux faire"
        else:
            grade = "❌ DIFFICILE. Révisez votre stratégie"

        print(f"\n🎯 ÉVALUATION: {grade}")

        # Statistiques
        if self.restaurant.turn_history:
            avg_clients = sum(t['clients'] for t in self.restaurant.turn_history) / len(self.restaurant.turn_history)
            avg_satisfaction = sum(t['satisfaction'] for t in self.restaurant.turn_history) / len(self.restaurant.turn_history)
            avg_margin = sum(t['net_margin'] for t in self.restaurant.turn_history) / len(self.restaurant.turn_history)

            print(f"\n📊 STATISTIQUES MOYENNES:")
            print(f"   Clients/tour: {avg_clients:.0f}")
            print(f"   Satisfaction: {avg_satisfaction:.1f}/5")
            print(f"   Marge nette: {avg_margin:.1f}%")

        print(f"\n🎉 Merci d'avoir joué à FoodOps Pro !")
        input("Appuyez sur Entrée pour terminer...")

def main():
    """Point d'entrée principal."""
    try:
        game = GameEngine()
        game.start_game()
    except KeyboardInterrupt:
        print("\n\n👋 Merci d'avoir joué à FoodOps Pro !")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("Veuillez relancer le jeu.")

if __name__ == "__main__":
    main()
