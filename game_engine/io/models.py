"""
Pydantic models for DataLoader return types in FoodOps Pro.
"""

from decimal import Decimal

from pydantic import BaseModel, Field

from game_engine.domain.ingredient import Ingredient
from game_engine.domain.recipe import Recipe
from game_engine.domain.scenario import Scenario
from game_engine.domain.supplier import Supplier


class SupplierPriceEntry(BaseModel):
    """
    Represents a supplier price entry for a specific ingredient.

    Used in supplier catalogs and pricing data.
    """

    supplier_id: str = Field(description="ID of the supplier")
    quality_level: int | None = Field(None, description="Quality level (1-5)")
    pack_size: Decimal = Field(description="Package size")
    pack_unit: str | None = Field(None, description="Package unit")
    unit_price_ht: Decimal = Field(description="Unit price excluding VAT")
    vat_rate: Decimal = Field(description="VAT rate")
    moq_qty: Decimal = Field(Decimal("0"), description="Minimum order quantity")
    moq_value: Decimal = Field(Decimal("0"), description="Minimum order value")
    lead_time_days: int | None = Field(None, description="Lead time in days")
    reliability: Decimal | None = Field(None, description="Supplier reliability (0-1)")
    available: int = Field(
        1, description="Availability status (1=available, 0=unavailable)"
    )


class IngredientGamme(BaseModel):
    """
    Represents quality level variations for an ingredient.

    Used to define different quality tiers with price and quality modifiers.
    """

    quality_level: int = Field(description="Quality level (1-5)")
    price_multiplier: Decimal = Field(
        description="Price multiplier for this quality level"
    )
    shelf_life_factor: Decimal = Field(
        description="Shelf life factor for this quality level"
    )
    quality_score: Decimal = Field(description="Quality score for this level")


class HRSocialCharges(BaseModel):
    """Social charges rates by contract type."""

    cdi: Decimal = Field(description="CDI contract social charges rate")
    cdd: Decimal = Field(description="CDD contract social charges rate")
    extra: Decimal = Field(description="Extra hours social charges rate")
    apprenti: Decimal = Field(description="Apprentice social charges rate")
    stage: Decimal = Field(description="Internship social charges rate")


class HRTables(BaseModel):
    """
    Represents HR tables configuration.

    Contains social charges rates and other HR-related parameters.
    """

    social_charges: HRSocialCharges = Field(
        description="Social charges rates by contract type"
    )


class SuppliersCatalogEntry(BaseModel):
    """
    Represents an enhanced catalog entry with supplier information.

    Extends SupplierPriceEntry with additional supplier metadata.
    """

    supplier_id: str = Field(description="ID of the supplier")
    quality_level: int | None = Field(None, description="Quality level (1-5)")
    pack_size: Decimal = Field(description="Package size")
    pack_unit: str | None = Field(None, description="Package unit")
    unit_price_ht: Decimal = Field(description="Unit price excluding VAT")
    vat_rate: Decimal = Field(description="VAT rate")
    moq_qty: Decimal = Field(Decimal("0"), description="Minimum order quantity")
    moq_value: Decimal = Field(Decimal("0"), description="Minimum order value")
    lead_time_days: int = Field(description="Lead time in days from supplier")
    reliability: Decimal = Field(description="Supplier reliability (0-1)")
    available: int = Field(
        1, description="Availability status (1=available, 0=unavailable)"
    )


class LoadAllDataResponse(BaseModel):
    """
    Represents the complete data structure returned by load_all_data.

    Contains all game data needed for a complete game session.
    """

    ingredients: dict[str, Ingredient] = Field(description="All ingredients by ID")
    recipes: dict[str, Recipe] = Field(description="All recipes by ID")
    suppliers: dict[str, Supplier] = Field(description="All suppliers by ID")
    suppliers_catalog: dict[str, list[SuppliersCatalogEntry]] = Field(
        description="Enhanced supplier catalog by ingredient ID"
    )
    ingredient_gammes: dict[str, list[IngredientGamme]] = Field(
        description="Quality level variations by ingredient ID"
    )
    hr_tables: HRTables = Field(description="HR configuration tables")
    scenario: Scenario = Field(description="Game scenario configuration")


# Type aliases for DataLoader return types
IngredientsDict = dict[str, Ingredient]
RecipesDict = dict[str, Recipe]
SuppliersDict = dict[str, Supplier]
SupplierPricesDict = dict[str, list[SupplierPriceEntry]]
IngredientGammesDict = dict[str, list[IngredientGamme]]
SuppliersCatalogDict = dict[str, list[SuppliersCatalogEntry]]
