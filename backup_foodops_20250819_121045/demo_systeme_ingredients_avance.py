#!/usr/bin/env python3
"""
Démonstration du système d'ingrédients avancé avec qualité, saisonnalité et stocks.
"""

from decimal import Decimal
from datetime import date, timedelta
from src.foodops_pro.domain.ingredient_quality import (
    IngredientQualityManager, QualityLevel, IngredientRange, 
    IngredientVariant, QUALITY_MODIFIERS
)
from src.foodops_pro.domain.seasonality import SeasonalityManager, Season
from src.foodops_pro.domain.stock_advanced import (
    AdvancedStockManager, AdvancedStockLot, WasteReason
)

def demo_quality_system():
    """Démonstration du système de qualité."""
    print("🏆 DÉMONSTRATION DU SYSTÈME DE QUALITÉ")
    print("=" * 60)
    
    quality_manager = IngredientQualityManager()
    
    # Afficher les variantes de steak haché
    beef_variants = quality_manager.get_variants_for_ingredient("beef_ground")
    
    print("\n🥩 VARIANTES DE STEAK HACHÉ:")
    for variant in beef_variants:
        base_cost = Decimal("8.50")  # Prix de référence
        final_cost = variant.calculate_final_cost(base_cost)
        
        print(f"\n{variant.display_name}")
        print(f"   Fournisseur: {variant.supplier_id}")
        print(f"   Prix: {final_cost:.2f}€/kg (base: {base_cost:.2f}€)")
        print(f"   Satisfaction: {variant.modifiers.satisfaction_bonus:+.0%}")
        print(f"   Temps prépa: {variant.modifiers.prep_time_multiplier:.0%}")
        print(f"   Certifications: {', '.join(variant.certifications) if variant.certifications else 'Aucune'}")
    
    # Calcul du score de qualité d'une recette
    print(f"\n📊 SCORE DE QUALITÉ D'UNE RECETTE:")
    recipe_variants = {
        "beef_ground": beef_variants[1],  # Standard
        "tomato": quality_manager.variants["tomato_terroir_5"]  # Luxe
    }
    
    quality_score = quality_manager.calculate_recipe_quality_score(recipe_variants)
    attractiveness_bonus = quality_manager.get_quality_impact_on_attractiveness(quality_score)
    
    print(f"   Score qualité: {quality_score:.1f}/5")
    print(f"   Impact attractivité: {(attractiveness_bonus - 1) * 100:+.0f}%")

def demo_seasonality_system():
    """Démonstration du système de saisonnalité."""
    print("\n\n🌱 DÉMONSTRATION DU SYSTÈME DE SAISONNALITÉ")
    print("=" * 60)
    
    seasonality_manager = SeasonalityManager()
    
    # Test avec différentes dates
    test_dates = [
        (date(2024, 7, 15), "Été"),
        (date(2024, 12, 20), "Hiver"),
        (date(2024, 4, 10), "Printemps")
    ]
    
    base_price_tomato = Decimal("3.20")
    
    for test_date, season_name in test_dates:
        print(f"\n📅 {season_name} ({test_date.strftime('%d/%m/%Y')}):")
        
        # Prix des tomates selon la saison
        final_price = seasonality_manager.calculate_final_price("tomato", base_price_tomato, test_date)
        quality_bonus = seasonality_manager.get_quality_bonus("tomato", test_date)
        demand_impact = seasonality_manager.get_demand_impact("tomato", test_date)
        
        price_change = (final_price / base_price_tomato - 1) * 100
        
        print(f"   🍅 Tomates: {final_price:.2f}€/kg ({price_change:+.0f}%)")
        print(f"   Qualité: {quality_bonus:+d}★")
        print(f"   Demande: {(demand_impact - 1) * 100:+.0f}%")
    
    # Résumé saisonnier actuel
    print(f"\n📊 RÉSUMÉ SAISONNIER ACTUEL:")
    summary = seasonality_manager.get_seasonal_summary()
    
    print(f"   Saison: {summary['season'].title()}")
    print(f"   Mois: {summary['month']}")
    
    if summary['in_season']:
        print(f"   🌱 Produits de saison (prix réduits):")
        for item in summary['in_season']:
            print(f"     • {item['ingredient_id']}: -{item['discount']:.0f}%")
    
    if summary['active_events']:
        print(f"   🎉 Événements actifs:")
        for event in summary['active_events']:
            print(f"     • {event['ingredient_id']}: {event['event']} ({event['price_impact']:+.0f}%)")

