"""
Système de fonds de commerce pour FoodOps Pro.
"""

from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
from enum import Enum

from foodops_pro.restaurant import RestaurantType


class LocationType(Enum):
    """Types d'emplacements."""

    CENTRE_VILLE = "centre_ville"
    BANLIEUE = "banlieue"
    ZONE_COMMERCIALE = "zone_commerciale"
    QUARTIER_ETUDIANT = "quartier_etudiant"
    ZONE_INDUSTRIELLE = "zone_industrielle"


class CommerceCondition(Enum):
    """État du fonds de commerce."""

    EXCELLENT = "excellent"
    BON = "bon"
    CORRECT = "correct"
    RENOVATION_LEGERE = "renovation_legere"
    RENOVATION_LOURDE = "renovation_lourde"


@dataclass
class CommerceLocation:
    """
    Fonds de commerce disponible à l'achat.

    Attributes:
        id: Identifiant unique
        name: Nom du commerce
        location_type: Type d'emplacement
        restaurant_type: Type de restaurant recommandé
        price: Prix d'achat du fonds
        size: Nombre de couverts
        condition: État du local
        equipment_included: Équipements inclus
        rent_monthly: Loyer mensuel
        lease_years: Durée du bail restante
        foot_traffic: Niveau de passage
        competition_nearby: Nombre de concurrents proches
        description: Description détaillée
        advantages: Avantages spécifiques
        disadvantages: Inconvénients
        renovation_cost: Coût de rénovation si nécessaire
        special_features: Caractéristiques spéciales
    """

    id: str
    name: str
    location_type: LocationType
    restaurant_type: RestaurantType
    price: Decimal
    size: int  # couverts
    condition: CommerceCondition
    equipment_included: List[str]
    rent_monthly: Decimal
    lease_years: int
    foot_traffic: str  # "low", "medium", "high", "very_high"
    competition_nearby: int
    description: str
    advantages: List[str]
    disadvantages: List[str]
    renovation_cost: Decimal = Decimal("0")
    special_features: List[str] = None

    def __post_init__(self):
        if self.special_features is None:
            self.special_features = []

    @property
    def total_initial_cost(self) -> Decimal:
        """Coût total initial (achat + rénovation)."""
        return self.price + self.renovation_cost

    @property
    def foot_traffic_multiplier(self) -> Decimal:
        """Multiplicateur de clientèle selon le passage."""
        multipliers = {
            "low": Decimal("0.7"),
            "medium": Decimal("1.0"),
            "high": Decimal("1.3"),
            "very_high": Decimal("1.6"),
        }
        return multipliers.get(self.foot_traffic, Decimal("1.0"))

    @property
    def competition_pressure(self) -> Decimal:
        """Pression concurrentielle (0.0 = aucune, 1.0 = très forte)."""
        if self.competition_nearby == 0:
            return Decimal("0.0")
        elif self.competition_nearby <= 2:
            return Decimal("0.3")
        elif self.competition_nearby <= 4:
            return Decimal("0.6")
        else:
            return Decimal("0.9")


