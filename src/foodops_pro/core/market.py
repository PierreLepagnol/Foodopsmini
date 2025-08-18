"""
Moteur de marché et allocation de la demande pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
import random

from ..domain.restaurant import Restaurant
from ..domain.scenario import Scenario, MarketSegment


@dataclass
class AllocationResult:
    """
    Résultat de l'allocation de marché pour un restaurant.
    
    Attributes:
        restaurant_id: ID du restaurant
        allocated_demand: Demande allouée
        served_customers: Clients effectivement servis
        capacity: Capacité disponible
        utilization_rate: Taux d'utilisation
        lost_customers: Clients perdus (capacité insuffisante)
        revenue: Chiffre d'affaires généré
        average_ticket: Ticket moyen
    """
    
    restaurant_id: str
    allocated_demand: int = 0
    served_customers: int = 0
    capacity: int = 0
    utilization_rate: Decimal = Decimal("0")
    lost_customers: int = 0
    revenue: Decimal = Decimal("0")
    average_ticket: Decimal = Decimal("0")
    
    def __post_init__(self) -> None:
        """Calcule les métriques dérivées."""
        if self.capacity > 0:
            object.__setattr__(self, 'utilization_rate', Decimal(self.served_customers) / Decimal(self.capacity))
        object.__setattr__(self, 'lost_customers', max(0, self.allocated_demand - self.served_customers))
        if self.served_customers > 0:
            object.__setattr__(self, 'average_ticket', self.revenue / Decimal(self.served_customers))


class MarketEngine:
    """
    Moteur de simulation du marché avec allocation de la demande.
    """
    
    def __init__(self, scenario: Scenario, random_seed: Optional[int] = None) -> None:
        """
        Initialise le moteur de marché.
        
        Args:
            scenario: Scénario de jeu
            random_seed: Graine aléatoire pour reproductibilité
        """
        self.scenario = scenario
        self.rng = random.Random(random_seed or scenario.random_seed)
        self.turn_history: List[Dict[str, AllocationResult]] = []
    
    def allocate_demand(self, restaurants: List[Restaurant], 
                       turn: int, month: int = 1) -> Dict[str, AllocationResult]:
        """
        Alloue la demande entre les restaurants selon leurs caractéristiques.
        
        Args:
            restaurants: Liste des restaurants en concurrence
            turn: Numéro du tour
            month: Mois de l'année (pour saisonnalité)
            
        Returns:
            Dict des résultats d'allocation par restaurant
        """
        # Calcul de la demande totale avec bruit
        base_demand = self.scenario.calculate_total_demand(turn, month)
        noise_factor = 1 + self.rng.uniform(-float(self.scenario.demand_noise), 
                                           float(self.scenario.demand_noise))
        total_demand = int(base_demand * noise_factor)
        
        # Allocation par segment de marché
        results = {}
        total_allocated = 0
        
        for segment in self.scenario.segments:
            segment_demand = int(total_demand * segment.share)
            segment_allocation = self._allocate_segment_demand(
                restaurants, segment, segment_demand
            )
            
            # Agrégation des résultats
            for restaurant_id, allocation in segment_allocation.items():
                if restaurant_id not in results:
                    results[restaurant_id] = AllocationResult(restaurant_id=restaurant_id)
                
                results[restaurant_id].allocated_demand += allocation['demand']
                total_allocated += allocation['demand']
        
        # Application des contraintes de capacité et redistribution
        results = self._apply_capacity_constraints(restaurants, results)

        # S'assurer que la capacité est définie dans les résultats
        for restaurant in restaurants:
            if restaurant.id in results:
                results[restaurant.id].capacity = restaurant.capacity_current
        
        # Calcul des revenus
        for restaurant in restaurants:
            if restaurant.id in results:
                results[restaurant.id] = self._calculate_revenue(restaurant, results[restaurant.id])
        
        # Sauvegarde de l'historique
        self.turn_history.append(results.copy())
        
        return results
    
    def _allocate_segment_demand(self, restaurants: List[Restaurant], 
                               segment: MarketSegment, 
                               segment_demand: int) -> Dict[str, Dict[str, int]]:
        """
        Alloue la demande d'un segment spécifique.
        
        Args:
            restaurants: Liste des restaurants
            segment: Segment de marché
            segment_demand: Demande du segment
            
        Returns:
            Allocation par restaurant
        """
        # Calcul des scores d'attractivité
        scores = {}
        for restaurant in restaurants:
            if restaurant.staffing_level == 0:  # Restaurant fermé
                scores[restaurant.id] = 0
                continue
            
            score = self._calculate_attraction_score(restaurant, segment)
            scores[restaurant.id] = score
        
        total_score = sum(scores.values())
        if total_score == 0:
            # Aucun restaurant attractif pour ce segment
            return {r.id: {'demand': 0} for r in restaurants}
        
        # Répartition proportionnelle
        allocation = {}
        for restaurant in restaurants:
            if scores[restaurant.id] > 0:
                allocated = int(segment_demand * scores[restaurant.id] / total_score)
                allocation[restaurant.id] = {'demand': allocated}
            else:
                allocation[restaurant.id] = {'demand': 0}
        
        return allocation

    def _calculate_attraction_score(self, restaurant: Restaurant,
                                  segment: MarketSegment) -> Decimal:
        """
        Calcule le score d'attractivité d'un restaurant pour un segment.

        Args:
            restaurant: Restaurant évalué
            segment: Segment de marché

        Returns:
            Score d'attractivité
        """
        # Affinité pour le type de restaurant
        type_affinity = segment.get_type_affinity(restaurant.type)

        # Facteur prix basé sur le ticket moyen
        average_ticket = restaurant.get_average_ticket()
        price_factor = self._calculate_price_factor(average_ticket, segment)

        # Facteur qualité (proxy basé sur le coût des ingrédients)
        quality_factor = self._calculate_quality_factor(restaurant, segment)

        # Score final
        score = type_affinity * price_factor * quality_factor

        # Bonus/malus selon le niveau de staffing
        staffing_bonus = {
            0: Decimal("0"),     # Fermé
            1: Decimal("0.8"),   # Léger
            2: Decimal("1.0"),   # Normal
            3: Decimal("1.2")    # Renforcé
        }

        score *= staffing_bonus.get(restaurant.staffing_level, Decimal("1.0"))

        return max(Decimal("0"), score)

    def _calculate_price_factor(self, average_ticket: Decimal,
                              segment: MarketSegment) -> Decimal:
        """
        Calcule le facteur d'attractivité lié au prix.

        Args:
            average_ticket: Ticket moyen du restaurant
            segment: Segment de marché

        Returns:
            Facteur prix (0.0 à 2.0)
        """
        if average_ticket <= 0:
            return Decimal("0.5")  # Prix non défini

        budget = segment.budget
        sensitivity = segment.price_sensitivity

        # Ratio prix/budget
        price_ratio = average_ticket / budget

        if price_ratio <= Decimal("0.8"):
            # Prix très attractif
            return Decimal("1.5") * (2 - sensitivity)
        elif price_ratio <= Decimal("1.0"):
            # Prix dans le budget
            return Decimal("1.2") * (2 - sensitivity)
        elif price_ratio <= Decimal("1.2"):
            # Prix légèrement au-dessus
            return Decimal("0.8") * (2 - sensitivity)
        elif price_ratio <= Decimal("1.5"):
            # Prix élevé mais acceptable
            return Decimal("0.4") * (2 - sensitivity)
        else:
            # Prix trop élevé
            return Decimal("0.1") * (2 - sensitivity)

    def _calculate_quality_factor(self, restaurant: Restaurant,
                                segment: MarketSegment) -> Decimal:
        """
        Calcule le facteur qualité perçue.

        Args:
            restaurant: Restaurant évalué
            segment: Segment de marché

        Returns:
            Facteur qualité (0.5 à 1.5)
        """
        # Proxy qualité basé sur le type de restaurant et le staffing
        base_quality = {
            'fast': Decimal("0.8"),
            'classic': Decimal("1.0"),
            'gastronomique': Decimal("1.3"),
            'brasserie': Decimal("1.1")
        }

        quality = base_quality.get(restaurant.type.value, Decimal("1.0"))

        # Ajustement selon le staffing
        staffing_quality = {
            0: Decimal("0.5"),   # Fermé
            1: Decimal("0.8"),   # Léger
            2: Decimal("1.0"),   # Normal
            3: Decimal("1.2")    # Renforcé
        }

        quality *= staffing_quality.get(restaurant.staffing_level, Decimal("1.0"))

        # Application de la sensibilité qualité du segment
        sensitivity = segment.quality_sensitivity
        adjusted_quality = Decimal("1.0") + (quality - Decimal("1.0")) * sensitivity

        return max(Decimal("0.5"), min(Decimal("1.5"), adjusted_quality))

    def _apply_capacity_constraints(self, restaurants: List[Restaurant],
                                  results: Dict[str, AllocationResult]) -> Dict[str, AllocationResult]:
        """
        Applique les contraintes de capacité et redistribue la demande excédentaire.

        Args:
            restaurants: Liste des restaurants
            results: Résultats d'allocation initiaux

        Returns:
            Résultats ajustés avec contraintes de capacité
        """
        # Mise à jour des capacités
        for restaurant in restaurants:
            if restaurant.id in results:
                results[restaurant.id].capacity = restaurant.capacity_current

        # Première passe : application des contraintes
        total_overflow = 0
        available_capacity = 0

        for restaurant in restaurants:
            if restaurant.id not in results:
                continue

            result = results[restaurant.id]
            capacity = restaurant.capacity_current

            if result.allocated_demand > capacity:
                # Demande excédentaire
                overflow = result.allocated_demand - capacity
                total_overflow += overflow
                result.served_customers = capacity
            else:
                # Capacité disponible
                result.served_customers = result.allocated_demand
                spare = capacity - result.allocated_demand
                available_capacity += spare

        # Redistribution de la demande excédentaire
        if total_overflow > 0 and available_capacity > 0:
            redistributed = min(total_overflow, available_capacity)

            for restaurant in restaurants:
                if restaurant.id not in results:
                    continue

                result = results[restaurant.id]
                spare = result.capacity - result.served_customers

                if spare > 0:
                    # Redistribution proportionnelle à la capacité libre
                    additional = int(redistributed * spare / available_capacity)
                    additional = min(additional, spare)
                    result.served_customers += additional

        return results

    def _calculate_revenue(self, restaurant: Restaurant,
                         result: AllocationResult) -> AllocationResult:
        """
        Calcule le chiffre d'affaires d'un restaurant.

        Args:
            restaurant: Restaurant concerné
            result: Résultat d'allocation

        Returns:
            Résultat avec revenus calculés
        """
        if result.served_customers == 0:
            return result

        # Revenus basés sur le menu actif
        active_menu = restaurant.get_active_menu()
        if not active_menu:
            return result

        # Simulation de la répartition des commandes
        total_revenue = Decimal("0")
        customers_served = result.served_customers

        # Répartition équitable entre les plats actifs (simplification)
        recipes_count = len(active_menu)
        if recipes_count > 0:
            customers_per_recipe = customers_served // recipes_count
            remaining_customers = customers_served % recipes_count

            for i, (recipe_id, price) in enumerate(active_menu.items()):
                recipe_customers = customers_per_recipe
                if i < remaining_customers:
                    recipe_customers += 1

                total_revenue += price * recipe_customers

        result.revenue = total_revenue

        # Recalculer les métriques dérivées
        if result.capacity > 0:
            result.utilization_rate = Decimal(result.served_customers) / Decimal(result.capacity)
        result.lost_customers = max(0, result.allocated_demand - result.served_customers)
        if result.served_customers > 0:
            result.average_ticket = result.revenue / Decimal(result.served_customers)

        return result

    def get_market_share(self, restaurant_id: str, turn: int = -1) -> Decimal:
        """
        Calcule la part de marché d'un restaurant.

        Args:
            restaurant_id: ID du restaurant
            turn: Tour à analyser (-1 pour le dernier)

        Returns:
            Part de marché (0.0 à 1.0)
        """
        if not self.turn_history:
            return Decimal("0")

        turn_data = self.turn_history[turn]
        total_customers = sum(result.served_customers for result in turn_data.values())

        if total_customers == 0:
            return Decimal("0")

        restaurant_customers = turn_data.get(restaurant_id, AllocationResult(restaurant_id)).served_customers
        return Decimal(restaurant_customers) / Decimal(total_customers)

    def get_market_analysis(self, turn: int = -1) -> Dict[str, any]:
        """
        Génère une analyse du marché pour un tour donné.

        Args:
            turn: Tour à analyser (-1 pour le dernier)

        Returns:
            Analyse du marché
        """
        if not self.turn_history:
            return {}

        turn_data = self.turn_history[turn]

        total_demand = sum(result.allocated_demand for result in turn_data.values())
        total_served = sum(result.served_customers for result in turn_data.values())
        total_capacity = sum(result.capacity for result in turn_data.values())
        total_revenue = sum(result.revenue for result in turn_data.values())

        return {
            'total_demand': total_demand,
            'total_served': total_served,
            'total_capacity': total_capacity,
            'total_revenue': float(total_revenue),
            'market_utilization': float(Decimal(total_served) / Decimal(total_capacity)) if total_capacity > 0 else 0,
            'demand_satisfaction': float(Decimal(total_served) / Decimal(total_demand)) if total_demand > 0 else 0,
            'average_ticket': float(total_revenue / Decimal(total_served)) if total_served > 0 else 0
        }
