from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from game_engine.domain.menu.ingredients_VO import FoodGrade


# Classement “qualité perçue” des gammes (plus haut = meilleur).
# Ajustable si besoin.
_GRADE_RANK: Dict[FoodGrade, int] = {
    FoodGrade.G5_CUIT_SOUS_VIDE: 5,
    FoodGrade.G1_FRAIS_BRUT: 3,
    FoodGrade.G3_SURGELE: 2,
    FoodGrade.G2_CONSERVE: 1,
}


@dataclass
class IngredientStockLot:
    """
    Lot d'ingrédient en stock.
    - perish_tour : dernier tour où le lot est consommable (exclu après cleanup).
    """

    name: str
    grade: FoodGrade
    qty_kg: float
    unit_cost: float
    received_tour: int
    perish_tour: int

    def is_expired(self, current_tour: int) -> bool:
        return current_tour > self.perish_tour


@dataclass
class FinishedBatch:
    """
    Lot de produits finis prêts à vendre.
    - expires_tour : dernier tour où la vente est possible (périme au tour suivant la prod par défaut).
    """

    recipe_name: str
    selling_price: float
    portions: int
    produced_tour: int
    expires_tour: int

    def is_expired(self, current_tour: int) -> bool:
        return current_tour > self.expires_tour


# -------------------- Inventory principal --------------------


