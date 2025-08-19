"""
Chargeur de données pour FoodOps Pro.
"""

import csv
import json
import yaml  # Chargement YAML
from pathlib import Path
from typing import Dict, List, Optional
from decimal import Decimal

from ..domain.ingredient import Ingredient
from ..domain.recipe import Recipe, RecipeItem
from ..domain.supplier import Supplier
from ..domain.restaurant import RestaurantType
from ..domain.scenario import Scenario, MarketSegment


class DataLoader:
    """
    Chargeur de données depuis les fichiers CSV, JSON et YAML.
    """

    def __init__(self, data_path: Optional[Path] = None) -> None:
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

    def load_ingredients(self) -> Dict[str, Ingredient]:
        """
        Charge les ingrédients depuis le fichier CSV.

        Returns:
            Dictionnaire des ingrédients par ID
        """
        ingredients = {}
        csv_path = self.data_path / "ingredients.csv"

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ingredient = Ingredient(
                    id=row['id'],
                    name=row['name'],
                    unit=row['unit'],
                    cost_ht=Decimal(row['cost_ht']),
                    vat_rate=Decimal(row['vat_rate']),
                    shelf_life_days=int(row['shelf_life_days']),
                    category=row['category'],
                    density=Decimal(row['density']) if row['density'] else None
                )
                ingredients[ingredient.id] = ingredient

        return ingredients

    def load_recipes(self) -> Dict[str, Recipe]:
        """
        Charge les recettes depuis les fichiers CSV.

        Returns:
            Dictionnaire des recettes par ID
        """
        # Chargement des recettes de base (métadonnées seulement)
        recipe_metadata = {}
        recipes_csv = self.data_path / "recipes.csv"

        with open(recipes_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipe_metadata[row['id']] = {
                    'id': row['id'],
                    'name': row['name'],
                    'temps_prepa_min': int(row['temps_prepa_min']),
                    'temps_service_min': int(row['temps_service_min']),
                    'portions': int(row['portions']),
                    'category': row['category'],
                    'difficulty': int(row['difficulty']),
                    'description': row['description']
                }

        # Chargement des ingrédients des recettes
        items_csv = self.data_path / "recipe_items.csv"
        recipe_items = {}

        with open(items_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipe_id = row['recipe_id']
                if recipe_id not in recipe_items:
                    recipe_items[recipe_id] = []

                item = RecipeItem(
                    ingredient_id=row['ingredient_id'],
                    qty_brute=Decimal(row['qty_brute']),
                    rendement_prepa=Decimal(row['rendement_prepa']),
                    rendement_cuisson=Decimal(row['rendement_cuisson'])
                )
                recipe_items[recipe_id].append(item)

        # Création des recettes finales avec ingrédients
        recipes = {}
        for recipe_id, metadata in recipe_metadata.items():
            items = recipe_items.get(recipe_id, [])
            if items:  # Seulement si la recette a des ingrédients
                recipe = Recipe(
                    id=metadata['id'],
                    name=metadata['name'],
                    items=items,
                    temps_prepa_min=metadata['temps_prepa_min'],
                    temps_service_min=metadata['temps_service_min'],
                    portions=metadata['portions'],
                    category=metadata['category'],
                    difficulty=metadata['difficulty'],
                    description=metadata['description']
                )
                recipes[recipe_id] = recipe

        return recipes

    def load_suppliers(self) -> Dict[str, Supplier]:
        """
        Charge les fournisseurs depuis le fichier CSV.

        Returns:
            Dictionnaire des fournisseurs par ID
        """
        suppliers = {}
        csv_path = self.data_path / "suppliers.csv"

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                supplier = Supplier(
                    id=row['id'],
                    name=row['name'],
                    reliability=Decimal(row['reliability']),
                    lead_time_days=int(row['lead_time_days']),
                    min_order_value=Decimal(row['min_order_value']),
                    shipping_cost=Decimal(row['shipping_cost']),
                    payment_terms_days=int(row['payment_terms_days']),
                    discount_threshold=Decimal(row['discount_threshold']) if row['discount_threshold'] else None,
                    discount_rate=Decimal(row['discount_rate']) if row['discount_rate'] else None
                )
                suppliers[supplier.id] = supplier
        return suppliers

    def load_supplier_prices(self) -> Dict[str, List[Dict]]:
        """Charge la mercuriale (prix fournisseurs par ingrédient)."""
        prices_csv = self.data_path / "supplier_prices.csv"
        catalog: Dict[str, List[Dict]] = {}
        if not prices_csv.exists():
            return catalog
        with open(prices_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ing = row['ingredient_id']
                entry = {
                    'supplier_id': row['supplier_id'],
                    'quality_level': int(row['quality_level']),
                    'pack_size': Decimal(row['pack_size']),
                    'pack_unit': row['pack_unit'],
                    'unit_price_ht': Decimal(row['unit_price_ht']),
                    'vat_rate': Decimal(row['vat_rate']),
                    'moq_qty': Decimal(row['moq_qty']) if row.get('moq_qty') else Decimal('0'),
                    'moq_value': Decimal(row['moq_value']) if row.get('moq_value') else Decimal('0'),
                }
                catalog.setdefault(ing, []).append(entry)

        def build_suppliers_catalog(self, suppliers: Dict[str, Supplier], prices: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
            """Construit un catalogue enrichi avec lead_time et fiabilité."""
            catalog: Dict[str, List[Dict]] = {}
            for ing_id, entries in prices.items():
                for e in entries:
                    sup = suppliers.get(e['supplier_id'])
                    offer = dict(e)
                    if sup:
                        offer['lead_time_days'] = sup.lead_time_days
                        offer['reliability'] = sup.reliability
                    catalog.setdefault(ing_id, []).append(offer)
            return catalog

        return catalog

    def load_ingredient_gammes(self) -> Dict[str, List[Dict]]:
        """Charge les gammes par ingrédient (optionnel)."""
        gammes_csv = self.data_path / "ingredients_gammes.csv"
        gammes: Dict[str, List[Dict]] = {}
        if not gammes_csv.exists():
            return gammes
        with open(gammes_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ing = row['ingredient_id']
                entry = {
                    'quality_level': int(row['quality_level']),
                    'price_multiplier': Decimal(row['price_multiplier']),
                    'shelf_life_factor': Decimal(row['shelf_life_factor']),
                    'quality_score': Decimal(row['quality_score'])
                }
                gammes.setdefault(ing, []).append(entry)
        return gammes
        return suppliers

    def load_hr_tables(self) -> Dict:
        """
        Charge les tables RH depuis le fichier JSON.

        Returns:
            Configuration RH complète
        """
        json_path = self.data_path / "hr_tables.json"

        with open(json_path, 'r', encoding='utf-8') as file:
            hr_data = json.load(file)

        # Conversion des valeurs numériques en Decimal
        for contract_type, rates in hr_data.get('social_charges', {}).items():
            for rate_type, value in rates.items():
                if isinstance(value, (int, float)):
                    hr_data['social_charges'][contract_type][rate_type] = Decimal(str(value))

        return hr_data

    def load_scenario(self, scenario_path: Path) -> Scenario:
        """
        Charge un scénario depuis un fichier JSON.

        Args:
            scenario_path: Chemin vers le fichier de scénario

        Returns:
            Scénario chargé
        """
        # Si c'est un fichier .yaml, on charge via PyYAML
        if str(scenario_path).endswith('.yaml'):
            with open(scenario_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
        else:
            with open(scenario_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

        # Conversion des segments
        segments = []
        for segment_data in data['segments']:
            # Conversion des affinités par type
            type_affinity = {}
            for type_name, affinity in segment_data['type_affinity'].items():
                restaurant_type = RestaurantType(type_name)
                type_affinity[restaurant_type] = Decimal(str(affinity))

            # Conversion de la saisonnalité
            seasonality = {}
            if 'seasonality' in segment_data:
                for month, factor in segment_data['seasonality'].items():
                    seasonality[int(month)] = Decimal(str(factor))

            segment = MarketSegment(
                name=segment_data['name'],
                share=Decimal(str(segment_data['share'])),
                budget=Decimal(str(segment_data['budget'])),
                type_affinity=type_affinity,
                price_sensitivity=Decimal(str(segment_data.get('price_sensitivity', 1.0))),
                quality_sensitivity=Decimal(str(segment_data.get('quality_sensitivity', 1.0))),
                seasonality=seasonality
            )
            segments.append(segment)

        # Conversion des taux de TVA
        vat_rates = {}
        for category, rate in data.get('vat_rates', {}).items():
            vat_rates[category] = Decimal(str(rate))

        # Conversion des charges sociales
        social_charges = {}
        for contract_type, rate in data.get('social_charges', {}).items():
            social_charges[contract_type] = Decimal(str(rate))

        scenario = Scenario(
            name=data['name'],
            description=data['description'],
            turns=data['turns'],
            base_demand=data['base_demand'],
            demand_noise=Decimal(str(data['demand_noise'])),
            segments=segments,
            vat_rates=vat_rates,
            social_charges=social_charges,
            interest_rate=Decimal(str(data.get('interest_rate', 0.05))),
            ai_competitors=data.get('ai_competitors', 2),
            random_seed=data.get('random_seed')
        )

        return scenario

    def _get_default_scenario_config(self) -> Dict:
        """Retourne la configuration par défaut du scénario."""
        return {
            "name": "Scénario Standard",
            "description": "Configuration équilibrée pour apprentissage général",
            "difficulty": "normal",
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
                    "quality_sensitivity": 0.7,
                    "description": "Étudiants avec budget limité"
                },
                "familles": {
                    "size": 180,
                    "budget": 17.0,
                    "price_sensitivity": 1.2,
                    "quality_sensitivity": 1.1,
                    "description": "Familles recherchant bon rapport qualité/prix"
                },
                "foodies": {
                    "size": 90,
                    "budget": 25.0,
                    "price_sensitivity": 0.6,
                    "quality_sensitivity": 1.8,
                    "description": "Amateurs de gastronomie privilégiant la qualité"
                }
            },
            "restaurant": {
                "initial_budget": 10000,
                "base_capacity": 150,
                "base_staff_cost": 2800,
                "base_overhead": 1200
            },
            "competitors": [
                {
                    "name": "Resto Rapide",
                    "strategy": "prix_bas",
                    "base_price": 9.50,
                    "quality_level": 1
                },
                {
                    "name": "Bistrot Central",
                    "strategy": "equilibre",
                    "base_price": 13.20,
                    "quality_level": 3
                },
                {
                    "name": "Table Gourmande",
                    "strategy": "premium",
                    "base_price": 18.80,
                    "quality_level": 4
                }
            ],
            "game": {
                "max_turns": 10,
                "starting_month": 1,
                "enable_seasonality": True,
                "enable_events": True,
                "enable_marketing": True,
                "enable_advanced_finance": True
            },
            "objectives": {
                "primary": "Réaliser un profit total de 5000€",
                "secondary": [
                    "Maintenir une satisfaction client > 3.5",
                    "Atteindre 25% de part de marché",
                    "Survivre aux 10 tours"
                ]
            }
        }

    def get_default_scenario_path(self) -> Path:
        """
        Retourne le chemin vers le scénario par défaut.

        Returns:
            Chemin vers base.yaml
        """
        return Path(__file__).parent.parent.parent.parent / "examples" / "scenarios" / "base.yaml"

    def load_all_data(self, scenario_path: Optional[Path] = None) -> Dict:
        """
        Charge toutes les données nécessaires au jeu.

        Args:
            scenario_path: Chemin vers le scénario (optionnel)

        Returns:
            Dict avec toutes les données chargées
        """
        if scenario_path is None:
            scenario_path = self.get_default_scenario_path()

        suppliers = self.load_suppliers()
        supplier_prices = self.load_supplier_prices()
        suppliers_catalog = self.build_suppliers_catalog(suppliers, supplier_prices)
        return {
            'ingredients': self.load_ingredients(),
            'recipes': self.load_recipes(),
            'suppliers': suppliers,
            'suppliers_catalog': suppliers_catalog,
            'ingredient_gammes': self.load_ingredient_gammes(),
            'hr_tables': self.load_hr_tables(),
            'scenario': self.load_scenario(scenario_path)
        }
