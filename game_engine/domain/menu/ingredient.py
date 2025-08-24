"""
Modèle des ingrédients et système de qualité des ingrédients
"""

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class Ingredient(BaseModel):
    """
    Représente un ingrédient utilisé dans les recettes.

    Attributes:
        id: Identifiant unique de l'ingrédient
        name: Nom de l'ingrédient
        unit: Unité de mesure (kg, L, pièce, etc.)
        cost_ht: Coût d'achat hors taxes par unité
        vat_rate: Taux de TVA à l'achat (ex: 0.055 pour 5.5%)
        density: Densité pour conversions d'unités (optionnel)
        shelf_life_days: Durée de conservation en jours
        category: Catégorie (viande, légume, épice, etc.)
    """

    id: str
    name: str
    unit: str
    cost_ht: Decimal
    vat_rate: Decimal
    shelf_life_days: int
    category: str
    density: Decimal | None = None

    @property
    def cost_ttc(self) -> Decimal:
        """Coût TTC par unité."""
        return self.cost_ht * (1 + self.vat_rate)

    def convert_quantity(
        self, quantity: Decimal, from_unit: str, to_unit: str
    ) -> Decimal:
        """
        Convertit une quantité d'une unité vers une autre.

        Args:
            quantity: Quantité à convertir
            from_unit: Unité source
            to_unit: Unité cible

        Returns:
            Quantité convertie

        Raises:
            ValueError: Si la conversion n'est pas possible
        """
        if from_unit == to_unit:
            return quantity

        # Conversions simples supportées
        conversions = {
            ("kg", "g"): Decimal("1000"),
            ("g", "kg"): Decimal("0.001"),
            ("L", "mL"): Decimal("1000"),
            ("mL", "L"): Decimal("0.001"),
        }

        factor = conversions.get((from_unit, to_unit))
        if factor is not None:
            return quantity * factor

        # Conversion avec densité si disponible
        if self.density is not None:
            if from_unit == "L" and to_unit == "kg":
                return quantity * self.density
            elif from_unit == "kg" and to_unit == "L":
                return quantity / self.density

        raise ValueError(
            f"Conversion impossible de {from_unit} vers {to_unit} pour {self.name}"
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.cost_ht:.2f}€ HT/{self.unit})"


class QualityLevel(Enum):
    """Niveaux de qualité des ingrédients."""

    ECONOMIQUE = 1  # ⭐ Surgelé industriel, conserves
    STANDARD = 2  # ⭐⭐ Frais classique, sous-vide
    SUPERIEUR = 3  # ⭐⭐⭐ Frais premium, origine contrôlée
    PREMIUM = 4  # ⭐⭐⭐⭐ Bio, Label Rouge, AOP
    LUXE = 5  # ⭐⭐⭐⭐⭐ Artisanal, terroir, exception


class IngredientRange(Enum):
    """Gammes d'ingrédients."""

    SURGELE = "surgelé"
    CONSERVE = "conserve"
    SOUS_VIDE = "sous_vide"
    FRAIS_IMPORT = "frais_import"
    FRAIS_LOCAL = "frais_local"
    BIO = "bio"
    LABEL_ROUGE = "label_rouge"
    AOP = "aop"
    ARTISANAL = "artisanal"
    TERROIR = "terroir"


class QualityModifiers(BaseModel):
    """Modificateurs liés à la qualité d'un ingrédient."""

    cost_multiplier: Decimal  # Multiplicateur de coût (ex: 1.25 = +25%)
    satisfaction_bonus: Decimal  # Bonus satisfaction client (ex: 0.15 = +15%)
    prep_time_multiplier: Decimal  # Multiplicateur temps préparation
    shelf_life_multiplier: Decimal  # Multiplicateur DLC
    availability_seasonal: bool = False  # Disponibilité saisonnière

    def __post_init__(self):
        """
        Valide la cohérence des modificateurs de qualité.
        
        Raises:
            ValueError: Si un modificateur est négatif ou nul
        """
        if self.cost_multiplier <= 0:
            raise ValueError(
                f"Le multiplicateur de coût doit être positif: {self.cost_multiplier}"
            )
        if self.prep_time_multiplier <= 0:
            raise ValueError(
                f"Le multiplicateur de temps doit être positif: {self.prep_time_multiplier}"
            )
        if self.shelf_life_multiplier <= 0:
            raise ValueError(
                f"Le multiplicateur de DLC doit être positif: {self.shelf_life_multiplier}"
            )


