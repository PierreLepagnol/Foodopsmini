#!/usr/bin/env python3
"""
FoodOps Pro Complet - Version autonome sans dépendances externes.
"""

import sys
import os
import random
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import json

# Ajouter le chemin src
sys.path.insert(0, str(Path(__file__).parent / "src"))

class SimpleYAMLLoader:
    """Chargeur YAML simplifié pour éviter la dépendance pyyaml."""
    
    @staticmethod
    def load_scenario(scenario_name="standard"):
        """Charge un scénario prédéfini."""
        scenarios = {
            "standard": {
                "name": "Scénario Standard",
                "description": "Configuration équilibrée pour apprentissage général",
                "market": {
                    "base_demand": 420,
                    "demand_noise": 0.15,
                    "price_sensitivity": 1.2,
                    "quality_importance": 1.0
                },
                "segments": {
                    "étudiants": {
                        "size": 150,
                        "budget": 11.0,
                        "price_sensitivity": 1.8,
                        "quality_sensitivity": 0.7
                    },
                    "familles": {
                        "size": 180,
                        "budget": 17.0,
                        "price_sensitivity": 1.2,
                        "quality_sensitivity": 1.1
                    },
                    "foodies": {
                        "size": 90,
                        "budget": 25.0,
                        "price_sensitivity": 0.6,
                        "quality_sensitivity": 1.8
                    }
                },
                "restaurant": {
                    "initial_budget": 10000,
                    "base_capacity": 150,
                    "base_staff_cost": 2800,
                    "base_overhead": 1200
                },
                "competitors": [
                    {"name": "Resto Rapide", "price": 9.50, "quality": 1},
                    {"name": "Bistrot Central", "price": 13.20, "quality": 3},
                    {"name": "Table Gourmande", "price": 18.80, "quality": 4}
                ],
                "game": {
                    "max_turns": 10,
                    "starting_month": 1,
                    "enable_seasonality": True,
                    "enable_events": True,
                    "enable_marketing": True,
                    "enable_advanced_finance": True
                }
            }
        }
        return scenarios.get(scenario_name, scenarios["standard"])

class QualitySystem:
    """Système de qualité avancé."""
    
    QUALITY_LEVELS = {
        1: {"name": "Économique", "cost_modifier": 0.7, "satisfaction_bonus": -0.5},
        2: {"name": "Standard", "cost_modifier": 1.0, "satisfaction_bonus": 0.0},
        3: {"name": "Supérieur", "cost_modifier": 1.25, "satisfaction_bonus": 0.3},
        4: {"name": "Premium", "cost_modifier": 1.5, "satisfaction_bonus": 0.6},
        5: {"name": "Luxe", "cost_modifier": 2.0, "satisfaction_bonus": 1.0}
    }
    
    @classmethod
    def get_quality_info(cls, level):
        """Retourne les informations d'un niveau de qualité."""
        return cls.QUALITY_LEVELS.get(level, cls.QUALITY_LEVELS[2])

class MarketingSystem:
    """Système marketing simplifié."""
    
    def __init__(self):
        self.campaigns = []
        self.reputation = 5.0
        self.total_marketing_spend = 0
    
    def launch_campaign(self, campaign_type, budget, duration=3):
        """Lance une campagne marketing."""
        campaigns_data = {
            "social_media": {"reach_per_euro": 20, "conversion_rate": 0.025},
            "local_ads": {"reach_per_euro": 15, "conversion_rate": 0.035},
            "loyalty": {"reach_per_euro": 5, "conversion_rate": 0.15},
            "events": {"reach_per_euro": 8, "conversion_rate": 0.08}
        }
        
        if campaign_type in campaigns_data:
            campaign = campaigns_data[campaign_type]
            reach = budget * campaign["reach_per_euro"]
            expected_customers = reach * campaign["conversion_rate"]
            
            self.campaigns.append({
                "type": campaign_type,
                "budget": budget,
                "duration": duration,
                "reach": reach,
                "expected_customers": expected_customers,
                "remaining_turns": duration
            })
            
            self.total_marketing_spend += budget
            return expected_customers
        
        return 0
    
    def get_marketing_boost(self):
        """Calcule le boost marketing actuel."""
        total_boost = 0
        active_campaigns = []
        
        for campaign in self.campaigns:
            if campaign["remaining_turns"] > 0:
                total_boost += campaign["expected_customers"]
                active_campaigns.append(campaign)
                campaign["remaining_turns"] -= 1
        
        self.campaigns = active_campaigns
        return total_boost