class CommerceManager:
    """Gestionnaire des fonds de commerce."""

    def __init__(self):
        self.available_locations = self._create_default_locations()

    def _create_default_locations(self) -> List[CommerceLocation]:
        """Crée la liste des fonds de commerce par défaut."""
        return [
            # Centre-ville premium
            CommerceLocation(
                id="bistrot_centre_premium",
                name="Le Bistrot du Centre",
                location_type=LocationType.CENTRE_VILLE,
                restaurant_type=RestaurantType.BRASSERIE,
                price=Decimal("95000"),
                size=70,
                condition=CommerceCondition.BON,
                equipment_included=[
                    "Cuisine professionnelle complète",
                    "Salle climatisée",
                    "Terrasse 20 places",
                    "Cave à vin",
                    "Système de caisse moderne",
                ],
                rent_monthly=Decimal("5200"),
                lease_years=9,
                foot_traffic="very_high",
                competition_nearby=3,
                description="Emplacement exceptionnel en plein cœur de ville avec terrasse. Clientèle d'affaires et touristes.",
                advantages=[
                    "Visibilité maximale",
                    "Clientèle aisée",
                    "Terrasse très prisée",
                    "Parking public proche",
                ],
                disadvantages=[
                    "Loyer élevé",
                    "Concurrence forte",
                    "Bruit de circulation",
                    "Livraisons compliquées",
                ],
                special_features=["Licence IV", "Terrasse chauffée"],
            ),
            # Fast-food étudiant
            CommerceLocation(
                id="fast_food_campus",
                name="Quick Campus",
                location_type=LocationType.QUARTIER_ETUDIANT,
                restaurant_type=RestaurantType.FAST,
                price=Decimal("42000"),
                size=45,
                condition=CommerceCondition.CORRECT,
                equipment_included=[
                    "Cuisine fast-food équipée",
                    "Comptoir de service",
                    "Mobilier moderne",
                    "Système de commande digitale",
                ],
                rent_monthly=Decimal("2800"),
                lease_years=6,
                foot_traffic="high",
                competition_nearby=2,
                description="Local moderne près du campus universitaire. Flux constant d'étudiants.",
                advantages=[
                    "Clientèle captive étudiante",
                    "Horaires étendus possibles",
                    "Loyer raisonnable",
                    "Croissance démographique",
                ],
                disadvantages=[
                    "Budget limité des clients",
                    "Saisonnalité forte",
                    "Concurrence sandwich/kebab",
                    "Vacances scolaires creuses",
                ],
                renovation_cost=Decimal("8000"),
                special_features=["Wifi gratuit", "Prises électriques"],
            ),
            # Restaurant familial banlieue
            CommerceLocation(
                id="restaurant_familial_banlieue",
                name="La Table Familiale",
                location_type=LocationType.BANLIEUE,
                restaurant_type=RestaurantType.CLASSIC,
                price=Decimal("58000"),
                size=55,
                condition=CommerceCondition.BON,
                equipment_included=[
                    "Cuisine traditionnelle",
                    "Salle familiale",
                    "Parking privé 15 places",
                    "Jeux pour enfants",
                ],
                rent_monthly=Decimal("3200"),
                lease_years=12,
                foot_traffic="medium",
                competition_nearby=1,
                description="Restaurant familial dans quartier résidentiel calme. Clientèle locale fidèle.",
                advantages=[
                    "Clientèle fidèle",
                    "Parking gratuit",
                    "Bail long",
                    "Peu de concurrence",
                ],
                disadvantages=[
                    "Passage limité",
                    "Dépendance aux habitants",
                    "Difficile à faire connaître",
                    "Croissance limitée",
                ],
                special_features=["Aire de jeux", "Parking privé"],
            ),
            # Gastronomique centre historique
            CommerceLocation(
                id="gastro_historique",
                name="L'Auberge du Vieux Port",
                location_type=LocationType.CENTRE_VILLE,
                restaurant_type=RestaurantType.GASTRONOMIQUE,
                price=Decimal("125000"),
                size=35,
                condition=CommerceCondition.EXCELLENT,
                equipment_included=[
                    "Cuisine gastronomique haut de gamme",
                    "Cave voûtée 200 bouteilles",
                    "Salle de caractère",
                    "Mobilier d'époque",
                    "Système son/éclairage",
                ],
                rent_monthly=Decimal("4800"),
                lease_years=15,
                foot_traffic="medium",
                competition_nearby=2,
                description="Restaurant de caractère dans bâtiment historique. Réputation établie.",
                advantages=[
                    "Cachet exceptionnel",
                    "Réputation établie",
                    "Clientèle haut de gamme",
                    "Bail très long",
                ],
                disadvantages=[
                    "Investissement important",
                    "Contraintes patrimoniales",
                    "Clientèle exigeante",
                    "Charges élevées",
                ],
                special_features=["Monument historique", "Cave d'exception"],
            ),
            # Zone commerciale accessible
            CommerceLocation(
                id="brasserie_zone_commerciale",
                name="Brasserie du Centre Commercial",
                location_type=LocationType.ZONE_COMMERCIALE,
                restaurant_type=RestaurantType.BRASSERIE,
                price=Decimal("35000"),
                size=80,
                condition=CommerceCondition.RENOVATION_LEGERE,
                equipment_included=[
                    "Cuisine standard",
                    "Grande salle",
                    "Terrasse couverte",
                ],
                rent_monthly=Decimal("3800"),
                lease_years=8,
                foot_traffic="high",
                competition_nearby=4,
                description="Grande brasserie dans centre commercial. Flux important mais concurrence forte.",
                advantages=[
                    "Gros volume possible",
                    "Parking gratuit",
                    "Flux de chalandise",
                    "Horaires étendus",
                ],
                disadvantages=[
                    "Concurrence très forte",
                    "Ambiance commerciale",
                    "Charges communes",
                    "Dépendance au centre",
                ],
                renovation_cost=Decimal("15000"),
                special_features=["Accès PMR", "Livraison facile"],
            ),
            # Opportunité à rénover
            CommerceLocation(
                id="opportunite_renovation",
                name="Local à Rénover - Centre",
                location_type=LocationType.CENTRE_VILLE,
                restaurant_type=RestaurantType.CLASSIC,
                price=Decimal("28000"),
                size=40,
                condition=CommerceCondition.RENOVATION_LOURDE,
                equipment_included=[
                    "Structure de base",
                    "Compteur électrique renforcé",
                ],
                rent_monthly=Decimal("2400"),
                lease_years=10,
                foot_traffic="high",
                competition_nearby=1,
                description="Ancien restaurant à rénover entièrement. Potentiel énorme pour investisseur motivé.",
                advantages=[
                    "Prix d'achat très bas",
                    "Liberté totale d'aménagement",
                    "Bon emplacement",
                    "Loyer modéré",
                ],
                disadvantages=[
                    "Gros travaux nécessaires",
                    "Investissement total élevé",
                    "Délai avant ouverture",
                    "Risques de dépassement",
                ],
                renovation_cost=Decimal("45000"),
                special_features=["Potentiel cave", "Possibilité terrasse"],
            ),
        ]

    def get_available_locations(
        self,
        budget: Decimal,
        location_types: Optional[List[LocationType]] = None,
        restaurant_types: Optional[List[RestaurantType]] = None,
    ) -> List[CommerceLocation]:
        """
        Retourne les emplacements disponibles selon les critères.

        Args:
            budget: Budget disponible
            location_types: Types d'emplacements autorisés
            restaurant_types: Types de restaurants autorisés

        Returns:
            Liste des emplacements accessibles
        """
        filtered_locations = []

        for location in self.available_locations:
            # Vérification du budget
            if location.total_initial_cost > budget:
                continue

            # Vérification du type d'emplacement
            if location_types and location.location_type not in location_types:
                continue

            # Vérification du type de restaurant
            if restaurant_types and location.restaurant_type not in restaurant_types:
                continue

            filtered_locations.append(location)

        return filtered_locations

    def get_location_by_id(self, location_id: str) -> Optional[CommerceLocation]:
        """Retourne un emplacement par son ID."""
        for location in self.available_locations:
            if location.id == location_id:
                return location
        return None