class IngredientVariant(BaseModel):
    """
    Variante d'un ingrédient avec qualité et gamme spécifiques.

    Attributes:
        base_ingredient_id: ID de l'ingrédient de base
        quality_level: Niveau de qualité (1-5 étoiles)
        range_type: Type de gamme (surgelé, bio, etc.)
        supplier_id: Fournisseur spécialisé
        modifiers: Modificateurs de qualité
        description: Description de la variante
        certifications: Certifications (bio, label rouge, etc.)
    """

    base_ingredient_id: str
    quality_level: QualityLevel
    range_type: IngredientRange
    supplier_id: str
    modifiers: QualityModifiers
    description: str = ""
    certifications: list[str] = []

    @property
    def id(self) -> str:
        """ID unique de la variante."""
        return f"{self.base_ingredient_id}_{self.range_type.value}_{self.quality_level.value}"

    @property
    def display_name(self) -> str:
        """Nom d'affichage avec qualité."""
        stars = "⭐" * self.quality_level.value
        return f"{self.description} {stars}"

    @property
    def quality_description(self) -> str:
        """Description de la qualité."""
        descriptions = {
            QualityLevel.ECONOMIQUE: "Économique - Rapport qualité/prix",
            QualityLevel.STANDARD: "Standard - Qualité classique",
            QualityLevel.SUPERIEUR: "Supérieur - Qualité premium",
            QualityLevel.PREMIUM: "Premium - Haute qualité certifiée",
            QualityLevel.LUXE: "Luxe - Excellence artisanale",
        }
        return descriptions[self.quality_level]

    def calculate_final_cost(self, base_cost: Decimal) -> Decimal:
        """
        Calcule le coût final d'achat en appliquant le multiplicateur de qualité.
        
        Args:
            base_cost: Coût de base de l'ingrédient
            
        Returns:
            Coût final avec ajustement qualité
            
        Example:
            Si base_cost = 10€ et cost_multiplier = 1.5 (premium)
            Retourne 15€
        """
        return base_cost * self.modifiers.cost_multiplier

    def calculate_prep_time(self, base_time: int) -> int:
        """
        Calcule le temps de préparation ajusté selon la qualité.
        
        Les ingrédients de haute qualité peuvent nécessiter plus de temps
        de préparation (découpe plus précise, etc.) tandis que les
        ingrédients pré-préparés peuvent réduire le temps.
        
        Args:
            base_time: Temps de préparation de base en minutes
            
        Returns:
            Temps de préparation ajusté en minutes
        """
        return int(base_time * self.modifiers.prep_time_multiplier)

    def calculate_shelf_life(self, base_shelf_life: int) -> int:
        """
        Calcule la durée de conservation ajustée selon la qualité.
        
        Les ingrédients surgelés ont une DLC plus longue,
        tandis que les produits ultra-frais se conservent moins longtemps.
        
        Args:
            base_shelf_life: Durée de conservation de base en jours
            
        Returns:
            Durée de conservation ajustée en jours
        """
        return int(base_shelf_life * self.modifiers.shelf_life_multiplier)


# Définitions des modificateurs par niveau de qualité
QUALITY_MODIFIERS = {
    QualityLevel.ECONOMIQUE: QualityModifiers(
        cost_multiplier=Decimal("0.70"),  # -30%
        satisfaction_bonus=Decimal("-0.20"),  # -20%
        prep_time_multiplier=Decimal("0.85"),  # -15% (pré-coupé)
        shelf_life_multiplier=Decimal("2.0"),  # +100% (surgelé)
    ),
    QualityLevel.STANDARD: QualityModifiers(
        cost_multiplier=Decimal("1.00"),  # Prix de référence
        satisfaction_bonus=Decimal("0.00"),  # Neutre
        prep_time_multiplier=Decimal("1.00"),  # Standard
        shelf_life_multiplier=Decimal("1.0"),  # Standard
    ),
    QualityLevel.SUPERIEUR: QualityModifiers(
        cost_multiplier=Decimal("1.25"),  # +25%
        satisfaction_bonus=Decimal("0.15"),  # +15%
        prep_time_multiplier=Decimal("1.10"),  # +10%
        shelf_life_multiplier=Decimal("0.9"),  # -10% (plus frais)
    ),
    QualityLevel.PREMIUM: QualityModifiers(
        cost_multiplier=Decimal("1.50"),  # +50%
        satisfaction_bonus=Decimal("0.30"),  # +30%
        prep_time_multiplier=Decimal("1.20"),  # +20%
        shelf_life_multiplier=Decimal("0.8"),  # -20% (très frais)
    ),
    QualityLevel.LUXE: QualityModifiers(
        cost_multiplier=Decimal("2.00"),  # +100%
        satisfaction_bonus=Decimal("0.50"),  # +50%
        prep_time_multiplier=Decimal("1.30"),  # +30%
        shelf_life_multiplier=Decimal("0.7"),  # -30% (ultra frais)
    ),
}