class FinanceSystem:
    """Système financier avancé."""
    
    def __init__(self):
        self.transactions = []
        self.total_revenue = 0
        self.total_costs = 0
        
    def record_transaction(self, type_transaction, amount, description=""):
        """Enregistre une transaction."""
        transaction = {
            "date": datetime.now(),
            "type": type_transaction,
            "amount": amount,
            "description": description
        }
        self.transactions.append(transaction)
        
        if type_transaction == "revenue":
            self.total_revenue += amount
        else:
            self.total_costs += amount
    
    def get_financial_ratios(self, current_assets=10000):
        """Calcule les ratios financiers."""
        if self.total_revenue > 0:
            net_margin = (self.total_revenue - self.total_costs) / self.total_revenue
            roa = (self.total_revenue - self.total_costs) / current_assets if current_assets > 0 else 0
        else:
            net_margin = 0
            roa = 0
        
        return {
            "net_margin": net_margin,
            "roa": roa,
            "total_profit": self.total_revenue - self.total_costs
        }

class EventSystem:
    """Système d'événements aléatoires."""
    
    def __init__(self):
        self.active_events = []
        self.events_pool = [
            {
                "name": "🌡️ Canicule",
                "description": "Forte chaleur, demande accrue pour plats frais",
                "probability": 0.15,
                "duration": 3,
                "demand_modifier": 1.25,
                "season": "été"
            },
            {
                "name": "🌧️ Pluie continue",
                "description": "Mauvais temps, moins de clients",
                "probability": 0.20,
                "duration": 2,
                "demand_modifier": 0.80,
                "season": "automne"
            },
            {
                "name": "🎪 Festival local",
                "description": "Événement culturel, affluence exceptionnelle",
                "probability": 0.25,
                "duration": 2,
                "demand_modifier": 1.50,
                "season": "all"
            },
            {
                "name": "🏪 Nouveau concurrent",
                "description": "Ouverture d'un nouveau restaurant",
                "probability": 0.08,
                "duration": 5,
                "demand_modifier": 0.85,
                "season": "all"
            }
        ]
    
    def process_events(self, turn, season="printemps"):
        """Traite les événements pour le tour actuel."""
        new_events = []
        
        # Vérifier les nouveaux événements
        for event_template in self.events_pool:
            if (event_template["season"] == "all" or event_template["season"] == season):
                if random.random() < event_template["probability"]:
                    event = event_template.copy()
                    event["remaining_turns"] = event["duration"]
                    new_events.append(event)
                    self.active_events.append(event)
        
        # Décrémenter la durée des événements actifs
        self.active_events = [e for e in self.active_events if e["remaining_turns"] > 0]
        for event in self.active_events:
            event["remaining_turns"] -= 1
        
        return new_events
    
    def get_current_modifiers(self):
        """Retourne les modificateurs actuels."""
        demand_modifier = 1.0
        for event in self.active_events:
            if event["remaining_turns"] > 0:
                demand_modifier *= event.get("demand_modifier", 1.0)
        
        return {"demand_modifier": demand_modifier}

