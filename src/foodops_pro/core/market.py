"""
Moteur de marché et allocation de la demande pour FoodOps Pro.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
import random

from ..domain.restaurant import Restaurant
from ..domain.scenario import Scenario, MarketSegment
from ..domain.seasonality import SeasonalityManager
from ..domain.competition import CompetitionManager


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
    recipe_sales: Dict[str, int] = field(default_factory=dict)


    def __post_init__(self) -> None:
        """Calcule les métriques dérivées."""
        if self.capacity > 0:
            object.__setattr__(
                self,
                "utilization_rate",
                Decimal(self.served_customers) / Decimal(self.capacity),
            )
        object.__setattr__(
            self,
            "lost_customers",
            max(0, self.allocated_demand - self.served_customers),
        )
        if self.served_customers > 0:
            object.__setattr__(
                self, "average_ticket", self.revenue / Decimal(self.served_customers)
            )


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
        # Exposition des facteurs pour affichage des résultats
        self._last_factors_by_restaurant: Dict[str, Dict[str, Decimal]] = {}

        self.scenario = scenario
        self.rng = random.Random(random_seed or scenario.random_seed)
        self.turn_history: List[Dict[str, AllocationResult]] = []
        self.seasonality_manager = SeasonalityManager()  # Gestionnaire saisonnalité
        self.competition_manager = CompetitionManager(
            random_seed
        )  # NOUVEAU: Gestionnaire concurrence

    def allocate_demand(
        self, restaurants: List[Restaurant], turn: int, month: int = 1
    ) -> Dict[str, AllocationResult]:
        """
        Alloue la demande entre les restaurants selon leurs caractéristiques.

        Args:
            restaurants: Liste des restaurants en concurrence
            turn: Numéro du tour
            month: Mois de l'année (pour saisonnalité)

        Returns:
            Dict des résultats d'allocation par restaurant
        """
        # NOUVEAU: Traiter les événements de marché
        current_season = self._get_season_name(month)
        new_events = self.competition_manager.process_turn_events(turn, current_season)
        market_modifiers = self.competition_manager.get_market_modifiers()

        # Calcul de la demande totale avec bruit et événements
        base_demand = self.scenario.calculate_total_demand(turn, month)
        noise_factor = 1 + self.rng.uniform(
            -float(self.scenario.demand_noise), float(self.scenario.demand_noise)
        )
        event_demand_modifier = float(market_modifiers["demand_modifier"])
        total_demand = int(base_demand * noise_factor * event_demand_modifier)

        # Allocation par segment de marché
        results = {}
        total_allocated = 0

        for segment in self.scenario.segments:
            base_segment_demand = int(total_demand * segment.share)

            # NOUVEAU: Application de la saisonnalité
            seasonal_bonus = self._get_seasonal_demand_bonus(segment.name, month)
            segment_demand = int(base_segment_demand * seasonal_bonus)

            segment_allocation = self._allocate_segment_demand(
                restaurants, segment, segment_demand
            )

            # Agrégation des résultats
            for restaurant_id, allocation in segment_allocation.items():
                if restaurant_id not in results:
                    results[restaurant_id] = AllocationResult(
                        restaurant_id=restaurant_id
                    )

                results[restaurant_id].allocated_demand += allocation["demand"]
                total_allocated += allocation["demand"]
                # NOUVEAU: ventes par recette si disponibles
                if "recipe_sales" in allocation:
                    for rid, sold_qty in allocation["recipe_sales"].items():
                        results[restaurant_id].recipe_sales[rid] = results[restaurant_id].recipe_sales.get(rid, 0) + int(sold_qty)

        # Application des contraintes de capacité et redistribution
        results = self._apply_capacity_constraints(restaurants, results)

        # Si des unités prêtes sont disponibles (production-aware), limiter le servi au minimum(capacité, unités prêtes)
        try:
            for restaurant in restaurants:
                units_ready = getattr(restaurant, "production_units_ready", None)
                if units_ready is None or restaurant.id not in results:
                    continue
                # Approximation: somme des unités prêtes toutes recettes confondues
                total_units_ready = sum(int(v) for v in units_ready.values())
                res = results[restaurant.id]
                res.served_customers = min(res.served_customers, total_units_ready)
        except Exception:
            # En cas d'erreur on garde le comportement classique
            pass

        # S'assurer que la capacité est définie dans les résultats
        for restaurant in restaurants:
            if restaurant.id in results:
                results[restaurant.id].capacity = restaurant.capacity_current

        # Calcul des revenus
        for restaurant in restaurants:
            if restaurant.id in results:
                results[restaurant.id] = self._calculate_revenue(
                    restaurant, results[restaurant.id]
                )

        # Sauvegarde de l'historique
        self.turn_history.append(results.copy())

        return results

    def _allocate_segment_demand(
        self, restaurants: List[Restaurant], segment: MarketSegment, segment_demand: int
    ) -> Dict[str, Dict[str, int]]:
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
                scores[restaurant.id] = Decimal("0")
                continue
            scores[restaurant.id] = self._calculate_attraction_score(restaurant, segment)

        # Mode production-aware + reroutage si des unités prêtes existent
        has_units = any(getattr(r, "production_units_ready", None) for r in restaurants)
        if has_units and segment_demand > 0:
            # Tri des restaurants par score décroissant
            ranked = [r for r in restaurants if scores.get(r.id, Decimal("0")) > 0]
            ranked.sort(key=lambda r: scores.get(r.id, Decimal("0")), reverse=True)
            # États locaux
            served = {r.id: 0 for r in restaurants}
            cap_rem = {r.id: (r.capacity_current if r.staffing_level > 0 else 0) for r in restaurants}
            units_map = {
                r.id: dict(getattr(r, "production_units_ready", {}) or {}) for r in restaurants
            }
            recipe_sales_local: Dict[str, Dict[str, int]] = {r.id: {} for r in restaurants}
            # Service client par client (simple)
            for _ in range(int(segment_demand)):
                served_this = False
                for r in ranked:
                    if cap_rem[r.id] <= 0:
                        continue
                    # Choisir une recette servable (heuristique: la moins chère dispo)
                    active_menu = r.get_active_menu()
                    if not active_menu:
                        continue
                    # recettes triées par prix croissant (budget-friendly par défaut)
                    recipes_sorted = sorted(active_menu.items(), key=lambda kv: kv[1])
                    umap = units_map.get(r.id, {})
                    chosen = None
                    for recipe_id, _price in recipes_sorted:
                        if umap.get(recipe_id, 0) > 0:
                            chosen = recipe_id
                            break
                    if chosen is None:
                        continue
                    # Servir
                    umap[chosen] = umap.get(chosen, 0) - 1
                    served[r.id] += 1
                    cap_rem[r.id] -= 1
                    # trace par recette
                    sales_map = recipe_sales_local[r.id]
                    sales_map[chosen] = sales_map.get(chosen, 0) + 1
                    served_this = True
                    break
                # Si aucun restaurant ne peut servir ce client: abandonné (on ignore pour allocation)
                if not served_this:
                    continue
            # Convertir en résultats
            output = {}
            for rid, qty in served.items():
                output[rid] = {"demand": qty, "recipe_sales": recipe_sales_local.get(rid, {})}
            return output

        # Fallback: répartition proportionnelle classique
        total_score = sum(scores.values())
        if total_score == 0:
            return {r.id: {"demand": 0} for r in restaurants}
        allocation = {}
        for restaurant in restaurants:
            sc = scores.get(restaurant.id, Decimal("0"))
            allocated = int(segment_demand * sc / total_score) if sc > 0 else 0
            allocation[restaurant.id] = {"demand": allocated}
        return allocation

    def _calculate_attraction_score(
        self, restaurant: Restaurant, segment: MarketSegment
    ) -> Decimal:
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

        # Facteur qualité longue (ingrédients) + qualité de production du tour
        quality_factor = self._calculate_quality_factor(restaurant, segment)
        prod_factor = self._calculate_production_quality_factor(restaurant)

        # Score final
        score = type_affinity * price_factor * quality_factor * prod_factor


        # Exposer les facteurs pour affichage
        self._last_factors_by_restaurant[restaurant.id] = {
            "type_affinity": type_affinity,
            "price_factor": price_factor,
            "quality_factor": quality_factor,
            "production_quality_factor": prod_factor,
        }

        # Bonus/malus selon le niveau de staffing
        staffing_bonus = {
            0: Decimal("0"),  # Fermé
            1: Decimal("0.8"),  # Léger
            2: Decimal("1.0"),  # Normal
            3: Decimal("1.2"),  # Renforcé
        }

        score *= staffing_bonus.get(restaurant.staffing_level, Decimal("1.0"))

        return max(Decimal("0"), score)

    def _calculate_price_factor(
        self, average_ticket: Decimal, segment: MarketSegment
    ) -> Decimal:
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

    def _calculate_quality_factor(
        self, restaurant: Restaurant, segment: MarketSegment
    ) -> Decimal:
        """
        Calcule le facteur qualité perçue avec le nouveau système qualité.

        Args:

            restaurant: Restaurant évalué
            segment: MarketSegment

        Returns:
            Facteur qualité (0.5 à 2.0)
        """

        # Score de qualité “longue” (ingrédients/positionnement)
        quality_score = restaurant.get_overall_quality_score()

        # Conversion du score qualité (1-5) en facteur d'attractivité
        if quality_score <= Decimal("1.5"):
            base_factor = Decimal("0.70")  # -30%
        elif quality_score <= Decimal("2.5"):
            base_factor = Decimal("1.00")  # Neutre
        elif quality_score <= Decimal("3.5"):
            base_factor = Decimal("1.20")  # +20%
        elif quality_score <= Decimal("4.5"):
            base_factor = Decimal("1.40")  # +40%
        else:
            base_factor = Decimal("1.60")  # +60%

        # NOUVEAU: Sensibilité à la qualité par segment
        segment_name = segment.name.lower()
        quality_sensitivity = Decimal("1.0")

        if "student" in segment_name or "étudiant" in segment_name:
            quality_sensitivity = Decimal("0.6")  # Moins sensibles
        elif "foodie" in segment_name or "gourmet" in segment_name:
            quality_sensitivity = Decimal("1.4")  # Très sensibles
        elif "family" in segment_name or "famille" in segment_name:
            quality_sensitivity = Decimal("1.0")  # Sensibilité normale

        # Ajustement selon la sensibilité du segment
        if base_factor > Decimal("1.0"):
            bonus = (base_factor - Decimal("1.0")) * quality_sensitivity
            final_factor = Decimal("1.0") + bonus
        else:
            malus = (Decimal("1.0") - base_factor) * quality_sensitivity
            final_factor = Decimal("1.0") - malus
        # NOUVEAU: Impact de la réputation
        reputation_factor = restaurant.reputation / Decimal("10")  # 0-1
        reputation_bonus = (reputation_factor - Decimal("0.5")) * Decimal("0.2")  # ±10%
        final_factor += reputation_bonus
        return max(Decimal("0.5"), min(Decimal("2.0"), final_factor))

    def _calculate_production_quality_factor(self, restaurant: Restaurant) -> Decimal:
        """Calcule un multiplicateur lié à la qualité de production du tour."""
        try:
            qmap = getattr(restaurant, "production_quality_score", {}) or {}
            pmap = getattr(restaurant, "production_produced_units", {}) or {}
            total_qty = sum(int(q) for q in pmap.values())
            if total_qty <= 0 or not qmap:
                return Decimal("1.00")
            weighted = Decimal("0")
            for rid, qty in pmap.items():
                q = Decimal(str(qmap.get(rid, Decimal("1.0"))))
                weighted += q * Decimal(int(qty))
            avg_q = (weighted / Decimal(total_qty)).quantize(Decimal("0.01"))
            span = Decimal("0.2")
            factor = Decimal("1.0") + (avg_q - Decimal("1.0")) * span
            return max(Decimal("0.90"), min(Decimal("1.10"), factor))
        except Exception:
            return Decimal("1.00")

    def _get_season_name(self, month: int) -> str:
        """Retourne le nom de la saison selon le mois."""
        if month in [12, 1, 2]:
            return "hiver"
        elif month in [3, 4, 5]:
            return "printemps"
        elif month in [6, 7, 8]:
            return "été"
        else:
            return "automne"

    def _get_seasonal_demand_bonus(self, segment_name: str, month: int) -> Decimal:
        """
        Calcule le bonus de demande saisonnier pour un segment.

        Args:
            segment_name: Nom du segment
            month: Mois de l'année (1-12)

        Returns:
            Multiplicateur saisonnier (0.8 à 1.3)
        """
        # Bonus saisonniers par segment et mois
        seasonal_bonuses = {
            "étudiants": {
                1: 0.9,
                2: 0.9,
                3: 1.0,
                4: 1.0,
                5: 1.0,
                6: 1.1,
                7: 1.2,
                8: 1.2,
                9: 1.0,
                10: 1.0,
                11: 0.9,
                12: 0.9,
            },
            "familles": {
                1: 1.0,
                2: 1.0,
                3: 1.0,
                4: 1.1,
                5: 1.1,
                6: 1.2,
                7: 1.3,
                8: 1.3,
                9: 1.0,
                10: 1.0,
                11: 1.0,
                12: 1.1,
            },
            "foodies": {
                1: 1.0,
                2: 1.0,
                3: 1.1,
                4: 1.2,
                5: 1.2,
                6: 1.1,
                7: 1.0,
                8: 1.0,
                9: 1.1,
                10: 1.2,
                11: 1.1,
                12: 1.2,
            },
        }

        # Recherche par nom de segment (insensible à la casse)
        segment_lower = segment_name.lower()
        for key, bonuses in seasonal_bonuses.items():
            if key in segment_lower:
                return Decimal(str(bonuses.get(month, 1.0)))

        # Par défaut, pas de bonus saisonnier
        return Decimal("1.0")

    def _apply_capacity_constraints(
        self, restaurants: List[Restaurant], results: Dict[str, AllocationResult]
    ) -> Dict[str, AllocationResult]:
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

    def _calculate_revenue(
        self, restaurant: Restaurant, result: AllocationResult
    ) -> AllocationResult:
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

        active_menu = restaurant.get_active_menu()
        if not active_menu:
            return result

        # Utiliser les ventes par recette si disponibles
        total_revenue = Decimal("0")
        if result.recipe_sales:
            for rid, sold in result.recipe_sales.items():
                price = active_menu.get(rid)
                if price:
                    total_revenue += price * Decimal(int(sold))
        else:
            # fallback équitable
            customers_served = result.served_customers
            recipes_count = len(active_menu)
            if recipes_count > 0:
                customers_per_recipe = customers_served // recipes_count
                remaining_customers = customers_served % recipes_count
                for i, (recipe_id, price) in enumerate(active_menu.items()):
                    recipe_customers = customers_per_recipe + (1 if i < remaining_customers else 0)
                    total_revenue += price * recipe_customers

        result.revenue = total_revenue

        # NOUVEAU: Calcul et mise à jour de la satisfaction client
        if result.served_customers > 0:
            # Satisfaction basée sur le rapport qualité/prix
            quality_score = restaurant.get_overall_quality_score()
            average_ticket = result.revenue / Decimal(result.served_customers)

            # Ratio prix/qualité (prix par étoile de qualité)
            price_quality_ratio = (
                average_ticket / quality_score if quality_score > 0 else average_ticket
            )

            # Calcul de la satisfaction (0-5)
            if price_quality_ratio <= Decimal("2.5"):  # Excellent rapport
                satisfaction = Decimal("5.0")
            elif price_quality_ratio <= Decimal("3.5"):  # Bon rapport
                satisfaction = Decimal("4.0")
            elif price_quality_ratio <= Decimal("4.5"):  # Correct
                satisfaction = Decimal("3.0")
            elif price_quality_ratio <= Decimal("6.0"):  # Cher
                satisfaction = Decimal("2.0")
            else:  # Très cher
                satisfaction = Decimal("1.0")

            # Mise à jour de la satisfaction et réputation du restaurant
            restaurant.update_customer_satisfaction(satisfaction)

        # Recalculer les métriques dérivées
        if result.capacity > 0:
            result.utilization_rate = Decimal(result.served_customers) / Decimal(
                result.capacity
            )
        result.lost_customers = max(
            0, result.allocated_demand - result.served_customers
        )
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

        restaurant_customers = turn_data.get(
            restaurant_id, AllocationResult(restaurant_id)
        ).served_customers
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
            "total_demand": total_demand,
            "total_served": total_served,
            "total_capacity": total_capacity,
            "total_revenue": float(total_revenue),
            "market_utilization": float(Decimal(total_served) / Decimal(total_capacity))
            if total_capacity > 0
            else 0,
            "demand_satisfaction": float(Decimal(total_served) / Decimal(total_demand))
            if total_demand > 0
            else 0,
            "average_ticket": float(total_revenue / Decimal(total_served))
            if total_served > 0
            else 0,
        }