class IngredientQualityManager:
    """
    Gestionnaire central du système de qualité des ingrédients.
    
    Cette classe gère toutes les variantes d'ingrédients disponibles
    avec leurs différents niveaux de qualité, gammes et fournisseurs.
    Elle permet l'optimisation des coûts et de la qualité des recettes.
    
    Attributes:
        variants: Dictionnaire de toutes les variantes indexées par ID
    
    Note:
        Le gestionnaire est initialisé avec des variantes par défaut
        pour démontrer le système de qualité.
    """

    def __init__(self):
        # Stockage de toutes les variantes d'ingrédients disponibles
        self.variants: dict[str, IngredientVariant] = {}
        # Chargement des exemples de variantes pour initialisation
        self._load_default_variants()

    def _load_default_variants(self):
        """
        Charge des exemples de variantes d'ingrédients pour initialiser le système.
        Crée des variantes avec différents niveaux de qualité et gammes pour 
        démontrer les possibilités du système de qualité.
        
        Cette méthode est appelée automatiquement lors de l'initialisation 
        pour fournir des données de base.
        """
        # Exemples de variantes pour le steak haché
        self.add_variant(
            IngredientVariant(
                base_ingredient_id="beef_ground",
                quality_level=QualityLevel.ECONOMIQUE,
                range_type=IngredientRange.SURGELE,
                supplier_id="davigel",
                modifiers=QUALITY_MODIFIERS[QualityLevel.ECONOMIQUE],
                description="Steak haché surgelé",
                certifications=[],
            )
        )

        self.add_variant(
            IngredientVariant(
                base_ingredient_id="beef_ground",
                quality_level=QualityLevel.STANDARD,
                range_type=IngredientRange.FRAIS_IMPORT,
                supplier_id="metro_pro",
                modifiers=QUALITY_MODIFIERS[QualityLevel.STANDARD],
                description="Steak haché frais",
                certifications=[],
            )
        )

        self.add_variant(
            IngredientVariant(
                base_ingredient_id="beef_ground",
                quality_level=QualityLevel.PREMIUM,
                range_type=IngredientRange.BIO,
                supplier_id="bio_france",
                modifiers=QUALITY_MODIFIERS[QualityLevel.PREMIUM],
                description="Steak haché bio",
                certifications=["AB", "Origine France"],
            )
        )

        # Exemples pour les tomates
        self.add_variant(
            IngredientVariant(
                base_ingredient_id="tomato",
                quality_level=QualityLevel.ECONOMIQUE,
                range_type=IngredientRange.CONSERVE,
                supplier_id="metro_pro",
                modifiers=QUALITY_MODIFIERS[QualityLevel.ECONOMIQUE],
                description="Tomates en conserve",
                certifications=[],
            )
        )

        self.add_variant(
            IngredientVariant(
                base_ingredient_id="tomato",
                quality_level=QualityLevel.LUXE,
                range_type=IngredientRange.TERROIR,
                supplier_id="local_farm",
                modifiers=QUALITY_MODIFIERS[QualityLevel.LUXE],
                description="Tomates du terroir",
                certifications=["Producteur local", "Variété ancienne"],
            )
        )

    def add_variant(self, variant: IngredientVariant):
        """
        Enregistre une nouvelle variante d'ingrédient dans le gestionnaire.
        
        Args:
            variant: La variante d'ingrédient à ajouter
            
        Note:
            La variante sera indexée par son ID unique généré automatiquement
        """
        self.variants[variant.id] = variant

    def get_variants_for_ingredient(
        self, base_ingredient_id: str
    ) -> list[IngredientVariant]:
        """
        Récupère toutes les variantes disponibles pour un ingrédient donné.
        
        Args:
            base_ingredient_id: L'identifiant de l'ingrédient de base
            
        Returns:
            Liste des variantes de cet ingrédient (peut être vide)
            
        Example:
            >>> manager = IngredientQualityManager()
            >>> variants = manager.get_variants_for_ingredient("beef_ground")
            >>> print(len(variants))  # 3 (économique, standard, premium)
        """
        return [
            v
            for v in self.variants.values()
            if v.base_ingredient_id == base_ingredient_id
        ]

    def get_variants_by_supplier(self, supplier_id: str) -> list[IngredientVariant]:
        """
        Récupère toutes les variantes d'ingrédients proposées par un fournisseur.
        
        Args:
            supplier_id: L'identifiant du fournisseur
            
        Returns:
            Liste des variantes disponibles chez ce fournisseur
            
        Note:
            Utile pour analyser l'offre d'un fournisseur ou pour 
            optimiser les commandes par fournisseur
        """
        return [v for v in self.variants.values() if v.supplier_id == supplier_id]

    def get_variants_by_quality(
        self, quality_level: QualityLevel
    ) -> list[IngredientVariant]:
        """
        Récupère toutes les variantes correspondant à un niveau de qualité donné.
        
        Args:
            quality_level: Le niveau de qualité recherché (ECONOMIQUE à LUXE)
            
        Returns:
            Liste des variantes de ce niveau de qualité
            
        Note:
            Permet de filtrer l'offre selon le positionnement du restaurant
        """
        return [v for v in self.variants.values() if v.quality_level == quality_level]

    def calculate_recipe_quality_score(
        self, ingredient_variants: dict[str, IngredientVariant]
    ) -> Decimal:
        """
        Calcule le score de qualité moyen d'une recette basé sur ses ingrédients.
        
        Le score est calculé comme la moyenne arithmétique des niveaux de qualité 
        de tous les ingrédients utilisés dans la recette.
        
        Args:
            ingredient_variants: Dictionnaire mapping ingredient_id vers sa variante
            
        Returns:
            Score de qualité moyen sur une échelle de 1.0 (économique) à 5.0 (luxe)
            Retourne 2.0 (standard) si aucun ingrédient n'est fourni
            
        Example:
            >>> variants = {
            ...     "beef": variant_premium,  # niveau 4
            ...     "tomato": variant_standard  # niveau 2
            ... }
            >>> score = manager.calculate_recipe_quality_score(variants)
            >>> print(score)  # 3.0 ((4+2)/2)
        """
        if not ingredient_variants:
            return Decimal("2.0")  # Standard par défaut

        total_score = Decimal("0")
        for variant in ingredient_variants.values():
            total_score += Decimal(str(variant.quality_level.value))

        return total_score / Decimal(str(len(ingredient_variants)))

    def get_quality_impact_on_attractiveness(self, quality_score: Decimal) -> Decimal:
        """
        Convertit un score de qualité en multiplicateur d'attractivité client.
        
        Plus la qualité est élevée, plus l'attractivité du plat augmente.
        Cette fonction traduit la qualité perçue en impact commercial.
        
        Args:
            quality_score: Score de qualité calculé (1.0 à 5.0)
            
        Returns:
            Multiplicateur d'attractivité:
            - <= 1.5: 0.80 (-20% d'attractivité)
            - <= 2.5: 1.00 (attractivité neutre)
            - <= 3.5: 1.15 (+15% d'attractivité)
            - <= 4.5: 1.30 (+30% d'attractivité)
            - > 4.5:  1.50 (+50% d'attractivité)
            
        Note:
            Ces multiplicateurs reflètent la perception client de la qualité
            et son impact sur la demande
        """
        if quality_score <= 1.5:
            return Decimal("0.80")  # -20%
        elif quality_score <= 2.5:
            return Decimal("1.00")  # Neutre
        elif quality_score <= 3.5:
            return Decimal("1.15")  # +15%
        elif quality_score <= 4.5:
            return Decimal("1.30")  # +30%
        else:
            return Decimal("1.50")  # +50%