class RestaurantPro:
    """Restaurant avec fonctionnalités avancées."""
    
    def __init__(self, name="Mon Restaurant Pro"):
        self.name = name
        self.budget = 10000
        self.price = 12.50
        self.quality_level = 2
        self.staff_level = 2
        self.reputation = 5.0
        self.turn = 1
        
        # Systèmes avancés
        self.marketing = MarketingSystem()
        self.finance = FinanceSystem()
        self.events = EventSystem()
        
        # Historique
        self.history = []
        
        # Stocks (simplifié)
        self.stock_level = 100  # %
        self.stock_quality = 2
    
    def get_capacity(self):
        """Calcule la capacité selon le personnel."""
        base_capacities = {1: 120, 2: 150, 3: 180}
        return base_capacities.get(self.staff_level, 150)
    
    def get_staff_cost(self):
        """Calcule le coût du personnel."""
        base_costs = {1: 2200, 2: 2800, 3: 3600}
        return base_costs.get(self.staff_level, 2800)
    
    def get_ingredient_cost_per_meal(self):
        """Calcule le coût des ingrédients par repas."""
        base_cost = 4.50
        quality_modifier = QualitySystem.get_quality_info(self.quality_level)["cost_modifier"]
        stock_modifier = 1.0 if self.stock_level > 50 else 1.2  # Pénalité si stock bas
        return base_cost * quality_modifier * stock_modifier

class MarketSimulatorPro:
    """Simulateur de marché avancé."""
    
    def __init__(self, scenario_data):
        self.scenario = scenario_data
        self.segments = scenario_data["segments"]
        self.competitors = scenario_data["competitors"]
    
    def simulate_turn(self, restaurant):
        """Simule un tour complet avec tous les systèmes."""
        # Traiter les événements
        season = self._get_season(restaurant.turn)
        new_events = restaurant.events.process_events(restaurant.turn, season)
        event_modifiers = restaurant.events.get_current_modifiers()
        
        # Calculer le boost marketing
        marketing_boost = restaurant.marketing.get_marketing_boost()
        
        # Simuler chaque segment
        total_customers = 0
        segment_details = {}
        
        for segment_name, segment_data in self.segments.items():
            customers = self._calculate_segment_customers(
                restaurant, segment_name, segment_data, 
                event_modifiers, marketing_boost
            )
            total_customers += customers
            segment_details[segment_name] = customers
        
        # Appliquer la capacité
        capacity = restaurant.get_capacity()
        lost_customers = max(0, total_customers - capacity)
        served_customers = min(total_customers, capacity)
        
        # Calculer les finances
        revenue = served_customers * restaurant.price
        
        ingredient_cost = served_customers * restaurant.get_ingredient_cost_per_meal()
        staff_cost = restaurant.get_staff_cost()
        overhead_cost = 1200
        total_costs = ingredient_cost + staff_cost + overhead_cost
        
        profit = revenue - total_costs
        
        # Enregistrer les transactions
        restaurant.finance.record_transaction("revenue", revenue, f"Ventes tour {restaurant.turn}")
        restaurant.finance.record_transaction("cost", total_costs, f"Coûts tour {restaurant.turn}")
        
        # Calculer la satisfaction
        satisfaction = self._calculate_satisfaction(restaurant, served_customers, capacity)
        
        # Mettre à jour la réputation
        reputation_change = (satisfaction - 3.0) * 0.1
        restaurant.reputation = max(1.0, min(10.0, restaurant.reputation + reputation_change))
        
        # Calculer la part de marché
        total_market = sum(segment["size"] for segment in self.segments.values())
        market_share = (served_customers / total_market) * 100 if total_market > 0 else 0
        
        # Mettre à jour le stock (simulation simple)
        restaurant.stock_level = max(20, restaurant.stock_level - (served_customers / 10))
        
        return {
            "customers": served_customers,
            "lost_customers": lost_customers,
            "revenue": revenue,
            "costs": total_costs,
            "profit": profit,
            "satisfaction": satisfaction,
            "market_share": market_share,
            "segment_details": segment_details,
            "new_events": new_events,
            "active_events": restaurant.events.active_events,
            "marketing_boost": marketing_boost,
            "ingredient_cost": ingredient_cost,
            "staff_cost": staff_cost,
            "overhead_cost": overhead_cost,
            "season": season
        }
    
    def _calculate_segment_customers(self, restaurant, segment_name, segment_data, event_modifiers, marketing_boost):
        """Calcule les clients d'un segment avec tous les modificateurs."""
        base_size = segment_data["size"]
        
        # Attractivité prix
        price_ratio = restaurant.price / segment_data["budget"]
        price_attractiveness = max(0.1, min(1.5, 1.2 - (price_ratio - 1) * segment_data["price_sensitivity"]))
        
        # Attractivité qualité
        quality_info = QualitySystem.get_quality_info(restaurant.quality_level)
        quality_attractiveness = 1.0 + quality_info["satisfaction_bonus"] * segment_data.get("quality_sensitivity", 1.0)
        
        # Attractivité réputation
        reputation_attractiveness = restaurant.reputation / 10.0
        
        # Attractivité globale
        base_attractiveness = (
            price_attractiveness * 0.4 +
            quality_attractiveness * 0.3 +
            reputation_attractiveness * 0.3
        )
        
        # Appliquer les modificateurs
        event_modifier = event_modifiers.get("demand_modifier", 1.0)
        
        # Boost marketing (réparti sur tous les segments)
        marketing_modifier = 1.0 + (marketing_boost / sum(s["size"] for s in self.segments.values()))
        
        # Bruit aléatoire
        noise = random.uniform(0.85, 1.15)
        
        # Calcul final
        final_customers = base_size * base_attractiveness * event_modifier * marketing_modifier * noise
        
        return max(0, int(final_customers))
    
    def _calculate_satisfaction(self, restaurant, served_customers, capacity):
        """Calcule la satisfaction client."""
        base_satisfaction = 3.0
        
        # Bonus qualité
        quality_info = QualitySystem.get_quality_info(restaurant.quality_level)
        quality_bonus = quality_info["satisfaction_bonus"]
        
        # Pénalité si restaurant plein
        capacity_penalty = 0
        if served_customers >= capacity * 0.95:
            capacity_penalty = -0.3
        
        # Bonus réputation
        reputation_bonus = (restaurant.reputation - 5.0) * 0.1
        
        satisfaction = base_satisfaction + quality_bonus + capacity_penalty + reputation_bonus
        return max(1.0, min(5.0, satisfaction))
    
    def _get_season(self, turn):
        """Détermine la saison selon le tour."""
        seasons = ["hiver", "printemps", "été", "automne"]
        return seasons[(turn - 1) % 4]

