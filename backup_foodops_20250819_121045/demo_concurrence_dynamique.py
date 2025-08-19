#!/usr/bin/env python3
"""
Démonstration du système de concurrence dynamique avec événements aléatoires.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from decimal import Decimal
from datetime import date
from src.foodops_pro.domain.competition import CompetitionManager, EventType, EventImpact

def demo_market_events():
    """Démonstration des événements de marché."""
    print("🎲 DÉMONSTRATION ÉVÉNEMENTS DE MARCHÉ")
    print("=" * 70)
    
    competition = CompetitionManager(random_seed=42)
    
    print(f"\n📋 ÉVÉNEMENTS DISPONIBLES ({len(competition.available_events)}):")
    
    # Grouper par type
    events_by_type = {}
    for event in competition.available_events:
        if event.type not in events_by_type:
            events_by_type[event.type] = []
        events_by_type[event.type].append(event)
    
    for event_type, events in events_by_type.items():
        print(f"\n🎯 {event_type.value.upper()}:")
        for event in events:
            impact_icon = {"positif": "📈", "negatif": "📉", "neutre": "⚖️"}[event.impact.value]
            print(f"   {impact_icon} {event.name} (prob: {event.probability:.1%})")
            print(f"      {event.description}")
            print(f"      Durée: {event.duration_days} jours")
            
            # Afficher l'impact
            impact_desc = competition.get_event_impact_description(event)
            if impact_desc != "Aucun impact direct":
                print(f"      Impact: {impact_desc}")
    
    return competition

def demo_event_simulation():
    """Simulation d'événements sur plusieurs tours."""
    print(f"\n\n🎮 SIMULATION ÉVÉNEMENTS SUR 10 TOURS")
    print("=" * 70)
    
    competition = CompetitionManager(random_seed=123)  # Seed différent pour plus d'événements
    
    seasons = ["hiver", "hiver", "printemps", "printemps", "printemps", 
               "été", "été", "été", "automne", "automne"]
    
    all_events = []
    
    for turn in range(1, 11):
        current_season = seasons[turn - 1]
        print(f"\n--- TOUR {turn} ({current_season.upper()}) ---")
        
        # Traiter les événements
        new_events = competition.process_turn_events(turn, current_season)
        
        if new_events:
            print(f"🎲 NOUVEAUX ÉVÉNEMENTS ({len(new_events)}):")
            for event in new_events:
                impact_icon = {"positif": "📈", "negatif": "📉", "neutre": "⚖️"}[event.impact.value]
                print(f"   {impact_icon} {event.name}")
                print(f"      {event.description}")
                print(f"      Durée: {event.duration_days} jours")
                all_events.append(event)
        else:
            print("🔹 Aucun nouvel événement")
        
        # Afficher les événements actifs
        active_events = [e for e in competition.active_events if e.duration_days > 0]
        if active_events:
            print(f"\n⚡ ÉVÉNEMENTS ACTIFS ({len(active_events)}):")
            for event in active_events:
                print(f"   • {event.name} (reste {event.duration_days} jours)")
        
        # Afficher les modificateurs de marché
        modifiers = competition.get_market_modifiers()
        print(f"\n📊 MODIFICATEURS DE MARCHÉ:")
        print(f"   Demande globale: {modifiers['demand_modifier']:.1%}")
        print(f"   Sensibilité prix: {modifiers['price_sensitivity_modifier']:.1%}")
        print(f"   Importance qualité: {modifiers['quality_importance_modifier']:.1%}")
        
        if modifiers['segment_modifiers']:
            print(f"   Segments spécifiques:")
            for segment, modifier in modifiers['segment_modifiers'].items():
                print(f"     • {segment}: {modifier:.1%}")
    
    print(f"\n📈 RÉSUMÉ DE LA SIMULATION:")
    print(f"   Total événements déclenchés: {len(all_events)}")
    print(f"   Événements positifs: {len([e for e in all_events if e.impact == EventImpact.POSITIVE])}")
    print(f"   Événements négatifs: {len([e for e in all_events if e.impact == EventImpact.NEGATIVE])}")
    print(f"   Événements neutres: {len([e for e in all_events if e.impact == EventImpact.NEUTRAL])}")