def demo_stock_management():
    """Démonstration de la gestion des stocks FEFO."""
    print("\n\n📦 DÉMONSTRATION DE LA GESTION DES STOCKS")
    print("=" * 60)
    
    stock_manager = AdvancedStockManager()
    
    # Ajouter des lots avec différentes dates d'expiration
    today = date.today()
    
    lots = [
        AdvancedStockLot(
            ingredient_id="beef_ground",
            quantity=Decimal("15"),
            unit_cost_ht=Decimal("8.50"),
            purchase_date=today - timedelta(days=1),
            expiry_date=today + timedelta(days=2),  # Expire bientôt
            supplier_id="metro_pro",
            lot_number="LOT001"
        ),
        AdvancedStockLot(
            ingredient_id="beef_ground",
            quantity=Decimal("20"),
            unit_cost_ht=Decimal("8.50"),
            purchase_date=today,
            expiry_date=today + timedelta(days=5),  # Plus frais
            supplier_id="metro_pro",
            lot_number="LOT002"
        ),
        AdvancedStockLot(
            ingredient_id="tomato",
            quantity=Decimal("8"),
            unit_cost_ht=Decimal("3.20"),
            purchase_date=today - timedelta(days=3),
            expiry_date=today + timedelta(days=1),  # Expire demain
            supplier_id="rungis_direct",
            lot_number="LOT003"
        )
    ]
    
    for lot in lots:
        stock_manager.add_lot(lot)
    
    print(f"📊 ÉTAT INITIAL DES STOCKS:")
    for lot in stock_manager.lots:
        print(f"   {lot.ingredient_id} - Lot {lot.lot_number}: {lot.quantity}kg")
        print(f"     Expire dans {lot.days_until_expiry} jours ({lot.status.value})")
    
    # Test de consommation FEFO
    print(f"\n🍽️ CONSOMMATION FEFO (10kg de steak haché):")
    quantity_obtained, lots_used = stock_manager.consume_ingredient("beef_ground", Decimal("10"))
    
    print(f"   Quantité obtenue: {quantity_obtained}kg")
    print(f"   Lots utilisés:")
    for lot in lots_used:
        print(f"     • Lot {lot.lot_number}: {lot.quantity}kg restants")
    
    # Simulation des opérations quotidiennes
    print(f"\n📅 OPÉRATIONS QUOTIDIENNES:")
    daily_report = stock_manager.process_daily_operations()
    
    print(f"   Lots expirés: {daily_report['expired_lots']}")
    print(f"   Valeur des pertes: {daily_report['total_waste_value']:.2f}€")
    
    if daily_report['lots_near_expiry']:
        print(f"   ⚠️ Lots proches expiration:")
        for lot in daily_report['lots_near_expiry']:
            print(f"     • {lot.ingredient_id} Lot {lot.lot_number}: {lot.days_until_expiry} jours")
    
    if daily_report['promotion_candidates']:
        print(f"   🎯 Candidats promotion:")
        for lot in daily_report['promotion_candidates']:
            promo_price = lot.get_promotion_price(Decimal("12.50"))  # Prix menu burger
            print(f"     • {lot.ingredient_id}: Prix promo {promo_price:.2f}€ (-50%)")

def demo_integrated_impact():
    """Démonstration de l'impact intégré sur le gameplay."""
    print("\n\n🎮 IMPACT INTÉGRÉ SUR LE GAMEPLAY")
    print("=" * 60)
    
    print(f"🎯 SCÉNARIO: Restaurant 'Chez Mario' en été")
    print(f"Stratégie: Qualité premium avec produits de saison")
    
    # Managers
    quality_manager = IngredientQualityManager()
    seasonality_manager = SeasonalityManager()
    
    # Date d'été
    summer_date = date(2024, 7, 15)
    
    # Recette: Burger aux tomates
    print(f"\n📋 RECETTE: Burger aux tomates premium")
    
    # Choix des ingrédients
    beef_premium = quality_manager.variants["beef_ground_bio_4"]
    tomato_local = quality_manager.variants["tomato_terroir_5"]
    
    # Calculs de coûts avec saisonnalité
    beef_base_cost = Decimal("8.50")
    tomato_base_cost = Decimal("3.20")
    
    beef_final_cost = beef_premium.calculate_final_cost(beef_base_cost)
    tomato_seasonal_cost = seasonality_manager.calculate_final_price("tomato", tomato_base_cost, summer_date)
    tomato_final_cost = tomato_local.calculate_final_cost(tomato_seasonal_cost)
    
    print(f"\n💰 COÛTS DES INGRÉDIENTS:")
    print(f"   🥩 Steak bio: {beef_final_cost:.2f}€/kg (base: {beef_base_cost:.2f}€)")
    print(f"   🍅 Tomates terroir été: {tomato_final_cost:.2f}€/kg")
    print(f"      (base: {tomato_base_cost:.2f}€, saison: {tomato_seasonal_cost:.2f}€)")
    
    # Score de qualité global
    recipe_variants = {"beef_ground": beef_premium, "tomato": tomato_local}
    quality_score = quality_manager.calculate_recipe_quality_score(recipe_variants)
    attractiveness_bonus = quality_manager.get_quality_impact_on_attractiveness(quality_score)
    
    # Impact saisonnier sur la demande
    tomato_demand_impact = seasonality_manager.get_demand_impact("tomato", summer_date)
    
    print(f"\n📊 IMPACT SUR L'ATTRACTIVITÉ:")
    print(f"   Score qualité: {quality_score:.1f}/5 ⭐")
    print(f"   Bonus attractivité qualité: {(attractiveness_bonus - 1) * 100:+.0f}%")
    print(f"   Bonus demande saisonnière: {(tomato_demand_impact - 1) * 100:+.0f}%")
    print(f"   TOTAL: {((attractiveness_bonus * tomato_demand_impact) - 1) * 100:+.0f}%")
    
    print(f"\n🎯 STRATÉGIE RECOMMANDÉE:")
    print(f"   • Prix justifié: 16-18€ (qualité premium)")
    print(f"   • Communication: 'Tomates du terroir d'été'")
    print(f"   • Positionnement: Restaurant gastronomique")
    print(f"   • ROI: Marge élevée compensant coûts premium")

def main():
    """Démonstration complète du système d'ingrédients avancé."""
    print("🎮 DÉMONSTRATION SYSTÈME D'INGRÉDIENTS AVANCÉ")
    print("=" * 70)
    
    try:
        demo_quality_system()
        demo_seasonality_system()
        demo_stock_management()
        demo_integrated_impact()
        
        print("\n\n🎉 CONCLUSION:")
        print("=" * 30)
        print("✅ Système de qualité opérationnel")
        print("✅ Saisonnalité implémentée")
        print("✅ Gestion FEFO fonctionnelle")
        print("✅ Impact gameplay intégré")
        print("🎯 Le jeu offre maintenant une vraie différenciation !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
