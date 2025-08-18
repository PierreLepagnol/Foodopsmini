#!/usr/bin/env python3
"""
Test simple du système de concurrence.
"""

def analyze_current_competition():
    """Analyse le système de concurrence actuel."""
    print("🔍 ANALYSE DU SYSTÈME DE CONCURRENCE ACTUEL")
    print("=" * 60)
    
    print("\n📊 COMMENT LES VENTES SONT SIMULÉES :")
    print("1. Demande totale: 420 clients ± 8% de bruit")
    print("2. Répartition par segments:")
    print("   - Étudiants: 35% (147 clients, budget 11€)")
    print("   - Familles: 40% (168 clients, budget 17€)")
    print("   - Foodies: 25% (105 clients, budget 25€)")
    
    print("\n3. Pour chaque segment, calcul du score d'attractivité:")
    print("   Score = Affinité_type × Facteur_prix")
    print("   - Affinité_type: fast=1.2, classic=0.7 (pour étudiants)")
    print("   - Facteur_prix: bonus si prix < budget, malus si prix > budget")
    
    print("\n4. Allocation proportionnelle aux scores")
    print("5. Application des contraintes de capacité")
    print("6. Redistribution des clients refusés")
    
    print("\n❌ PROBLÈMES IDENTIFIÉS :")
    print("1. TROP PRÉVISIBLE")
    print("   → Même prix = même résultat à chaque fois")
    print("   → Pas de variabilité dans les goûts clients")
    
    print("\n2. SEGMENTS TROP RIGIDES")
    print("   → Étudiants vont TOUJOURS au fast-food")
    print("   → Pas de clients qui changent de segment")
    
    print("\n3. PRIX DOMINE TOUT")
    print("   → Prix bas = victoire garantie")
    print("   → Qualité, service, ambiance ignorés")
    
    print("\n4. PAS D'EFFETS DYNAMIQUES")
    print("   → Pas de fidélisation")
    print("   → Pas de bouche-à-oreille")
    print("   → Pas d'effet de réputation")

def simulate_competition_example():
    """Simule un exemple de concurrence."""
    print("\n\n🎮 EXEMPLE DE SIMULATION")
    print("=" * 60)
    
    # Paramètres de test
    segments = [
        {"name": "Étudiants", "clients": 147, "budget": 11.0, "affinite": {"fast": 1.2, "classic": 0.7}},
        {"name": "Familles", "clients": 168, "budget": 17.0, "affinite": {"fast": 0.9, "classic": 1.0}},
        {"name": "Foodies", "clients": 105, "budget": 25.0, "affinite": {"fast": 0.6, "classic": 1.3}},
    ]
    
    restaurants = [
        {"name": "Quick Burger", "type": "fast", "prix": 10.0, "capacite": 168},
        {"name": "Chez Papa", "type": "classic", "prix": 16.0, "capacite": 60},
    ]
    
    print("Restaurants en concurrence:")
    for r in restaurants:
        print(f"  {r['name']} ({r['type']}): {r['prix']}€, capacité {r['capacite']}")
    
    total_allocation = {r['name']: 0 for r in restaurants}
    
    print("\nAllocation par segment:")
    for segment in segments:
        print(f"\n{segment['name']} ({segment['clients']} clients, budget {segment['budget']}€):")
        
        # Calcul des scores
        scores = {}
        for r in restaurants:
            affinite = segment['affinite'][r['type']]
            
            # Facteur prix simplifié
            if r['prix'] <= segment['budget']:
                facteur_prix = 1.0 + (segment['budget'] - r['prix']) / segment['budget'] * 0.3
            elif r['prix'] <= segment['budget'] * 1.15:
                facteur_prix = 0.8
            else:
                facteur_prix = 0.0
            
            score = affinite * facteur_prix
            scores[r['name']] = score
            
            print(f"  {r['name']}: affinité {affinite:.1f} × prix {facteur_prix:.2f} = {score:.2f}")
        
        # Allocation proportionnelle
        total_score = sum(scores.values())
        if total_score > 0:
            for r in restaurants:
                allocation = segment['clients'] * (scores[r['name']] / total_score)
                total_allocation[r['name']] += allocation
                print(f"    → {r['name']}: {allocation:.0f} clients ({allocation/segment['clients']:.1%})")
    
    print(f"\nAllocation totale avant capacité:")
    for r in restaurants:
        print(f"  {r['name']}: {total_allocation[r['name']]:.0f} clients demandés")
    
    # Application des contraintes de capacité
    print(f"\nAprès contraintes de capacité:")
    clients_perdus = 0
    for r in restaurants:
        demande = int(total_allocation[r['name']])
        capacite = r['capacite']
        servi = min(demande, capacite)
        perdu = max(0, demande - capacite)
        clients_perdus += perdu
        
        ca = servi * r['prix']
        part_marche = servi / sum(min(int(total_allocation[resto['name']]), resto['capacite']) for resto in restaurants) * 100
        
        print(f"  {r['name']}: {servi}/{demande} clients, CA {ca:.0f}€, part {part_marche:.1f}%")
        if perdu > 0:
            print(f"    ❌ {perdu} clients perdus (capacité insuffisante)")
    
    print(f"\nClients totaux perdus: {clients_perdus}")

def propose_improvements():
    """Propose des améliorations pour la concurrence."""
    print("\n\n💡 AMÉLIORATIONS PROPOSÉES")
    print("=" * 60)
    
    print("1. 🎲 VARIABILITÉ ET ALÉATOIRE")
    print("   → Préférences clients variables (+/- 20%)")
    print("   → Événements aléatoires (grève, festival)")
    print("   → Météo affectant la demande")
    
    print("\n2. 🏆 FACTEURS DE QUALITÉ")
    print("   → Score qualité basé sur les ingrédients")
    print("   → Vitesse de service (temps d'attente)")
    print("   → Ambiance et décoration")
    
    print("\n3. 📈 EFFETS DYNAMIQUES")
    print("   → Réputation qui évolue selon les performances")
    print("   → Fidélisation client (bonus pour clients réguliers)")
    print("   → Bouche-à-oreille (bon/mauvais buzz)")
    
    print("\n4. 🎯 SEGMENTATION PLUS FINE")
    print("   → Sous-segments avec préférences spécifiques")
    print("   → Clients qui changent de segment selon l'offre")
    print("   → Sensibilité prix variable selon le contexte")
    
    print("\n5. 🔄 MÉCANIQUES DE CONCURRENCE")
    print("   → Guerre des prix avec conséquences")
    print("   → Différenciation récompensée")
    print("   → Positionnement stratégique")
    
    print("\n6. 📊 FEEDBACK AMÉLIORÉ")
    print("   → Pourquoi j'ai perdu/gagné des clients")
    print("   → Analyse de la concurrence")
    print("   → Suggestions d'amélioration")

def main():
    """Analyse complète."""
    analyze_current_competition()
    simulate_competition_example()
    propose_improvements()
    
    print("\n\n🎯 CONCLUSION:")
    print("Le système actuel est trop prévisible et manque de dynamisme.")
    print("Il faut ajouter de la variabilité et des facteurs de différenciation.")

if __name__ == "__main__":
    main()