def demo_competitor_actions():
    """Démonstration des actions des concurrents IA."""
    print(f"\n\n🤖 DÉMONSTRATION ACTIONS CONCURRENTS IA")
    print("=" * 70)
    
    competition = CompetitionManager(random_seed=456)
    
    # Simuler des données de marché
    market_data = {
        "average_margin": 0.15,
        "market_growth": 0.05,
        "competitive_intensity": 0.7
    }
    
    print(f"📊 DONNÉES DE MARCHÉ:")
    print(f"   Marge moyenne: {market_data['average_margin']:.1%}")
    print(f"   Croissance: {market_data['market_growth']:.1%}")
    print(f"   Intensité concurrentielle: {market_data['competitive_intensity']:.1%}")
    
    all_actions = []
    
    for turn in range(1, 8):
        print(f"\n--- TOUR {turn} ---")
        
        # Simuler les actions des concurrents
        actions = competition.simulate_competitor_actions(turn, market_data)
        
        if actions:
            print(f"🎯 ACTIONS CONCURRENTS ({len(actions)}):")
            for action in actions:
                print(f"   🤖 {action.competitor_id}:")
                print(f"      Action: {action.action_type}")
                print(f"      Description: {action.parameters.get('description', 'N/A')}")
                
                # Détails spécifiques selon le type d'action
                if action.action_type == "price_reduction":
                    change = action.parameters.get('price_change', 0) * 100
                    print(f"      Réduction prix: {change:.1f}%")
                elif action.action_type == "quality_upgrade":
                    improvement = action.parameters.get('quality_improvement', 0) * 100
                    print(f"      Amélioration qualité: +{improvement:.1f}%")
                elif action.action_type == "marketing_campaign":
                    boost = action.parameters.get('marketing_boost', 0) * 100
                    duration = action.parameters.get('duration', 0)
                    print(f"      Boost marketing: +{boost:.1f}% pendant {duration} jours")
                elif action.action_type == "menu_expansion":
                    new_options = action.parameters.get('new_options', 0)
                    boost = action.parameters.get('attractiveness_boost', 0) * 100
                    print(f"      Nouveaux plats: {new_options}, attractivité: +{boost:.1f}%")
                
                print(f"      Durée d'impact: {action.impact_duration} tours")
                all_actions.append(action)
        else:
            print("🔹 Aucune action concurrent ce tour")
        
        # Mettre à jour la pression concurrentielle
        performance = {"restaurant_1": 0.12, "restaurant_2": 0.18, "restaurant_3": 0.15}
        competition.update_competitive_pressure(performance)
        
        print(f"📈 Pression concurrentielle: {competition.competitive_pressure:.2f}")
    
    print(f"\n📊 RÉSUMÉ ACTIONS CONCURRENTS:")
    action_types = {}
    for action in all_actions:
        if action.action_type not in action_types:
            action_types[action.action_type] = 0
        action_types[action.action_type] += 1
    
    for action_type, count in action_types.items():
        print(f"   • {action_type}: {count} fois")