@dataclass
class Inventory:
    """
    Stock du restaurant :
      - ingredient_lots_by_name[name] -> liste de lots d'ingrédients (multi-gammes)
      - finished_product_batches  -> liste de lots de produits finis (FIFO de vente)
    """

    ingredient_lots_by_name: Dict[str, List[IngredientStockLot]] = field(
        default_factory=dict
    )
    finished_product_batches: List[FinishedBatch] = field(default_factory=list)

    # -------- Ingrédients (achats / disponibilité / consommation) --------

    def add_ingredient(
        self,
        name: str,
        grade: FoodGrade,
        qty_kg: float,
        unit_cost: float,
        current_tour: int,
        shelf_tours: int = 1,
    ) -> None:
        """
        Ajoute un lot d'ingrédient. La péremption est exprimée en nombre de tours.
        Par ex. shelf_tours=1 => consommable sur le tour courant seulement.
        """
        new_lot = IngredientStockLot(
            name=name,
            grade=grade,
            qty_kg=float(qty_kg),
            unit_cost=float(unit_cost),
            received_tour=current_tour,
            perish_tour=current_tour + int(max(0, shelf_tours)),
        )
        self.ingredient_lots_by_name.setdefault(name, []).append(new_lot)

    def get_available_qty(self, name: str, current_tour: Optional[int] = None) -> float:
        """
        Quantité totale dispo (kg) non périmée pour un ingrédient.
        """
        ingredient_lots = self.ingredient_lots_by_name[name]
        total_available_qty = 0.0
        for lot in ingredient_lots:
            if current_tour is not None and lot.is_expired(current_tour):
                continue
            total_available_qty += max(0.0, lot.qty_kg)
        return round(total_available_qty, 6)

    def has_ingredient(
        self, name: str, qty_needed_kg: float, current_tour: Optional[int] = None
    ) -> bool:
        """
        True si la somme des lots non périmés couvre qty_needed_kg.
        """
        return self.get_available_qty(name, current_tour) >= float(qty_needed_kg)

    def _iter_lots_best_quality_fifo(
        self, name: str, current_tour: Optional[int]
    ) -> List[IngredientStockLot]:
        """
        Retourne les lots ordonnés par :
          1) meilleure gamme d'abord (rank décroissant)
          2) ancienneté (FIFO dans une même gamme)
        Les lots périmés sont exclus.
        """
        non_expired_lots = [
            lot
            for lot in self.ingredient_lots_by_name.get(name, [])
            if not (current_tour and lot.is_expired(current_tour))
        ]
        # Tri : meilleure gamme d'abord (-rank), puis received_tour croissant (ancien d'abord)
        non_expired_lots.sort(
            key=lambda lot: (-_GRADE_RANK[lot.grade], lot.received_tour)
        )
        return non_expired_lots

    def consume_ingredient(
        self,
        name: str,
        qty_needed_kg: float,
        current_tour: Optional[int] = None,
    ) -> Tuple[float, float]:
        """
        Consomme jusqu'à qty_needed_kg en priorisant la meilleure gamme puis FIFO.
        Retourne (qty_retirée, coût_total_consumé). Si la quantité dispo est insuffisante,
        consommera le maximum possible (et retournera une quantité < qty_needed_kg).

        NOTE : on ne mixe pas de logique de coût "cible" ici ; on valorise au coût unitaire du lot.
        """
        remaining_need_kg = float(qty_needed_kg)
        total_consumed_qty = 0.0
        total_consumed_cost = 0.0

        if remaining_need_kg <= 0:
            return (0.0, 0.0)

        sorted_lots = self._iter_lots_best_quality_fifo(name, current_tour)
        lot_index = 0
        while lot_index < len(sorted_lots) and remaining_need_kg > 0:
            current_lot = sorted_lots[lot_index]
            qty_to_take = min(current_lot.qty_kg, remaining_need_kg)
            if qty_to_take > 0:
                current_lot.qty_kg -= qty_to_take
                total_consumed_qty += qty_to_take
                total_consumed_cost += qty_to_take * current_lot.unit_cost
                remaining_need_kg -= qty_to_take

            if current_lot.qty_kg <= 1e-9:
                # supprimer le lot vide du "vrai" tableau
                original_lots = self.ingredient_lots_by_name.get(name, [])
                try:
                    original_lot_index = original_lots.index(current_lot)
                    original_lots.pop(original_lot_index)
                except ValueError:
                    pass
                sorted_lots.pop(lot_index)
            else:
                lot_index += 1

        return (round(total_consumed_qty, 6), round(total_consumed_cost, 2))

    # -------- Produits finis (production / vente / nettoyage) --------

    def add_finished_lot(
        self,
        recipe_name: str,
        selling_price: float,
        portions: int,
        produced_tour: int,
        shelf_tours: int = 1,
    ) -> None:
        """
        Ajoute un lot de produits finis. Par défaut, périme au tour suivant (shelf_tours=1).
        """
        new_batch = FinishedBatch(
            recipe_name=recipe_name,
            selling_price=float(selling_price),
            portions=int(portions),
            produced_tour=produced_tour,
            expires_tour=produced_tour + int(max(0, shelf_tours)),
        )
        self.finished_product_batches.append(new_batch)

    def total_finished_portions(
        self,
        recipe_name: Optional[str] = None,
        current_tour: Optional[int] = None,
    ) -> int:
        """
        Nombre total de portions prêtes à vendre (non périmées). Si recipe_name est fourni, filtre.
        """
        total_portions = 0
        for batch in self.finished_product_batches:
            if current_tour is not None and batch.is_expired(current_tour):
                continue
            if recipe_name is not None and batch.recipe_name != recipe_name:
                continue
            total_portions += max(0, int(batch.portions))
        return total_portions

    def sell_from_finished_fifo(self, qty_portions: int) -> Tuple[int, float]:
        """
        Vend jusqu'à qty_portions (peu importe la recette), FIFO strict.
        Retourne (portions_vendues, chiffre_affaires).
        NB : certaines UIs préféreront choisir une recette précise — cette
        méthode globale est utile quand on "sert" des clients sans granularité.
        """
        remaining_portions_to_sell = int(qty_portions)
        total_sold_portions = 0
        total_revenue = 0.0
        batch_index = 0
        while (
            batch_index < len(self.finished_product_batches)
            and remaining_portions_to_sell > 0
        ):
            current_batch = self.finished_product_batches[batch_index]
            if current_batch.portions <= 0:
                self.finished_product_batches.pop(batch_index)
                continue
            portions_to_take = min(current_batch.portions, remaining_portions_to_sell)
            if portions_to_take > 0:
                total_sold_portions += portions_to_take
                total_revenue += portions_to_take * current_batch.selling_price
                current_batch.portions -= portions_to_take
                remaining_portions_to_sell -= portions_to_take

            if current_batch.portions <= 0:
                self.finished_product_batches.pop(batch_index)
            else:
                batch_index += 1
        return (total_sold_portions, round(total_revenue, 2))

    # -------- Nettoyage (péremption) --------

    def cleanup_expired(self, current_tour: int) -> None:
        """
        Supprime tous les lots périmés (ingrédients & produits finis).
        À appeler au début de chaque tour.
        """
        # Ingrédients
        for ingredient_name, ingredient_lots in list(
            self.ingredient_lots_by_name.items()
        ):
            non_expired_lots: List[IngredientStockLot] = []
            for lot in ingredient_lots:
                if lot.is_expired(current_tour):
                    continue
                # on garde uniquement les quantités positives
                if lot.qty_kg > 1e-9:
                    non_expired_lots.append(lot)
            if non_expired_lots:
                self.ingredient_lots_by_name[ingredient_name] = non_expired_lots
            else:
                self.ingredient_lots_by_name.pop(ingredient_name, None)

        # Produits finis
        self.finished_product_batches = [
            batch
            for batch in self.finished_product_batches
            if not batch.is_expired(current_tour)
        ]

    # -------- Aides diverses --------

    def available_grades(
        self, name: str, current_tour: Optional[int] = None
    ) -> List[FoodGrade]:
        """
        Liste des gammes disponibles (non périmées) pour un ingrédient donné,
        triées de la meilleure à la moins bonne.
        """
        sorted_lots = self._iter_lots_best_quality_fifo(name, current_tour)
        available_grade_list = []
        seen_grades = set()
        for lot in sorted_lots:
            if lot.grade not in seen_grades:
                seen_grades.add(lot.grade)
                available_grade_list.append(lot.grade)
        return available_grade_list

    def snapshot(
        self, current_tour: Optional[int] = None
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Vue simple du stock : {ingredient: [(grade, qty_kg), ...]} (non périmé uniquement si current_tour fourni)

        Étapes du processus:
        1. Parcourt tous les ingrédients dans self.ingredient_lots_by_name
        2. Pour chaque ingrédient, examine tous ses lots
        3. Filtre les lots périmés si current_tour est fourni
        4. Extrait le nom de la gamme et la quantité de chaque lot valide
        5. Trie les résultats par qualité de gamme (meilleure d'abord)
        6. Retourne un dictionnaire organisé

        Exemple:
        Si self.ingredient_lots_by_name = {
            "tomate": [
                IngredientStockLot(name="tomate", grade=FoodGrade.G1_FRAIS_BRUT, qty_kg=2.5, ...),
                IngredientStockLot(name="tomate", grade=FoodGrade.G2_CONSERVE, qty_kg=1.0, ...)
            ],
            "oignon": [
                IngredientStockLot(name="oignon", grade=FoodGrade.G3_SURGELE, qty_kg=0.8, ...)
            ]
        }

        Retourne:
        {
            "tomate": [("G1_FRAIS_BRUT", 2.5), ("G2_CONSERVE", 1.0)],  # trié par qualité
            "oignon": [("G3_SURGELE", 0.8)]
        }
        """
        inventory_snapshot: Dict[str, List[Tuple[str, float]]] = {}

        # Étape 1: Parcourir tous les ingrédients
        for ingredient_name, ingredient_lots in self.ingredient_lots_by_name.items():
            grade_quantity_pairs: List[Tuple[str, float]] = []

            # Étape 2: Examiner chaque lot de l'ingrédient
            for lot in ingredient_lots:
                # Étape 3: Filtrer les lots périmés si nécessaire
                if current_tour is not None and lot.is_expired(current_tour):
                    continue

                # Étape 4: Extraire nom de gamme et quantité
                grade_name = getattr(lot.grade, "name", str(lot.grade))
                lot_quantity = round(lot.qty_kg, 3)
                grade_quantity_pairs.append((grade_name, lot_quantity))

            # Étape 5: Trier par qualité de gamme (meilleure d'abord)
            grade_quantity_pairs.sort(
                key=lambda grade_qty_pair: -_GRADE_RANK.get(
                    getattr(FoodGrade, grade_qty_pair[0], grade_qty_pair[0])
                    if isinstance(grade_qty_pair[0], str)
                    else grade_qty_pair[0],
                    0,  # valeur par défaut si gamme inconnue
                )
            )

            # Étape 6: Ajouter au résultat final si des lots valides existent
            if grade_quantity_pairs:
                inventory_snapshot[ingredient_name] = grade_quantity_pairs

        return inventory_snapshot
