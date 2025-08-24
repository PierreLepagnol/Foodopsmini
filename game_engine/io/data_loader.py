"""
Chargeur de données pour FoodOps Pro.
"""

import csv
import json
from decimal import Decimal
from pathlib import Path

import yaml  # Chargement YAML

from game_engine.domain.ingredient import Ingredient
from game_engine.domain.scenario import Scenario
from game_engine.domain.supplier import Supplier
from game_engine.io.models import (
    HRSocialCharges,
    HRTables,
    IngredientGamme,
    IngredientGammesDict,
    IngredientsDict,
    LoadAllDataResponse,
    SupplierPriceEntry,
    SupplierPricesDict,
    SuppliersCatalogDict,
    SuppliersCatalogEntry,
    SuppliersDict,
)


class DataLoader:
    """
    Chargeur de données depuis les fichiers CSV, JSON et YAML.
    """

    def __init__(self, data_path: Path | None = None) -> None:
        """
        Initialise le chargeur de données.

        Args:
            data_path: Chemin vers le dossier de données
        """
        if data_path is None:
            # Chemin par défaut relatif au module
            self.data_path = Path(__file__).parent.parent / "data"
        else:
            self.data_path = data_path

    def load_ingredients(self) -> IngredientsDict:
        """
        Charge les ingrédients depuis le fichier CSV.

        Returns:
            Dictionnaire des ingrédients par ID
        """
        ingredients = {}
        csv_path = self.data_path / "ingredients.csv"

        with open(csv_path, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ingredient = Ingredient(
                    id=row["id"],
                    name=row["name"],
                    unit=row["unit"],
                    cost_ht=Decimal(row["cost_ht"]),
                    vat_rate=Decimal(row["vat_rate"]),
                    shelf_life_days=int(row["shelf_life_days"]),
                    category=row["category"],
                    density=Decimal(row["density"]) if row["density"] else None,
                )
                ingredients[ingredient.id] = ingredient

        return ingredients

    def load_suppliers(self) -> SuppliersDict:
        """
        Charge les fournisseurs depuis le fichier CSV.

        Returns:
            Dictionnaire des fournisseurs par ID
        """
        suppliers = {}
        csv_path = self.data_path / "suppliers.csv"

        with open(csv_path, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                supplier = Supplier(
                    id=row["id"],
                    name=row["name"],
                    reliability=Decimal(row["reliability"]),
                    lead_time_days=int(row["lead_time_days"]),
                    min_order_value=Decimal(row["min_order_value"]),
                    shipping_cost=Decimal(row["shipping_cost"]),
                    payment_terms_days=int(row["payment_terms_days"]),
                    discount_threshold=Decimal(row["discount_threshold"])
                    if row["discount_threshold"]
                    else None,
                    discount_rate=Decimal(row["discount_rate"])
                    if row["discount_rate"]
                    else None,
                )
                suppliers[supplier.id] = supplier
        return suppliers

    def load_supplier_prices(self) -> SupplierPricesDict:
        """Charge la mercuriale (prix fournisseurs par ingrédient)."""
        prices_csv = self.data_path / "supplier_prices.csv"
        catalog: dict[str, list[SupplierPriceEntry]] = {}
        if not prices_csv.exists():
            return catalog
        with open(prices_csv, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ing = row["ingredient_id"]
                entry = SupplierPriceEntry(
                    supplier_id=row["supplier_id"],
                    quality_level=int(row["quality_level"])
                    if row.get("quality_level")
                    else None,
                    pack_size=Decimal(row["pack_size"]),
                    pack_unit=row.get("pack_unit") or None,
                    unit_price_ht=Decimal(row["unit_price_ht"]),
                    vat_rate=Decimal(row["vat_rate"]),
                    moq_qty=Decimal(row["moq_qty"])
                    if row.get("moq_qty")
                    else Decimal("0"),
                    moq_value=Decimal(row["moq_value"])
                    if row.get("moq_value")
                    else Decimal("0"),
                    lead_time_days=int(row["lead_time_days"])
                    if row.get("lead_time_days")
                    else None,
                    reliability=Decimal(row["reliability"])
                    if row.get("reliability")
                    else None,
                    available=int(row["available"]) if row.get("available") else 1,
                )
                catalog.setdefault(ing, []).append(entry)

        return catalog

    def load_ingredient_gammes(self) -> IngredientGammesDict:
        """Charge les gammes par ingrédient (optionnel)."""
        gammes_csv = self.data_path / "ingredients_gammes.csv"
        gammes: dict[str, list[IngredientGamme]] = {}
        if not gammes_csv.exists():
            return gammes
        with open(gammes_csv, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ing = row["ingredient_id"]
                entry = IngredientGamme(
                    quality_level=int(row["quality_level"]),
                    price_multiplier=Decimal(row["price_multiplier"]),
                    shelf_life_factor=Decimal(row["shelf_life_factor"]),
                    quality_score=Decimal(row["quality_score"]),
                )
                gammes.setdefault(ing, []).append(entry)
        return gammes

    def load_hr_tables(self) -> HRTables:
        """
        Charge les tables RH depuis le fichier JSON.

        Returns:
            Configuration RH complète
        """
        json_path = self.data_path / "hr_tables.json"
        with open(json_path, encoding="utf-8") as file:
            hr_data = json.load(file)

        # Conversion des valeurs numériques en Decimal
        social_charges_data = hr_data.get("social_charges", {})
        for contract_type, rates in social_charges_data.items():
            for rate_type, value in rates.items():
                if isinstance(value, int | float):
                    social_charges_data[contract_type][rate_type] = Decimal(str(value))

        # Création du modèle Pydantic
        social_charges = HRSocialCharges(
            cdi=Decimal(str(social_charges_data.get("cdi", 0.42))),
            cdd=Decimal(str(social_charges_data.get("cdd", 0.44))),
            extra=Decimal(str(social_charges_data.get("extra", 0.45))),
            apprenti=Decimal(str(social_charges_data.get("apprenti", 0.11))),
            stage=Decimal(str(social_charges_data.get("stage", 0.00))),
        )

        return HRTables(social_charges=social_charges)

    def build_suppliers_catalog(
        self, suppliers: SuppliersDict, prices: SupplierPricesDict
    ) -> SuppliersCatalogDict:
        """Construit un catalogue enrichi avec lead_time et fiabilité."""
        catalog: dict[str, list[SuppliersCatalogEntry]] = {}
        for ing_id, entries in prices.items():
            for e in entries:
                sup = suppliers.get(e.supplier_id)
                if sup:
                    catalog_entry = SuppliersCatalogEntry(
                        supplier_id=e.supplier_id,
                        quality_level=e.quality_level,
                        pack_size=e.pack_size,
                        pack_unit=e.pack_unit,
                        unit_price_ht=e.unit_price_ht,
                        vat_rate=e.vat_rate,
                        moq_qty=e.moq_qty,
                        moq_value=e.moq_value,
                        lead_time_days=sup.lead_time_days,
                        reliability=sup.reliability,
                        available=e.available,
                    )
                    catalog.setdefault(ing_id, []).append(catalog_entry)
        return catalog

    def load_scenario(self, scenario_path: Path) -> Scenario:
        """
        Charge un scénario depuis un fichier JSON ou YAML.

        Cette méthode parse les fichiers de configuration de scénario et convertit
        les données en objets domaine typés. Elle gère automatiquement la conversion
        des types de données (string vers Decimal, enum, etc.) et valide la cohérence
        des données.

        Args:
            scenario_path: Chemin vers le fichier de scénario (.json ou .yaml)

        Returns:
            Scénario chargé et validé

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si les données du scénario sont invalides
            yaml.YAMLError: Si le fichier YAML est malformé

        Examples:
            >>> loader = DataLoader()
            >>> # Chargement d'un scénario YAML (comme base.yaml)
            >>> scenario = loader.load_scenario(Path("examples/scenarios/base.yaml"))
            >>> print(f"Scénario: {scenario.name}")
            Scénario: Scénario de Base
            >>> print(f"Segments: {len(scenario.segments)}")
            Segments: 3
            >>> print(f"Tours: {scenario.turns}")
            Tours: 12

        Note:
            Le format YAML est recommandé pour sa lisibilité. Si PyYAML n'est pas
            disponible, la méthode utilise automatiquement un scénario de fallback.
        """
        # Détection du format et chargement des données brutes
        with open(scenario_path, encoding="utf-8") as file:
            data = yaml.safe_load(file)
            scenario = Scenario(**data)
        return scenario
        # # Conversion et validation des segments de marché
        # segments: list[MarketSegment] = []
        # for segment_data in data["segments"]:
        #     # Conversion des affinités par type de restaurant
        #     # Exemple: {"fast": 1.2, "classic": 0.7} -> {RestaurantType.FAST: Decimal("1.2")}
        #     type_affinity = {}
        #     for type_name, affinity in segment_data["type_affinity"].items():
        #         restaurant_type = RestaurantType(type_name)
        #         type_affinity[restaurant_type] = Decimal(str(affinity))

        #     # Conversion de la saisonnalité (mois -> facteur)
        #     # Exemple base.yaml: {1: 0.8, 2: 1.1, ...} pour les étudiants en janvier/février
        #     seasonality = {}
        #     if "seasonality" in segment_data:
        #         for month, factor in segment_data["seasonality"].items():
        #             seasonality[int(month)] = Decimal(str(factor))

        #     # Création du segment avec conversion des types numériques
        #     segment = MarketSegment(
        #         name=segment_data["name"],
        #         share=Decimal(
        #             str(segment_data["share"])
        #         ),  # Ex: 0.35 pour 35% du marché
        #         budget=Decimal(str(segment_data["budget"])),  # Ex: 11.0€ pour étudiants
        #         type_affinity=type_affinity,
        #         price_sensitivity=Decimal(
        #             str(segment_data.get("price_sensitivity", 1.0))
        #         ),  # Ex: 1.4 = sensible au prix
        #         quality_sensitivity=Decimal(
        #             str(segment_data.get("quality_sensitivity", 1.0))
        #         ),  # Ex: 0.8 = peu sensible à la qualité
        #         seasonality=seasonality,
        #     )
        #     segments.append(segment)

        # # Conversion des taux de TVA par catégorie
        # # Exemple base.yaml: food_onsite: 0.10 (10%), food_takeaway: 0.055 (5.5%)
        # vat_rates = {}
        # for category, rate in data.get("vat_rates", {}).items():
        #     vat_rates[category] = Decimal(str(rate))

        # # Conversion des charges sociales par type de contrat
        # # Exemple base.yaml: cdi: 0.42 (42%), apprenti: 0.11 (11%)
        # social_charges = {}
        # for contract_type, rate in data.get("social_charges", {}).items():
        #     social_charges[contract_type] = Decimal(str(rate))

        # # Construction de l'objet Scenario avec validation automatique
        # scenario = Scenario(
        #     name=data["name"],  # Ex: "Scénario de Base"
        #     description=data["description"],  # Description détaillée
        #     turns=data["turns"],  # Ex: 12 tours de jeu
        #     base_demand=data["base_demand"],  # Ex: 420 clients de base
        #     demand_noise=Decimal(
        #         str(data["demand_noise"])
        #     ),  # Ex: 0.08 = 8% de variabilité
        #     segments=segments,  # Segments convertis ci-dessus
        #     vat_rates=vat_rates,
        #     social_charges=social_charges,
        #     interest_rate=Decimal(str(data.get("interest_rate", 0.05))),  # Ex: 4.5%
        #     ai_competitors=data.get("ai_competitors", 2),  # Nombre de concurrents IA
        #     random_seed=data.get("random_seed"),  # Pour reproductibilité (ex: 42)
        # )

        # return scenario

    def _get_default_scenario_config(self) -> dict:
        """Retourne la configuration par défaut du scénario."""
        return {
            "name": "Scénario Standard",
            "description": "Configuration équilibrée pour apprentissage général",
            "difficulty": "normal",
            "market": {
                "base_demand": 420,
                "demand_noise": 0.15,
                "price_sensitivity": 1.2,
                "quality_importance": 1.0,
            },
            "segments": {
                "étudiants": {
                    "size": 150,
                    "budget": 11.0,
                    "price_sensitivity": 1.8,
                    "quality_sensitivity": 0.7,
                    "description": "Étudiants avec budget limité",
                },
                "familles": {
                    "size": 180,
                    "budget": 17.0,
                    "price_sensitivity": 1.2,
                    "quality_sensitivity": 1.1,
                    "description": "Familles recherchant bon rapport qualité/prix",
                },
                "foodies": {
                    "size": 90,
                    "budget": 25.0,
                    "price_sensitivity": 0.6,
                    "quality_sensitivity": 1.8,
                    "description": "Amateurs de gastronomie privilégiant la qualité",
                },
            },
            "restaurant": {
                "initial_budget": 10000,
                "base_capacity": 150,
                "base_staff_cost": 2800,
                "base_overhead": 1200,
            },
            "competitors": [
                {
                    "name": "Resto Rapide",
                    "strategy": "prix_bas",
                    "base_price": 9.50,
                    "quality_level": 1,
                },
                {
                    "name": "Bistrot Central",
                    "strategy": "equilibre",
                    "base_price": 13.20,
                    "quality_level": 3,
                },
                {
                    "name": "Table Gourmande",
                    "strategy": "premium",
                    "base_price": 18.80,
                    "quality_level": 4,
                },
            ],
            "game": {
                "max_turns": 10,
                "starting_month": 1,
                "enable_seasonality": True,
                "enable_events": True,
                "enable_marketing": True,
                "enable_advanced_finance": True,
            },
            "objectives": {
                "primary": "Réaliser un profit total de 5000€",
                "secondary": [
                    "Maintenir une satisfaction client > 3.5",
                    "Atteindre 25% de part de marché",
                    "Survivre aux 10 tours",
                ],
            },
        }

    def get_default_scenario_path(self) -> Path:
        """
        Retourne le chemin vers le scénario par défaut.

        Returns:
            Chemin vers base.yaml
        """
        return (
            Path(__file__).parent.parent.parent.parent
            / "examples"
            / "scenarios"
            / "base.yaml"
        )

    def load_all_data(self, scenario_path: Path | None = None) -> LoadAllDataResponse:
        """
        Charge toutes les données nécessaires au jeu.

        Args:
            scenario_path: Chemin vers le scénario (optionnel)

        Returns:
            Données complètes du jeu dans un modèle Pydantic
        """
        if scenario_path is None:
            scenario_path = self.get_default_scenario_path()

        suppliers = self.load_suppliers()
        supplier_prices = self.load_supplier_prices()
        suppliers_catalog = self.build_suppliers_catalog(suppliers, supplier_prices)

        return LoadAllDataResponse(
            ingredients=self.load_ingredients(),
            recipes=self.load_recipes(),
            suppliers=suppliers,
            suppliers_catalog=suppliers_catalog,
            ingredient_gammes=self.load_ingredient_gammes(),
            hr_tables=self.load_hr_tables(),
            scenario=self.load_scenario(scenario_path),
        )