def demo_integrated_impact():
    """Démonstration de l'impact intégré événements + concurrence."""
    print(f"\n\n🎯 IMPACT INTÉGRÉ ÉVÉNEMENTS + CONCURRENCE")
    print("=" * 70)
    
    competition = CompetitionManager(random_seed=789)
    
    # Scénario : Restaurant en difficulté face à la concurrence
    print(f"📖 SCÉNARIO: Restaurant 'Chez Mario' face à la concurrence")
    print(f"   Situation initiale: Marge 12%, part de marché 25%")
    print(f"   Objectif: Maintenir la position malgré la pression")
    
    restaurant_performance = {
        "margin": 0.12,
        "market_share": 0.25,
        "customer_satisfaction": 3.8
    }
    
    for turn in range(1, 6):
        print(f"\n--- TOUR {turn} ---")
        
        # Événements de marché
        season = ["hiver", "printemps", "été", "automne", "hiver"][turn - 1]
        new_events = competition.process_turn_events(turn, season)
        
        # Actions concurrents
        market_data = {"average_margin": restaurant_performance["margin"]}
        competitor_actions = competition.simulate_competitor_actions(turn, market_data)
        
        # Calculer l'impact combiné
        modifiers = competition.get_market_modifiers()
        
        # Impact sur le restaurant
        demand_impact = float(modifiers["demand_modifier"])
        price_sensitivity_impact = float(modifiers["price_sensitivity_modifier"])
        
        # Simuler l'évolution des performances
        if new_events:
            print(f"🎲 ÉVÉNEMENTS:")
            for event in new_events:
                impact_icon = {"positif": "📈", "negatif": "📉", "neutre": "⚖️"}[event.impact.value]
                print(f"   {impact_icon} {event.name}")
                
                # Impact sur les performances du restaurant
                if event.impact == EventImpact.POSITIVE:
                    restaurant_performance["market_share"] *= 1.05
                    restaurant_performance["customer_satisfaction"] += 0.1
                elif event.impact == EventImpact.NEGATIVE:
                    restaurant_performance["market_share"] *= 0.95
                    restaurant_performance["customer_satisfaction"] -= 0.1
        
        if competitor_actions:
            print(f"🤖 ACTIONS CONCURRENTS:")
            for action in competitor_actions:
                print(f"   • {action.action_type}")
                
                # Impact sur notre restaurant
                if action.action_type == "price_reduction":
                    restaurant_performance["market_share"] *= 0.92  # Perte de parts
                elif action.action_type == "marketing_campaign":
                    restaurant_performance["market_share"] *= 0.95
        
        # Afficher l'état du restaurant
        print(f"\n📊 ÉTAT DU RESTAURANT:")
        print(f"   Marge: {restaurant_performance['margin']:.1%}")
        print(f"   Part de marché: {restaurant_performance['market_share']:.1%}")
        print(f"   Satisfaction: {restaurant_performance['customer_satisfaction']:.1f}/5")
        
        # Recommandations stratégiques
        if restaurant_performance["market_share"] < 0.20:
            print(f"⚠️ ALERTE: Part de marché critique ! Recommandations:")
            print(f"   • Lancer une campagne marketing")
            print(f"   • Améliorer la qualité")
            print(f"   • Revoir la stratégie prix")
        elif restaurant_performance["market_share"] > 0.30:
            print(f"✅ SUCCÈS: Position renforcée !")
    
    # Résumé final
    final_share = restaurant_performance["market_share"]
    evolution = (final_share - 0.25) / 0.25 * 100
    
    print(f"\n🎯 RÉSULTAT FINAL:")
    print(f"   Part de marché finale: {final_share:.1%}")
    print(f"   Évolution: {evolution:+.1f}%")
    
    if evolution > 0:
        print(f"   🏆 Succès ! Le restaurant a résisté à la concurrence")
    else:
        print(f"   📉 Difficultés. Stratégie à revoir.")

def main():
    """Démonstration complète du système de concurrence."""
    print("🎮 DÉMONSTRATION SYSTÈME CONCURRENCE DYNAMIQUE")
    print("=" * 80)
    
    try:
        demo_market_events()
        demo_event_simulation()
        demo_competitor_actions()
        demo_integrated_impact()
        
        print(f"\n\n🎉 SYSTÈME CONCURRENCE DYNAMIQUE OPÉRATIONNEL !")
        print("=" * 70)
        print("✅ Événements aléatoires avec impacts réalistes")
        print("✅ Actions concurrents IA intelligentes")
        print("✅ Modificateurs de marché dynamiques")
        print("✅ Pression concurrentielle adaptative")
        print("✅ Intégration complète dans le gameplay")
        print("✅ Variabilité et rejouabilité maximales")
        print("")
        print("🎯 FoodOps Pro offre maintenant une expérience")
        print("   de marché vivante et imprévisible !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