class GameInterfacePro:
    """Interface de jeu professionnelle."""
    
    def __init__(self):
        self.scenario = SimpleYAMLLoader.load_scenario("standard")
        self.restaurant = RestaurantPro()
        self.market = MarketSimulatorPro(self.scenario)
    
    def show_welcome(self):
        """Affiche l'écran d'accueil."""
        print("🍽️ FOODOPS PRO - VERSION COMPLÈTE")
        print("=" * 60)
        print("🎯 Simulateur professionnel de gestion de restaurant")
        print("📚 Avec systèmes avancés : Qualité, Marketing, Finance, Événements")
        print("")
        print(f"🏪 Bienvenue dans {self.restaurant.name}")
        print(f"💰 Budget initial : {self.restaurant.budget:,.0f}€")
        print(f"🎮 Objectif : Survivre 10 tours et maximiser les profits")
        print("")
    
    def show_status(self):
        """Affiche le statut complet."""
        print(f"\n📊 STATUT RESTAURANT - TOUR {self.restaurant.turn}")
        print("=" * 50)
        print(f"💰 Budget: {self.restaurant.budget:,.0f}€")
        print(f"💵 Prix menu: {self.restaurant.price:.2f}€")
        print(f"⭐ Qualité: {self.restaurant.quality_level}/5 ({QualitySystem.get_quality_info(self.restaurant.quality_level)['name']})")
        print(f"👥 Personnel: Niveau {self.restaurant.staff_level}/3 (Capacité: {self.restaurant.get_capacity()})")
        print(f"🌟 Réputation: {self.restaurant.reputation:.1f}/10")
        print(f"📦 Stock: {self.restaurant.stock_level:.0f}%")
        
        # Systèmes avancés
        ratios = self.restaurant.finance.get_financial_ratios(self.restaurant.budget)
        print(f"📈 Profit total: {ratios['total_profit']:+,.0f}€")
        print(f"💼 Marge nette: {ratios['net_margin']:.1%}")
    
    def show_events(self):
        """Affiche les événements actifs."""
        if self.restaurant.events.active_events:
            print(f"\n🎲 ÉVÉNEMENTS ACTIFS:")
            for event in self.restaurant.events.active_events:
                if event["remaining_turns"] > 0:
                    print(f"   {event['name']} (reste {event['remaining_turns']} tours)")
                    print(f"      {event['description']}")
    
    def show_marketing(self):
        """Affiche le statut marketing."""
        active_campaigns = [c for c in self.restaurant.marketing.campaigns if c["remaining_turns"] > 0]
        if active_campaigns:
            print(f"\n📈 CAMPAGNES MARKETING ACTIVES:")
            for campaign in active_campaigns:
                print(f"   • {campaign['type']}: {campaign['budget']}€ (reste {campaign['remaining_turns']} tours)")
    
    def get_decisions(self):
        """Interface de décisions avancée."""
        print(f"\n🎯 DÉCISIONS TOUR {self.restaurant.turn}")
        print("=" * 40)
        
        try:
            # Décisions de base
            print("📋 PARAMÈTRES DE BASE:")
            
            new_price = input(f"💵 Prix menu (actuel: {self.restaurant.price:.2f}€): ")
            if new_price.strip():
                self.restaurant.price = max(5.0, min(30.0, float(new_price)))
            
            new_quality = input(f"⭐ Qualité 1-5 (actuel: {self.restaurant.quality_level}): ")
            if new_quality.strip():
                self.restaurant.quality_level = max(1, min(5, int(new_quality)))
            
            new_staff = input(f"👥 Personnel 1-3 (actuel: {self.restaurant.staff_level}): ")
            if new_staff.strip():
                self.restaurant.staff_level = max(1, min(3, int(new_staff)))
            
            # Gestion des stocks
            if self.restaurant.stock_level < 50:
                print(f"\n📦 GESTION STOCKS (Niveau: {self.restaurant.stock_level:.0f}%):")
                restock = input("Réapprovisionner ? (o/n): ").lower()
                if restock == 'o':
                    self.restaurant.stock_level = 100
                    restock_cost = 500
                    self.restaurant.budget -= restock_cost
                    print(f"✅ Stock reconstitué (-{restock_cost}€)")
            
            # Marketing
            print(f"\n📈 MARKETING (Budget disponible: {self.restaurant.budget:,.0f}€):")
            marketing_choice = input("Lancer campagne ? (social/local/loyalty/events/non): ").lower()
            
            if marketing_choice in ["social", "local", "loyalty", "events"]:
                budget = input("Budget campagne (€): ")
                if budget.strip() and budget.isdigit():
                    budget = int(budget)
                    if budget <= self.restaurant.budget:
                        boost = self.restaurant.marketing.launch_campaign(marketing_choice, budget)
                        self.restaurant.budget -= budget
                        print(f"✅ Campagne lancée ! Clients attendus: +{boost:.0f}")
                    else:
                        print("❌ Budget insuffisant")
            
            return True
            
        except (ValueError, KeyboardInterrupt):
            print("❌ Entrée invalide")
            return True
        except EOFError:
            return False
    
    def simulate_and_show_results(self):
        """Simule et affiche les résultats complets."""
        results = self.market.simulate_turn(self.restaurant)
        
        print(f"\n📈 RÉSULTATS TOUR {self.restaurant.turn}")
        print("=" * 45)
        
        # Événements
        if results["new_events"]:
            print("🎲 NOUVEAUX ÉVÉNEMENTS:")
            for event in results["new_events"]:
                print(f"   {event['name']}: {event['description']}")
        
        # Résultats opérationnels
        print(f"\n👥 CLIENTÈLE:")
        print(f"   Clients servis: {results['customers']}")
        if results['lost_customers'] > 0:
            print(f"   Clients perdus: {results['lost_customers']} (capacité insuffisante)")
        
        print(f"   Répartition par segment:")
        for segment, count in results["segment_details"].items():
            print(f"     • {segment}: {count}")
        
        if results["marketing_boost"] > 0:
            print(f"   📈 Boost marketing: +{results['marketing_boost']:.0f} clients")
        
        # Résultats financiers
        print(f"\n💰 FINANCES:")
        print(f"   Chiffre d'affaires: {results['revenue']:,.0f}€")
        print(f"   Coûts totaux: {results['costs']:,.0f}€")
        print(f"     • Ingrédients: {results['ingredient_cost']:,.0f}€")
        print(f"     • Personnel: {results['staff_cost']:,.0f}€")
        print(f"     • Charges: {results['overhead_cost']:,.0f}€")
        
        profit_icon = "💚" if results['profit'] > 0 else "❤️"
        print(f"   {profit_icon} Profit: {results['profit']:+,.0f}€")
        
        # KPIs
        print(f"\n📊 PERFORMANCE:")
        print(f"   Satisfaction: {results['satisfaction']:.1f}/5")
        print(f"   Part de marché: {results['market_share']:.1f}%")
        print(f"   Saison: {results['season']}")
        
        # Mettre à jour le budget
        self.restaurant.budget += results['profit']
        
        # Sauvegarder
        self.restaurant.history.append(results)
        
        return results
    
    def show_competitors(self):
        """Affiche la concurrence."""
        print(f"\n🏪 CONCURRENCE:")
        for comp in self.scenario["competitors"]:
            print(f"   • {comp['name']}: {comp['price']:.2f}€, Qualité {comp['quality']}/5")
    
    def show_help(self):
        """Affiche l'aide complète."""
        print(f"\n💡 GUIDE STRATÉGIQUE COMPLET")
        print("=" * 40)
        
        print("🎯 SEGMENTS CLIENTÈLE:")
        for name, data in self.scenario["segments"].items():
            print(f"   • {name} ({data['size']}): Budget {data['budget']:.0f}€")
        
        print(f"\n⭐ SYSTÈME QUALITÉ:")
        for level, info in QualitySystem.QUALITY_LEVELS.items():
            cost_change = (info['cost_modifier'] - 1) * 100
            sat_change = info['satisfaction_bonus']
            print(f"   {level}⭐ {info['name']}: {cost_change:+.0f}% coût, {sat_change:+.1f} satisfaction")
        
        print(f"\n📈 MARKETING:")
        print("   • social: 20 portée/€, 2.5% conversion")
        print("   • local: 15 portée/€, 3.5% conversion")
        print("   • loyalty: 5 portée/€, 15% conversion")
        print("   • events: 8 portée/€, 8% conversion")
        
        print(f"\n🎲 ÉVÉNEMENTS POSSIBLES:")
        print("   • Canicule: +25% demande (été)")
        print("   • Pluie: -20% demande (automne)")
        print("   • Festival: +50% demande")
        print("   • Nouveau concurrent: -15% demande")
    
    def play(self):
        """Boucle de jeu principale."""
        self.show_welcome()
        
        while self.restaurant.turn <= 10 and self.restaurant.budget > -10000:
            self.show_status()
            self.show_events()
            self.show_marketing()
            self.show_competitors()
            
            print(f"\n📋 MENU PRINCIPAL")
            print("1. Prendre décisions et jouer le tour")
            print("2. Voir le guide stratégique")
            print("3. Voir les ratios financiers détaillés")
            print("4. Quitter")
            
            try:
                choice = input("\nVotre choix (1-4): ").strip()
                
                if choice == "1":
                    if self.get_decisions():
                        results = self.simulate_and_show_results()
                        
                        # Feedback
                        if results['profit'] < -1500:
                            print("\n⚠️ ALERTE ! Grosses pertes ! Révisez votre stratégie.")
                        elif results['profit'] > 1500:
                            print("\n🎉 EXCELLENT ! Très bon tour !")
                        
                        if results['satisfaction'] < 2.5:
                            print("😞 Satisfaction faible ! Améliorez la qualité ou baissez les prix.")
                        elif results['satisfaction'] > 4.0:
                            print("😊 Clients très satisfaits ! Excellente stratégie.")
                        
                        self.restaurant.turn += 1
                        
                        if self.restaurant.turn <= 10:
                            input("\nAppuyez sur Entrée pour continuer...")
                    else:
                        break
                
                elif choice == "2":
                    self.show_help()
                    input("\nAppuyez sur Entrée pour continuer...")
                
                elif choice == "3":
                    self.show_detailed_finance()
                    input("\nAppuyez sur Entrée pour continuer...")
                
                elif choice == "4":
                    break
                
                else:
                    print("❌ Choix invalide")
            
            except (KeyboardInterrupt, EOFError):
                break
        
        self.show_final_results()
    
    def show_detailed_finance(self):
        """Affiche les finances détaillées."""
        print(f"\n💼 ANALYSE FINANCIÈRE DÉTAILLÉE")
        print("=" * 45)
        
        ratios = self.restaurant.finance.get_financial_ratios(self.restaurant.budget)
        
        print(f"📊 RATIOS FINANCIERS:")
        print(f"   Marge nette: {ratios['net_margin']:.1%}")
        print(f"   ROA: {ratios['roa']:.1%}")
        print(f"   Profit total: {ratios['total_profit']:+,.0f}€")
        
        print(f"\n📈 MARKETING:")
        print(f"   Dépenses totales: {self.restaurant.marketing.total_marketing_spend:,.0f}€")
        print(f"   Campagnes actives: {len([c for c in self.restaurant.marketing.campaigns if c['remaining_turns'] > 0])}")
        
        if self.restaurant.history:
            avg_profit = sum(h['profit'] for h in self.restaurant.history) / len(self.restaurant.history)
            avg_customers = sum(h['customers'] for h in self.restaurant.history) / len(self.restaurant.history)
            print(f"\n📊 MOYENNES:")
            print(f"   Profit moyen/tour: {avg_profit:+,.0f}€")
            print(f"   Clients moyens/tour: {avg_customers:.0f}")
    
    def show_final_results(self):
        """Affiche les résultats finaux."""
        print(f"\n🏁 FIN DE PARTIE - FOODOPS PRO")
        print("=" * 50)
        
        print(f"🏪 Restaurant: {self.restaurant.name}")
        print(f"📅 Tours joués: {self.restaurant.turn - 1}")
        print(f"💰 Budget final: {self.restaurant.budget:,.0f}€")
        print(f"🌟 Réputation finale: {self.restaurant.reputation:.1f}/10")
        
        if self.restaurant.history:
            total_profit = sum(h['profit'] for h in self.restaurant.history)
            total_customers = sum(h['customers'] for h in self.restaurant.history)
            avg_satisfaction = sum(h['satisfaction'] for h in self.restaurant.history) / len(self.restaurant.history)
            max_market_share = max(h['market_share'] for h in self.restaurant.history)
            
            print(f"\n📊 STATISTIQUES FINALES:")
            print(f"   Profit total: {total_profit:+,.0f}€")
            print(f"   Clients totaux servis: {total_customers:,}")
            print(f"   Satisfaction moyenne: {avg_satisfaction:.1f}/5")
            print(f"   Part de marché max: {max_market_share:.1f}%")
            print(f"   Dépenses marketing: {self.restaurant.marketing.total_marketing_spend:,.0f}€")
            
            # Évaluation
            if total_profit > 8000:
                print("\n🏆 MAÎTRE ENTREPRENEUR ! Résultats exceptionnels !")
            elif total_profit > 3000:
                print("\n🥇 EXCELLENT ! Vous maîtrisez la gestion !")
            elif total_profit > 0:
                print("\n✅ BIEN JOUÉ ! Restaurant rentable !")
            else:
                print("\n💪 COURAGE ! L'entrepreneuriat demande de la persévérance !")
        
        print(f"\n🎯 Merci d'avoir joué à FoodOps Pro !")

def main():
    """Point d'entrée principal."""
    try:
        print("🚀 Chargement de FoodOps Pro...")
        game = GameInterfacePro()
        game.play()
    except KeyboardInterrupt:
        print(f"\n\n👋 Au revoir ! Merci d'avoir testé FoodOps Pro !")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("💡 Veuillez signaler ce problème.")

if __name__ == "__main__":
    main()
